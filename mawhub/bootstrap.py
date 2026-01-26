import frappe
from mawhub.container.app_container import AppContainer

# This stays None until the first time get_app_container() is called
_app_container = None

def get_app_container() -> AppContainer:
    global _app_container

    if _app_container is None:
        site_conf = frappe.get_site_config()
        gemini_key = site_conf.get("gemini_api_key")

        if not gemini_key:
            # Better to log or raise a specific error than frappe.throw
            # if you want to avoid UI-style breaks in CLI
            raise ValueError(f"Gemini API Key is missing for  in coomin_site_config.json")
        _app_container = AppContainer(gemini_api_key=str(gemini_key))

    return _app_container

app_container = get_app_container()
