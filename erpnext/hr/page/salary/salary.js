var module_name = "HR";
frappe.pages['salary'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title:  __("Salary System"),
		single_column: true
	});
frappe.module.make(page,"salary");
}
{% include "erpnext/public/js/module_page_base.js" %}
