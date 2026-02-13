# Copyright (c) 2026, darwishdev and contributors
# For license information, please see license.txt

# import frappe
import json
from frappe.model.document import Document

from mawhub.pkg.objectutils.objectutils import pick_keys


class ParsedDocument(Document):
    def before_save(self):
        """Automatically build output JSON before saving"""
        sections_data = []

        for row in self.get("sections") or []:
            keys = ["title", "description", "bullet_points", "idx"]
            sections_data.append(pick_keys(row, keys))
        meta_data = self.get("meta_data")
        payload = {
            "meta_data": meta_data,
            "sections": sections_data,
        }

        self.set("output", json.dumps(payload, ensure_ascii=False))

