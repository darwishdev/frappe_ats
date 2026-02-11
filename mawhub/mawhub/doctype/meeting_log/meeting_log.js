frappe.ui.form.on("Meeting Log", {
    questions_template: function(frm) {
        if (!frm.doc.questions_template) {
            frm.clear_table("questions");
            frm.refresh_field("questions");
            return;
        }

        frappe.model.with_doc("Question Template", frm.doc.questions_template, function() {
            const template = frappe.model.get_doc(
                "Question Template",
                frm.doc.questions_template
            );

            // clear existing rows
            frm.clear_table("questions");

            // copy rows from template table_lrsx → questions
            (template.table_lrsx || []).forEach(row => {
                let child = frm.add_child("questions");

                // copy matching fields — adjust if your child doctype has more fields
                Object.keys(row).forEach(key => {
                    if (!["name", "parent", "parentfield", "parenttype", "idx"].includes(key)) {
                        child[key] = row[key];
                    }
                });
            });

            frm.refresh_field("questions");
        });
    }
});
