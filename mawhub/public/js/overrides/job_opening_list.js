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
                on_success: (file_doc) => attach_callback(file_doc.file_url)
            });
        });
        const page_body = listview.page.body[0];


        page_body.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            page_body.classList.add('drag-over'); // optional class for styling
        });

        page_body.addEventListener('dragleave', (e) => {
            e.preventDefault();
            page_body.classList.remove('drag-over');
        });

        page_body.addEventListener('drop', (e) => {
            e.preventDefault();
            page_body.classList.remove('drag-over');

            const files = e.dataTransfer.files;
            if (!files.length) return;

            for (const file of files) {
                uploadAsAttachment(file);
            }
        });
    },
    formatters: {
        description(_value, _field, doc) {
            const steps = [...doc.steps]
            const jobName = doc.name
            html = `<div class="flex gap-4">`
            for (const step of steps) {
                console.log("step is" , step)
                html +=  `  <div class="pipeline-step mx-2"
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
const attach_callback = (file_url) => {
    frappe.call({
        method: "mawhub.parsed_document_parse",
        args: {
            "path": file_url
        },
        callback: function(r) {
            if (r.message && r.message.request_id) {
                frappe.show_alert({
                    message: __("Processing JD in background..."),
                    indicator: 'blue'
                });

            }
        }
    });

}

// Use Frappe’s Attachments class to handle upload
const uploadAsAttachment = (file) => {
    const uploader = new frappe.ui.FileUploader({
        on_success: (file_doc) => {
            console.log("Uploaded:", file_doc.file_url);
            attach_callback(file_doc.file_url);
        }
    });
    console.log("uipload" , Object.keys(uploader.uploader))
    uploader.uploader.add_files([file]);
};
