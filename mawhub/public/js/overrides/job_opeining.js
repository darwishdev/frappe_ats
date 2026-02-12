// Copyright (c) 2026, darwishdev and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Opening", {
    refresh(frm) {
        console.log("Custom Job Opening refresh hook");
        console.log("FRM object:", frm);

        // Load custom Job Openings bundle if not already loaded
        frappe.require("job_openings.bundle.js").then(() => {
            if (!frappe.custom_job_openings) {
                frappe.custom_job_openings = new frappe.ui.JobOpenings({
                    wrapper: $(frm.wrapper).find(".form-layout"),
                    page: frm.page || null,
                    frm: frm,  // pass the actual frm
                });
            }
        });
    },

    // Example: call server-side method
    some_button_action(frm) {
        frm.call("print_hello", { param1: "Ahmed", param2: 42 })
            .then(r => console.log("Server response:", r))
            .catch(err => console.error(err));
    }
});
