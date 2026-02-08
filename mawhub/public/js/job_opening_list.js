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
            console.log("filedis" , field)
            console.log("filedis" , doc)
            if (doc.status === "Open") {
                return `<span style="color:green;font-weight:bold">Hola</span>`;
            }

            return value;
        }
    },
    filters: [["status", "=", "Open"]],
};
