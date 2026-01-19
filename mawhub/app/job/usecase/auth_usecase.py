
from frappe import _
import frappe
from frappe.auth import LoginManager
from typing import Protocol

from mawhub.app.job.dto.auth import LoginResponse
from mawhub.app.job.repo.job_repo import JobRepoInterface


class AuthUsecaseInterface(Protocol):
    def user_login(
        self,
        user_name: str,
        user_password: str,
    ) -> LoginResponse: ...

class AuthUsecase:
    repo: JobRepoInterface
    def __init__(
        self,
        repo: JobRepoInterface,
    ):
        self.repo = repo

    def user_login(self, user_name: str, user_password: str)->LoginResponse:
        user = self.repo.auth.user_find_by_cashier_code(user_name)
        if not user_password:
            frappe.throw(_("Missing user password"), frappe.AuthenticationError)
        login_manager = LoginManager()
        user_name = str(user.name)
        login_manager.authenticate(user_name, user_password)
        login_manager.post_login()
        expires_in = 60 * 60   # 1 hour
        access_token , refresh_token = self.repo.auth.token_create_by_user(str(user.name),expires_in)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": expires_in,
            "user": {
                "name": str(user.name),
                "email": str(user.email),
            },
        }


