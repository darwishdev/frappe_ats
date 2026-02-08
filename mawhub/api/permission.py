import frappe

def has_app_permission(user=None):
    """Check if user has permission to access Mawhub app"""
    if not user:
        user = frappe.session.user

    # Allow all users to access (customize as needed)
    return True

    # Or restrict to specific roles:
    # return frappe.has_role(user, ["HR User", "HR Manager", "System Manager"])
