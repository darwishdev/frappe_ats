frappe.listview_settings['Job Opening'] = {
    onload: function(listview) {
        // Store pipeline data for use in formatters

        frappe.realtime.on(`document_parser`, (data) => {
            console.log("parser progress:", data);
        });
        listview.pipeline_data = {};

        setTimeout(() => {
            frappe.call({
                method: "mawhub.job_opening_step_list",
                type: "GET",
                args: {job_names : listview.data.map(d => d.name).join(',')}
            }).then(resp => {
                console.log("resp is" , resp);
                if (resp.message) {
                    listview.pipeline_data = resp.message;

                    // Update DOM directly for each job
                    Object.keys(resp.message).forEach(jobName => {
                        const container = document.getElementById(`pipeline-steps-${jobName}`);
                        if (container) {
                            const pipeline_steps = resp.message[jobName] || [];

                            if (pipeline_steps.length === 0) {
                                container.innerHTML = '<span class="text-muted">No steps</span>';
                            } else {
                                const stepsHtml = pipeline_steps.map(step => `
                                    <div class="pipeline-step"
                                         data-job="${jobName}"
                                         data-step="${step.step_code}"
                                         style="cursor: pointer;"
                                         onclick="window.location.hash = '#job-opening/${jobName}?step=${step.step_code}'">
                                        <span class="step-count">${step.applicants_count || 0}</span>
                                        <span class="step-label">${step.step_name}</span>
                                    </div>
                                `).join('');

                                container.innerHTML = stepsHtml;
                            }
                        }
                    });
                }
            });
        }, 600);

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
        description(value, field, doc) {
            // Return a container with unique ID that will be populated via DOM manipulation
            return `<div class="job-pipeline-steps" id="pipeline-steps-${doc.name}">
                        <span class="text-muted">Loading...</span>
                    </div>`;
        }
    },
    filters: [[
        "status", "=", "Open"
    ]],
};
