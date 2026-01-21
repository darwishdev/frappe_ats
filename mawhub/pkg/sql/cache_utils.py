import frappe
import json
from typing import Optional, cast

def get_ai_cache(task_id: str, provider: str) -> Optional[str]:
    # We cast to Optional[str] because we know 'result_json' is stored as a string/text in MariaDB
    value = frappe.db.get_value("AI Task Cache",
        {"task_id": task_id, "provider": provider},
        "result_json"
    )
    return cast(Optional[str], value)

def set_ai_cache(task_id: str, provider: str, result: dict) -> None:
    doc = frappe.get_doc({
        "doctype": "AI Task Cache",
        "task_id": task_id,
        "provider": provider,
        "result_json": json.dumps(result)
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
