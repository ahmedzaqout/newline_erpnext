var module_name = "HR";
frappe.pages['attendence'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title:  __("Attendance & Leaves") ,
		single_column: true
	});
frappe.module.make(page,"attendence");
}
{% include "erpnext/public/js/module_page_base.js" %}
