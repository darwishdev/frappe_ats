# mawhub/mawhub/pkg/helpers/update_module.py
import frappe
from typing import List

def update_doctypes_module(doctype_names: List[str], target_module: str):
    """
    Update the module of multiple DocTypes to the target_module.
    Safe to call multiple times (idempotent).
    """
    for dt_name in doctype_names:
        try:
            dt = frappe.get_doc("DocType", dt_name)
            if dt.get("module") != target_module:
                dt.set("module" , target_module)
                dt.save()
                frappe.db.commit()
                frappe.log(f"'{dt_name}' moved to module '{target_module}'")
            else:
                frappe.log(f"'{dt_name}' already in module '{target_module}'")
        except frappe.DoesNotExistError:
            frappe.log(f"DocType '{dt_name}' does not exist")
        except Exception as e:
            frappe.log_error(f"Failed to update module for '{dt_name}': {str(e)}")
