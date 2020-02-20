var module_name = "HR";
frappe.pages['work-shift'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Work Shift"),
		single_column: true
	});

frappe.module.make(page,"work_shift");
}
{% include "erpnext/public/js/module_page_base.js" %}

