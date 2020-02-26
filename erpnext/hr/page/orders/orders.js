var module_name = "HR";
frappe.pages['orders'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("The Orders"),
		single_column: true
	});
frappe.module.make(page,"orders");
}
{% include "erpnext/public/js/module_page_base.js" %}
