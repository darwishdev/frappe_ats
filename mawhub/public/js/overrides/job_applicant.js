frappe.listview_settings['Job Applicant'] = {
    onload(listview) {
        frappe.throw("hello")
        console.log("Job applicants custom")
        // Change the page title
        listview.page.set_title("Candidates");

        // Change the icon
        listview.page.icon = "google";

        // Override the module for the UI/sidebar
        listview.page._module = "Mawhub";

        // Optional: set a fixed breadcrumb if you have multiple levels
        listview.page.set_breadcrumb("Mawhub");
    },

    // Optional: default filters
    onload_post_render(listview) {
        // Example: only show applicants with status "Applied"
        // listview.filter_area.add([['status', '=', 'Applied']])
    },

    // Optional: format fields
    formatters: {
        status: (value) => {
            if (value === "Rejected") return `<span style="color:red">${value}</span>`;
            if (value === "Selected") return `<span style="color:green">${value}</span>`;
            return value;
        }
    }
};

