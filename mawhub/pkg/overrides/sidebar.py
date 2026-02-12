# your_custom_app/utils.py
import frappe

def patch_sidebar(bootinfo):
    """
    Ensures Mawhub sidebar items are prioritized in the boot payload.
    """


    sidebar = frappe.get_doc("Workspace Sidebar" , "Mawhub")
    print("iotesssm")

    if sidebar:
        items = sidebar.get("items")
        print("itemssss")
        print(items)
        items_list = []
        if items:
            for item in items:
                if item:
                    items_list.append(item.as_dict())
        print(items_list)
        print(bootinfo.workspace_sidebar_item)
        # bootinfo.workspace_sidebar_item = items_list
    # # 1. Get the Mawhub sidebar data (assuming 'mawhub' is the workspace name)
    # mawhub_data = bootinfo.get("workspace_sidebar_item", {}).get("mawhub")
    #
    # if mawhub_data:
    #     print("mawww")
    #     # 2. You can inject Mawhub items into the 'home' or current workspace
    #     # so they appear regardless of the active module.
    # for key in bootinfo.workspace_sidebar_item:
    #     # Don't hide the original, just prepend Mawhub items to the current list
    #     original_items = bootinfo.workspace_sidebar_item[key].get("items", [])
    #
    #     # Check if already injected to avoid duplicates
    #     if not any(i.get("label") == "Mawhub Home" for i in original_items):
    #         bootinfo.workspace_sidebar_item[key]["items"] = mawhub_data["items"] + original_items
    #
    # # 3. Force the app name to stay as 'Mawhub' in the header subtitle
    # bootinfo.app_name_style = "Mawhub"
