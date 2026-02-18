from typing import Iterable, Dict, List, Union
import frappe
from frappe.model.document import Document
FieldSpec = Union[List[str], Dict[str, str]]
def _normalize_fields(spec: FieldSpec) -> Dict[str, str]:
    if isinstance(spec, dict):
        return spec
    return {f: f for f in spec}
def create_or_update_doc(
    *,
    doctype: str,
    name: str,
    name_key: str,
    payload: dict,
    scalar_fields: FieldSpec,
    child_tables: FieldSpec | None,
    ignore_permissions: bool = False,
) -> Document:
    """
    Generic create/update helper for Frappe documents.

    :param doctype: Target DocType
    :param name: Document name (primary key)
    :param payload: Incoming payload dict
    :param scalar_fields: Simple fields to update
    :param child_tables: payload_key -> docfieldname mapping
    :return: Updated Document
    """

    # Fetch or create
    if frappe.db.exists(doctype, name):
        doc = frappe.get_doc(doctype, name)
    else:
        doc = frappe.new_doc(doctype)
        doc.set(name_key,name)
    scalar_map = _normalize_fields(scalar_fields)
    # Scalar fields
    for payload_key, fieldname in scalar_map.items():
        if payload_key in payload:
            doc.set(fieldname, payload[payload_key])

    if child_tables:
        child_map = _normalize_fields(child_tables)
        # Child tables
        for payload_key, fieldname in child_map.items():
            if payload_key in payload:
                doc.set(fieldname, [])
                for row in payload[payload_key] or []:
                    doc.append(fieldname, row)

    doc.save(ignore_permissions=ignore_permissions)
    frappe.db.commit()

    return doc

def bulk_create_docs(
    *,
    doctype: str,
    items: Iterable[dict],
    name_key: str,
    scalar_fields: FieldSpec,
    child_tables: FieldSpec | None,
    ignore_permissions: bool = True,
) -> List[Document]:
    """
    Bulk CREATE-ONLY helper for Frappe documents.
    Raises error if document already exists.
    """

    docs: List[Document] = []

    for payload in items:
        name = payload.get(name_key)
        if not isinstance(name, str):
            raise frappe.ValidationError(f"{name_key}_required")

        if frappe.db.exists(doctype, name):
            raise frappe.DuplicateEntryError(
                f"{doctype} already exists: {name}"
            )

        doc = frappe.new_doc(doctype)
        doc.name = name
        scalar_map = _normalize_fields(scalar_fields)
        for payload_key, fieldname in scalar_map.items():
            if payload_key in payload:
                doc.set(fieldname, payload[payload_key])

        # Child tables
        if child_tables:
            child_map = _normalize_fields(child_tables)
            for payload_key, fieldname in child_map.items():
                if payload_key in payload:
                    for row in payload[payload_key] or []:
                        doc.append(fieldname, row)

        # Performance flags (safe for bulk import)
        doc.flags.ignore_version = True

        doc.save(ignore_permissions=ignore_permissions)
        docs.append(doc)

    frappe.db.commit()
    return docs
