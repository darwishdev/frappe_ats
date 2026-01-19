from typing import  Protocol, cast
import frappe
from frappe import _
from datetime import timedelta
from frappe.core.doctype.user.user import User
from frappe.utils import now_datetime, random_string
class AuthRepoInterface(Protocol):
    def user_find_by_cashier_code(self, user_name: str)->User: ...
    def token_create_by_user(
        self,
        user_name: str,
        expires_in: int,
    ) -> tuple[str, str]:
        ...


class AuthRepo:
    from erpnext.accounts.doctype.pos_profile.pos_profile import POSProfile
    def user_find_by_cashier_code(self, user_name: str)->User:
        if not user_name:
            frappe.throw(_("Missing cashier code"), frappe.AuthenticationError)

        # 1️⃣ Get the unique User name directly
        user_name = frappe.get_value(
            "User",
            {
                "name": user_name,
                "enabled": 1,
            },
            "name",
        )

        if not user_name:
            frappe.throw(_("Invalid cashier code"), frappe.AuthenticationError)

        # 2️⃣ Load and return the real User document
        user = frappe.get_doc("User", user_name)
        return cast(User , user)
    # returns access token and refresh token
    def token_create_by_user(self, user_name: str, expires_in: int)->tuple[str,str]:
                # 1️⃣ Try to find an existing valid token
        existing = frappe.get_all(
            "OAuth Bearer Token",
            filters={
                "user": user_name,
            },
            fields=[
                "name",
                "access_token",
                "refresh_token",
                "creation",
                "expires_in",
            ],
            order_by="creation desc",
            limit=1,
        )

        if existing:
            token = existing[0]

            # Calculate expiration time
            expiry_time = token["creation"] + timedelta(seconds=token["expires_in"])
            if expiry_time > now_datetime():
                # ✅ Token still valid → return it
                return (
                    str(token["access_token"]),
                    str(token["refresh_token"]),
                )
        token = frappe.get_doc({
            "doctype": "OAuth Bearer Token",
            "user": user_name,
            "access_token": random_string(32),
            "refresh_token": random_string(32),
            "expires_in": expires_in,
            "scopes": "all",
        }).insert(ignore_permissions=True)

        frappe.db.commit()
        access_token = str(token.get("access_token"))
        refresh_token = str(token.get("refresh_token"))
        return access_token,refresh_token


