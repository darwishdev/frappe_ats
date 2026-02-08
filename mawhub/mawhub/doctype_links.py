import frappe

def get_doctype_links():
    return {
        "Job Opening": {
            "views": ["List", "Report", "Dashboard", "Kanban", "Cards"]
        }
    }
