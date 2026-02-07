// mawhub/public/js/job_applicant_override.js

// Listen for any route change
frappe.router.on('change', () => {
    const route = frappe.get_route(); // e.g., ["List", "Job Applicant", "List"]
    if (route[0] === "List" && route[1] === "Job Applicant") {

        // Patch listview_settings for this DocType
        frappe.listview_settings['Job Applicant'] = {
            onload(listview) {
                console.log("Job Applicant ListView override applied!");
                listview.page.set_title("Candidates");
                listview.page.icon = "google";
                listview.page._module = "Mawhub";
            },
            formatters: {
                status: (value) => {
                    if (value === "Rejected") return `<span style="color:red">${value}</span>`;
                    if (value === "Selected") return `<span style="color:green">${value}</span>`;
                    return value;
                }
            }
        };
    }
});
