var module_name = "HR";

frappe.pages['training'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Training'),
		single_column: true
	});
frappe.module.make(page,'training');
}

{% include "erpnext/public/js/module_page_base.js" %}



