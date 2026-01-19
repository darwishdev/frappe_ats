import frappe
from frappe import _
from mawhub.app.job.dto.auth import LoginResponse
from mawhub.bootstrap import app_container

@frappe.whitelist(methods=["POST"], allow_guest=True)
def user_login(user_name: str, user_password: str)->LoginResponse:
    return app_container.job_usecase.auth.user_login(
            user_name,
            user_password,
        )
