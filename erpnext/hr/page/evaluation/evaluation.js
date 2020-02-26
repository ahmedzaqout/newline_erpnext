var module_name = "HR";
frappe.pages['evaluation'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title:  __("Evaluation") ,
		single_column: true
	});
frappe.module.make(page,"evaluation");
}
{% include "erpnext/public/js/module_page_base.js" %}
