import os
from typing import List, cast
from click import Path
import frappe
from pathlib import Path

from frappe.core.doctype.user.user import User
from frappe.model.document import Document
from mawhub.pkg.customfields.custom_fields_utils import install_custom_fields
from mawhub.pkg.overrides.module_overrides_utils import update_doctypes_module
from mawhub.pkg.seeder.role_utils import seed_app_roles
from mawhub.pkg.sql.sql_utils import run_sql_dir
SQL_DIR = Path(frappe.get_app_path("mawhub", "pkg", "sql" , "schema"))
CUSTOMFIELDS_PATH = os.path.join(frappe.get_app_path("mawhub"),  "pkg", "customfields" ,
                                 "fields")

INITIAL_USERS = [
    {"name": "Brone Ram", "email": "brone@mawhub.io"},
    {"name": "Ahmed Darwish", "email": "ahmed@mawhub.io"},
    {"name": "Amal Mussa", "email": "amalm@mawhub.io"},
    {"name": "Amal Yaghi", "email": "amal@mawhub.io"},
    {"name": "Angela Brown", "email": "angela@mawhub.io"},
    {"name": "Esraa Adel", "email": "esraa@mawhub.io"},
    {"name": "Frankie Cornelissen", "email": "frankie@mawhub.io"},
    {"name": "Micaela Jackson", "email": "micaela@mawhub.io"},
    {"name": "Mohamed Fahmi", "email": "marketing@mawhub.io"},
    {"name": "Reem Khaled", "email": "reem@mawhub.io"},
    {"name": "Sarah Taha", "email": "sarah@mawhub.io"},
]

INITIAL_USERS_PASSWORD = "Mawhub@2026"
ROLES_CONFIG = {
    "Recruiter": {
        "desk_access": True,
        "perms": {
            "Designation": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Comment": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Job Opening": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Job Applicant": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Parsed Document": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Interview": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Interview Feedback": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
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
            "Comment": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Designation": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
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
            "Designation": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Comment": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
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
            "Designation": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
            "Comment": {"read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "amend": 1},
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

def update_client_secrets():
    print("calleldddd")
    client_secret = frappe.conf.get("OAUTH_CLIENT_SECRET")
    if not client_secret:
        frappe.log_error("OAUTH_CLIENT_SECRET not set in common_site_config.json")
        return

    def update_docs(docs_to_update: List[Document]):
        """Update client_secret on given docs"""
        for doc in docs_to_update:
            print("updating", doc, "with", client_secret)
            if hasattr(doc, "client_secret"):
                doc.set("client_secret", client_secret)
                doc.save(ignore_permissions=True)

    docs_to_update: List[Document] = []

    # Social Login Key (regular DocType)
    try:
        docs_to_update.append(frappe.get_doc("Social Login Key", "google"))
    except frappe.db.TableMissingError:
        frappe.logger().warning("Social Login Key table missing, skipping.")

    # Google Settings (Single DocType)
    try:
        docs_to_update.append(frappe.get_single("Google Settings"))
    except frappe.db.TableMissingError:
        frappe.logger().warning("Google Settings table missing, skipping.")

    # Call the small updater function
    update_docs(docs_to_update)

    frappe.db.commit()
    frappe.logger().info("OAuth client secrets updated from common_site_config.json")
def seed_initial_users(users: list[dict], password: str, role: str = "Recruiter"):
    for u in users:
        email = u["email"].strip().lower()
        full_name = u["name"].strip()

        if frappe.db.exists("User", email):
            continue

        parts = full_name.split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

        doc = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "enabled": 1,
            "send_welcome_email": 0,
        })

        doc.insert(ignore_permissions=True)
        doc = cast(User , doc)
        # set static password
        doc.new_password = password
        doc.save(ignore_permissions=True)

        # assign role
        doc.add_roles(role)

    frappe.db.commit()
def after_install():
    return {"ok" : True}
# Optional: run this on every migrate so changes apply during development
def after_migrate():
    print("calleldddd miggg")
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
    mawhub_company = frappe.get_doc("Company" , "Mawhub")
    if mawhub_company:
        mawhub_company.set("default_holiday_list" , "Saudi Arabia")
        mawhub_company.save()
        frappe.db.commit()

    seed_initial_users(
        INITIAL_USERS,
        password=INITIAL_USERS_PASSWORD,
        role="Recruiter"
    )
    update_client_secrets()
    return {"ok" : True}



