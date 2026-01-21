import frappe
from mawhub.container.app_container import AppContainer
# This is the ONLY place where wiring happens
gemini_key = frappe.conf.get("gemini_api_key")
if not gemini_key:
    frappe.throw("Gemini API Key is missing in site_config.json")
app_container = AppContainer(gemini_api_key=str(gemini_key))

