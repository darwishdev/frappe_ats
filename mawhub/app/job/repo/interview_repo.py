from typing import Protocol
import frappe
from mawhub.sqltypes.table_models import Interview

class InterviewRepoInterface(Protocol):
	def interview_create_update(self, payload: Interview)->Interview: ...

class InterviewRepo:
    def interview_create_update(self, payload: Interview)->Interview:
        name = payload.get("name")
        if not name or len(name) == 0:
            doc = frappe.new_doc("Interview")
        else:
            doc = frappe.get_doc("Interview" , payload.get('name'))
            if not doc :
                raise frappe.NotFound(f"Interview {payload.get('name')} Not Found")
        try:
            doc.update(payload)
            doc.save()
            frappe.db.commit()
            return payload
        except Exception as e:
            frappe.db.rollback()
            raise e
