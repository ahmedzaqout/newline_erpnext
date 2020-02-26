var module_name = "HR";
frappe.pages['permissions'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Permissions") ,
		single_column: true
	});

frappe.module.make(page,"permissions");
}
{% include "erpnext/public/js/module_page_base.js" %}
