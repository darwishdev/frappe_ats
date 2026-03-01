// Copyright (c) 2026, darwishdev and contributors
// For license information, please see license.txt

frappe.ui.form.on("Interview", {
    refresh(frm) {
        // Example: Add another button without a group
        frm.add_custom_button(
            __("Open TAL Interview Assistant"),
            () => openTal(frm)
        );
    },
});

function handle_custom_action(frm) {
    // Call the custom Python method
    frm.call({
        method: "custom_action",
        doc: frm.doc,
        callback: function(r) {
            if (r.message && r.message.status === "success") {
                frappe.show_alert({
                    message: __(r.message.message),
                    indicator: "green"
                });
                console.log("Custom action data:", r.message.data);
            }
        },
        error: function(r) {
            frappe.show_alert({
                message: __("Error executing custom action"),
                indicator: "red"
            });
        }
    });
}

function send_interview_reminder(frm) {
    frappe.confirm(
        __("Send reminder email to the candidate for this interview?"),
        () => {
            // User confirmed - proceed with sending reminder
            frappe.show_alert({
                message: __("Sending reminder email..."),
                indicator: "blue"
            });
            
            // Call the send_custom_reminder Python method
            frm.call({
                method: "send_custom_reminder",
                doc: frm.doc,
                callback: function(r) {
                    if (r.message && r.message.status === "success") {
                        frappe.show_alert({
                            message: __(r.message.message),
                            indicator: "green"
                        });
                    }
                },
                error: function(r) {
                    frappe.show_alert({
                        message: __("Error sending reminder"),
                        indicator: "red"
                    });
                }
            });
        }
    );
}

function openTal(frm) {
    const url = "tal://interview-assistant/?interview=" + frm.doc.name;
    window.open(url, "_blank");
}