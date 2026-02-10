frappe.pages["job-openings"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Job Openings"),
		single_column: true,
	});
};

frappe.pages["job-openings"].on_page_show = function (wrapper) {
	load_desk_page(wrapper);
};

function load_desk_page(wrapper) {
	let $parent = $(wrapper).find(".layout-main-section");
	$parent.empty();

	frappe.require("job_openings.bundle.js").then(() => {
		frappe.job_openings = new frappe.ui.JobOpenings({
			wrapper: $parent,
			page: wrapper.page,
		});
	});
}