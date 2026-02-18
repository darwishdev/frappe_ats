frappe.listview_settings['Job Opening'] = {
    onload: function(listview) {
        frappe.realtime.on(`job_parser`, (data) => {
            console.log("job parser progress:", data);
        });
        frappe.realtime.on(`document_parser`, (data) => {
            console.log("doc parser progress:", data);
        });
        listview.page.add_inner_button('Add From JD', function() {
            new frappe.ui.FileUploader({
                make_attachments: 0, // Don't attach to a specific doc yet
                on_success: (file_doc) => {
                    // 2. Send the file path to the background task
                    frappe.call({
                        method: "mawhub.parsed_document_parse",
                        args: {
                            "path": file_doc.file_url
                        },
                        callback: function(r) {
                            if (r.message && r.message.request_id) {
                                const req_id = r.message.request_id;

                                frappe.show_alert({
                                    message: __("Processing JD in background..."),
                                    indicator: 'blue'
                                });

                                // 3. Listen to the Real-time room using the request_id
                                frappe.realtime.on("jd_parsing_done_" + req_id, (data) => {
                                    frappe.msgprint({
                                        title: __('JD Parsed'),
                                        indicator: 'green',
                                        message: __(`Job Opening for <b>${data.job_title}</b> created.`)
                                    });
                                    listview.refresh();
                                });
                            }
                        }
                    });
                }
            });
        });
    },
    formatters: {
        description(_value, _field, doc) {
            const steps = [...doc.steps]
            const jobName = doc.name
            html = `<div class="flex gap-4">`
            for (const step of steps) {
                console.log("step is" , step)
                html +=  `  <div class="pipeline-step"
                data-job="${jobName}"
                data-step="${step.step_code}"
                style="cursor: pointer;"
                onclick="window.location.hash = '#job-opening/${jobName}?step=${step.step_code}'">
                    <span class="step-count">${step.applicants_count || 0}</span>
                    <span class="step-label">${step.step_name}</span>
                    </div>
                    `
            }
            html += `</div >`
            return html
        }
    },
    filters: [
        [
            "status", "=", "Open"
        ],
        ["owner", "=", frappe.session.user]
    ],
};
