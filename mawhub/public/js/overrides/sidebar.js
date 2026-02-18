// your_app/public/js/sidebar_override.js
frappe.ui.Sidebar = class Sidebar extends frappe.ui.Sidebar {
    constructor() {
        super(); // Initialize original if needed, or omit if fully replacing
    }

    // Override the setup method to force "Mawhub"
    setup(workspace_title) {
        // Force the workspace title to always be Mawhub
        const original_setup = (title) => {
            this.sidebar_title = title;
            this.check_for_private_workspace(title);
            this.workspace_title = this.sidebar_title.toLowerCase();
            this.prepare();
            this.$sidebar.attr("data-title", this.sidebar_title);
            this.sidebar_header = new frappe.ui.SidebarHeader(this);
            this.make_sidebar();
        }
        const overriden_docs = ["people" , "crm" , "expenses" , "projects" , "selling" , "recruitment" ,"build"]
        const is_overriden = overriden_docs.includes(workspace_title.toLowerCase())
        original_setup(is_overriden ? 'Mawhub' : workspace_title)
        console.log("workspace title is" , workspace_title)
        // this.sidebar_title = "Mawhub";
        // this.check_for_private_workspace(this.sidebar_title);
        // this.workspace_title = "mawhub";
        //
            // this.prepare();
        // this.$sidebar.attr("data-title", this.sidebar_title);
        //
            // // Ensure SidebarHeader exists
        // if (!this.sidebar_header) {
            //     this.sidebar_header = new frappe.ui.SidebarHeader(this);
            // }
        //
            // this.make_sidebar();
    }

    // Override choose_app_name to force the subtitle
    // choose_app_name() {
        //     this.sidebar_title = "Mawhub";
        //     this.header_subtitle = "Mawhub Recruitment"; // Or whatever you prefer
        // }
};
