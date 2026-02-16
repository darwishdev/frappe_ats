// Copyright (c) 2026, darwishdev and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Opening", {
    onload_post_render(frm) {
        ensure_vue_root(frm);
    },
    refresh(frm) {
        frappe.realtime.on(`resume_parser_progress:${frm.doc.name}`, (data) => {
            console.log("progress:", data);
        });
        frm._custom_vue_mode = frm._custom_vue_mode || false;
        frm.attachments.attachment_uploaded = (attachment) => attachment_uploaded(frm,attachment)
        frm.add_custom_button(
            __("Toggle Custom View"),
            () => toggle_custom_view(frm),
            __("View")
        );

        frm.add_custom_button("Test", () => {
            frm.call("fetch_job_info").then(res=>{
                console.log("res is" , res)
            })
        })
        

    },
});
function ensure_vue_root(frm) {
    if (frm._vue_root_ready) return;

    const $layout = $(frm.wrapper).find(".form-layout");

    if (!$layout.length) {
        // layout not yet present — try next tick
        setTimeout(() => ensure_vue_root(frm), 50);
        return;
    }

    let vue_wrapper = $("#custom-vue-root");

    if (!vue_wrapper.length) {
        vue_wrapper = $('<div id="custom-vue-root"></div>');
        $layout.after(vue_wrapper);
    }

    frm._vue_root_ready = true;
}
function toggle_custom_view(frm) {
    if (!frm._vue_root_ready) {
        ensure_vue_root(frm);
    }

    const $layout = $(frm.wrapper).find(".form-layout");
    const vue_wrapper = $("#custom-vue-root");

    frm._custom_vue_mode = !frm._custom_vue_mode;

    if (frm._custom_vue_mode) {
        $layout.hide();
        vue_wrapper.show();

        // Destroy existing Vue instance if it exists
        if (frappe.custom_job_openings) {
            // Clean up the old instance
            if (typeof frappe.custom_job_openings.$destroy === 'function') {
                frappe.custom_job_openings.$destroy();
            }
            // Clear the wrapper content
            vue_wrapper.empty();
            frappe.custom_job_openings = null;
        }

        // Always create a new Vue app instance with current job context
        frappe.require("job_openings.bundle.js").then(() => {
            frappe.custom_job_openings = new frappe.ui.JobOpenings({
                wrapper: vue_wrapper,
                page: frm.page || null,
                frm: frm,
            });
        });

    } else {
        vue_wrapper.hide();
        $layout.show();
    }
}
function attachment_uploaded(frm,attachment) {
    const original = frm.attachments.attachment_uploaded;
    original.call(this, attachment);
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
            pipeline_step_id: "SC"
        },
        callback: function (r) {
            if (r.message && r.message.request_id) {
                frappe.show_alert({
                    message: __("Processing Resume in background..."),
                    indicator: "blue"
                });
            }
        }
    });
}
