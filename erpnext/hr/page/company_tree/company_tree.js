var module_name = "HR";
frappe.pages['company-tree'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Company Tree"),
		single_column: true
	});

frappe.module.make(page,"company_tree");
}
{% include "erpnext/public/js/module_page_base.js" %}

