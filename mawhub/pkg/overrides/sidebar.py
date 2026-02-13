import frappe

def patch_sidebar(bootinfo):
    try:
        # 1. Fetch the items from the Sidebar doc
        sidebar = frappe.get_doc("Workspace Sidebar", "Mawhub")

        if not sidebar or not sidebar.items:
            return

        # 2. Map the items strictly
        mawhub_items = []
        for item in sidebar.items:
            mawhub_items.append({
                "label": item.label,
                "link_to": item.link_to,
                "link_type": item.link_type,
                "type": item.type,
                "icon": item.icon,
                "child": item.child or 0,
                "collapsible": item.collapsible or 0,
                "indent": item.indent or 0,
                "keep_closed": item.keep_closed or 0,
                "url": item.url,
            })

        # 3. Get the name of the workspace the user is actually supposed to see
        # We find every workspace the user has access to and replace its sidebar
        # with our Mawhub items.

        new_sidebar_dict = {}

        # This replaces EVERY sidebar entry in the boot payload with Mawhub items
        if hasattr(bootinfo, "workspace_sidebar_item"):
            for ws_name in bootinfo.workspace_sidebar_item.keys():
                new_sidebar_dict[ws_name] = {
                    "label": "Mawhub",
                    "items": mawhub_items,
                    "header_icon": "work",
                }

        # Also add the specific keys just in case
        new_sidebar_dict["Mawhub"] = {"label": "Mawhub", "items": mawhub_items}
        new_sidebar_dict["mawhub"] = {"label": "Mawhub", "items": mawhub_items}

        bootinfo.workspace_sidebar_item = new_sidebar_dict

    except Exception as e:
        frappe.log_error(f"Sidebar Force Patch Error: {str(e)}")
