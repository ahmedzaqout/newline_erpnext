var module_name = "HR";
frappe.pages['recruitment-and-sele'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Recruitment and selection"),
		single_column: true
	});
frappe.module.make(page,"recruitment_and_sele");
}
{% include "erpnext/public/js/module_page_base.js" %}

