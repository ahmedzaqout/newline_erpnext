var module_name = "HR";
frappe.pages['work-shifts-manageme'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Work Shifts Management"),
		single_column: true
	});

frappe.module.make(page,"work_shifts_manageme");
}
{% include "erpnext/public/js/module_page_base.js" %}

