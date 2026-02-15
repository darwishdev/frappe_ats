// Copyright (c) 2026, darwishdev and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Opening", {
    refresh(frm) {
        console.log("frm is" , frm.attachments.attachment_uploaded)
        const original = frm.attachments.attachment_uploaded;
        console.log("proggesss")
        frappe.realtime.on("job_info_progress", (data) => {
            console.log("progress:", data);
        });

        frm.attachments.attachment_uploaded = function(attachment) {
            // 1️⃣ call original behavior
            original.call(this, attachment);

            // 2️⃣ run your custom logic
            if (!attachment.file_url.toLowerCase().endsWith(".pdf")) {
                frappe.show_alert({
                    message: __("Only PDF resumes will be parsed"),
                    indicator: "orange"
                });
                return;
            }

            frappe.call({
                method: "mawhub.applicant_resume_parse",
                args: {
                    path: attachment.file_url,
                    job_opening_id: frm.doc.name,
                    pipeline_step_id: "TE"
                },
                callback: function (r) {

                    if (r.message && r.message.request_id) {
                        const req_id = r.message.request_id;

                        frappe.show_alert({
                            message: __("Processing Resume in background..."),
                            indicator: "blue"
                        });

                        frappe.realtime.on(
                            "resume_parsing_done_" + req_id,
                            (data) => {
                                frappe.msgprint({
                                    title: __("Resume Parsed"),
                                    indicator: "green",
                                    message: __(
                                        `Applicant <b>${data.applicant_name}</b> created.`
                                    )
                                });

                                frm.reload_doc();
                            }
                        );
                    }
                }
            });
            console.log("Attachment uploaded intercepted for Job Opening:", attachment);
        }

        frm.add_custom_button("Test", () => {
            frm.call("fetch_job_info").then(res=>{
                console.log("res is" , res)
            })
        })
        // Load custom Job Openings bundle if not already loaded
        // Only render custom Vue app in edit mode (not when creating new document)
        if (!frm.doc.name || !frm.doc.name.includes("new-job-opening")) {
            frappe.require("job_openings.bundle.js").then(() => {
                if (!frappe.custom_job_openings) {
                    frappe.custom_job_openings = new frappe.ui.JobOpenings({
                        wrapper: $(frm.wrapper).find(".form-layout"),
                        page: frm.page || null,
                        frm: frm,  // pass the actual frm
                    });
                }
            });
        }
    },
});
