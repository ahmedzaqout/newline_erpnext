var module_name = "HR";
frappe.pages['company-structure'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Company Structure'),
		single_column: true
	});

frappe.module.make(page,"company_structure");
}
{% include "erpnext/public/js/module_page_base.js" %}

