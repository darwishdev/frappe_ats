import os
from click import Path
import frappe
from pathlib import Path
from mawhub.pkg.customfields.custom_fields_utils import install_custom_fields
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
        },
    }
}
def after_install():
    return {"ok" : True}
# Optional: run this on every migrate so changes apply during development
def after_migrate():
    install_custom_fields(CUSTOMFIELDS_PATH)
    run_sql_dir(SQL_DIR)
    seed_app_roles(ROLES_CONFIG, domain="mawhub.io")
    return {"ok" : True}

