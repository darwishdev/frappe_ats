from typing import Any, Dict, List, cast
import frappe
from frappe.desk.reportview import get as original_get


@frappe.whitelist()
def get():
    args = frappe.local.form_dict

    data = cast(Dict[str, Any], original_get())

    if args.get("doctype") != "Job Opening":
        return data


    keys = data["keys"]
    values = data["values"]
    if not values:
        return data

    name_index = keys.index("name")
    job_names = tuple(row[name_index] for row in values)

    steps = cast(
            List[Dict[str , Any]],
            frappe.db.sql("""
                          SELECT
                          s.name,
                          s.parent,
                          s.step_code,
                          s.step_name,
                          COUNT(a.name) applicants_count
                          FROM `tabPipeline Step` s
                          LEFT JOIN `tabJob Opening Applicant` a
                          on s.name = a.step
                          AND a.invalidated_at IS NULL
                          WHERE s.parenttype = 'Job Opening'
                          AND s.parent IN %s
                          GROUP BY
                          s.name,
                          s.parent,
                          s.step_code,
                          s.step_name
                          ORDER BY s.parent , s.idx
                          """ , (job_names,) , as_dict=True ))
    if not isinstance(steps,list):
        return data
    steps_map: dict[str, list[dict[str, Any]]] = {}
    for s in steps:
        steps_map.setdefault(s["parent"], []).append({
            "name": s["name"],
            "code": s["step_code"],
            "title": s["step_name"],
            "applicants": s["applicants_count"]
        })
        keys.append("steps")
    return data
