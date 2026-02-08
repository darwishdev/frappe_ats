frappe.listview_settings['Job Opening'] = {
    onload: function(listview) {
        // Override the module

        // listview.render_header = function() {
        //     // Clear existing content
        //     this.$result.empty();
        //
        //     // Your custom HTML instead of datatable
        //     this.$result.html(`
        //         <div class="custom-table-wrapper" style="padding: 15px;">
        //             <h3>Custom karem</h3>
        //             <div id="custom-data-container"></div>
        //         </div>
        //     `);
        // };
        // Override the render method to replace datatable

        // Add custom button
        listview.page.add_inner_button('Add From JD', function() {
        console.log(listview.data)
            frappe.msgprint('Custom button clicked');
        });
    },
    formatters: {
        description(value, field, doc) {
            console.log(field);
            console.log(value);
            console.log(doc);
            
            // Static pipeline steps for now - will be dynamic later
            const pipeline_steps = [
                { label: "Online Interview", count: 0 },
                { label: "Offer", count: 0 },
                { label: "Final Interview", count: 0 },
                { label: "Screening", count: 0 },
                { label: "Hired", count: 0 }
            ];

            const stepsHtml = pipeline_steps.map(step => `
                <div class="pipeline-step">
                    <span class="step-count">${step.count}</span>
                    <span class="step-label">${step.label}</span>
                </div>
            `).join('');

            return `<div class="job-pipeline-steps">${stepsHtml}</div>`;
        }
    },
    filters: [["status", "=", "Open"]],
};
