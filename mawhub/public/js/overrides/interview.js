frappe.ui.form.on("Interview", {
    refresh(frm) {
        if (frm.doc.name && !frm.doc.name.includes("new-interview")) {
            frm.add_custom_button(
                __("Personalize Question Bank"),
                () => personalize_question_bank(frm),
                __("AI")
            );

            frm.add_custom_button(
                __("Upload to Google Drive"),
                () => upload_interview_to_drive(frm),
                __("Export")
            );
        }
    },
});

function personalize_question_bank(frm) {
    frappe.confirm(
        __("Generate a personalized question bank for this interview? This may take a few seconds."),
        () => {
            frappe.show_alert({ message: __("Personalizing question bank..."), indicator: "blue" });
            frappe.call({
                method: "mawhub.api.interview_question_bank_api.personalize_question_bank",
                args: { interview_id: frm.doc.name },
                error(r) {
                    frappe.show_alert({
                        message: r.exc || __("Failed to personalize question bank"),
                        indicator: "red"
                    });
                },
                callback(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __("Personalized question bank created: {0}", [r.message]),
                            indicator: "green"
                        });
                        frm.reload_doc();
                    }
                }
            });
        }
    );
}

function upload_interview_to_drive(frm) {
    frappe.show_alert({ message: __("Uploading to Google Drive..."), indicator: "blue" });

    frappe.call({
        method: "mawhub.api.google_drive_api.upload_interview_to_drive",
        args: { interview_id: frm.doc.name },
        callback(r) {
            const result = r.message;
            if (!result) return;

            if (result.status === "unauthorized") {
                frappe.confirm(
                    __("Google Drive access not authorized. Open the authorization page now?"),
                    () => window.open(result.auth_url, "_blank")
                );
                return;
            }

            if (result.status === "success") {
                frappe.msgprint({
                    title: __("Upload Successful"),
                    message: __('Uploaded to <b>tal_assistant</b> folder as {0}.<br><a href="{1}" target="_blank">Open in Drive</a>', [result.file_name, result.file_url]),
                    indicator: "green"
                });
            }
        },
        error(r) {
            frappe.show_alert({
                message: r.exc || __("Upload failed"),
                indicator: "red"
            });
        }
    });
}
