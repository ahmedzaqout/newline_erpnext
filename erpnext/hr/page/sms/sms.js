var module_name = "HR";
frappe.pages['sms'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("SMS"),
		single_column: true
	});

frappe.module.make(page,"sms");
}
{% include "erpnext/public/js/module_page_base.js" %}
