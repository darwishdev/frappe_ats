from typing import Any, Dict, List, cast
import frappe
from frappe.desk.reportview import get as original_get


@frappe.whitelist()
def get():
    args = frappe.local.form_dict

    data = cast(Dict[str, Any], original_get())

    if  args.get("doctype") != "Job Opening":
        return data


    keys = data["keys"]
    values = data["values"]
    if not values:
        return data

    name_index = keys.index("name")
    job_names = tuple(row[name_index] for row in values)
    steps = frappe.call(
        "mawhub.job_opening_step_list",
        job_names=",".join(job_names)
    )
    if not isinstance(steps,dict):
        return data
    for i, row in enumerate(values):
        job_name = row[0]
        steps_array = steps.get(job_name)
        row.append(steps_array)
        print(f"array is {steps_array} , job_name is {job_name} : index is : {i}")
    keys.append("steps")
    return data
