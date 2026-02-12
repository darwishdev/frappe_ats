import os
from click import Path
import frappe
from pathlib import Path
from mawhub.pkg.customfields.custom_fields_utils import install_custom_fields
from mawhub.pkg.overrides.module_overrides_utils import update_doctypes_module
from mawhub.pkg.seeder.role_utils import seed_app_roles
from mawhub.pkg.sql.sql_utils import run_sql_dir
SQL_DIR = Path(frappe.get_app_path("mawhub", "pkg", "sql" , "schema"))
CUSTOMFIELDS_PATH = os.path.join(frappe.get_app_path("mawhub"),  "pkg", "customfields" ,
                                 "fields")
ROLES_CONFIG = {
    "Recruiter": {
        "desk_access": True,
        "perms": {
            "Job Opening": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Job Applicant": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Interview": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Applicant Resume": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Parsed Document": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Customer": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Project": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Task": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Job Pipeline": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Job Applicant": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
        },
    },
     "ATS Client Viewer": {
        "desk_access": True,
        "perms": {
            "Page": {"read": 1},
            "Workspace": {"read": 1},
            "Job Opening": {"read": 1},
            "Job Applicant": {"read": 1},
            "Interview": {"read": 1},
            "Comment": {"read": 1, "create": 1},
            "Communication": {"read": 1},

            # Project Management
            "Project": {"read": 1},
            "Task": {"read": 1},
        },
    },

    "ATS Client Reviewer": {
        "desk_access": True,
        "perms": {
            "Page": {"read": 1},
            "Workspace": {"read": 1},
            "Job Opening": {"read": 1},
            "Job Applicant": {"read": 1, "write": 1},
            "Interview": {"read": 1, "write": 1},
            "Comment": {"read": 1, "create": 1},
            "Communication": {"read": 1, "create": 1},

            # Project Management
            "Project": {"read": 1},
            "Task": {"read": 1, "write": 1},
        },
    },

    "ATS Client Collaborator": {
        "desk_access": True,
        "perms": {
            "Page": {"read": 1},
            "Workspace": {"read": 1},
            "Job Opening": {"read": 1},
            "Job Applicant": {"read": 1, "write": 1},
            "Interview": {"read": 1, "write": 1, "create": 1},
            "Comment": {"read": 1, "create": 1},
            "Communication": {"read": 1, "create": 1},

            # Project Management
            "Project": {"read": 1},
            "Task": {"read": 1, "write": 1},
        },
    },
}
def after_install():
    return {"ok" : True}
# Optional: run this on every migrate so changes apply during development
def after_migrate():
    doctypes_to_update = [
        # "Job Applicant",
        # "Customer",
        # "Job Opening",
        # "Project",
        # "Task"
    ]
    update_doctypes_module(doctypes_to_update, "Mawhub")
    install_custom_fields(CUSTOMFIELDS_PATH)
    run_sql_dir(SQL_DIR)
    seed_app_roles(ROLES_CONFIG, domain="mawhub.io")
    return {"ok" : True}

