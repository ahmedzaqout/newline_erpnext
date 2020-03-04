frappe.pages['employee-address-cha'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Employee Address Chart',
		single_column: true
	});
}