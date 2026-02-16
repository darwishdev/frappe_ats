// Copyright (c) 2026, darwishdev and contributors
// For license information, please see license.txt
frappe.ui.form.on("Job Pipeline", {
    refresh(frm) {
        console.log("Form object:", frm);
        // Load the bundle if not already loaded
        frappe.require("job_openings.bundle.js").then(() => {
            // Initialize JobOpenings UI with the form's wrapper
            if (!frappe.job_openings) {
                frappe.job_openings = new frappe.ui.JobOpenings({
                    wrapper: $(frm.wrapper).find(".form-layout"),
                    page: frm.page || null, // in case you have a page object, otherwise null
                    frm: frm,               // pass the actual frm
                });
            }
        });
    },
});
