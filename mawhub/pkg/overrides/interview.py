# Copyright (c) 2026, darwishdev and contributors
# For license information, please see license.txt

from __future__ import annotations
from typing import TYPE_CHECKING

import frappe
from frappe import _
from hrms.hr.doctype.interview.interview import Interview

if TYPE_CHECKING:
    from frappe.model.document import Document


class CustomInterview(Interview):
    """
    Custom Interview class extending the default HRMS Interview doctype.
    Add your custom methods here.
    """
    
    @frappe.whitelist()
    def send_custom_reminder(self):
        """
        Example custom method that can be called from the client side.
        This method sends a custom reminder for the interview.
        """
        # Add your custom logic here
        frappe.msgprint(_("Custom reminder logic executed for Interview: {0}").format(self.name))
        
        return {
            "status": "success",
            "message": "Reminder sent successfully"
        }
    