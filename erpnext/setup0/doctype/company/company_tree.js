frappe.treeview_settings['Company'] = {
	get_tree_nodes: "erpnext.setup.doctype.company.company.get_children",
	filters: [
		{
			fieldname: "company",
			fieldtype:"Select",
			options: $.map(locals[':Company'], function(c) { return c.name; }).sort(),
			label: __("Company"),
			default: frappe.defaults.get_default('company') ? frappe.defaults.get_default('company') : ""
		}
	],
	breadcrumb: "Hr",
	title: __("Chart Of Accounts"),
	root_label: "Companies",
	get_tree_root: false,
	toolbar: [
		{ toggle_btn: true },
		{
			label:__("Edit"),
			condition: function(node) {
				return !node.is_root;
			},
			click: function(node) {
				frappe.set_route("Form", "Company", node.data.value);
			}
		},
		{
			label:__("New"),
			condition: function(node) {
				return !node.is_root;
			},
			click: function(node) {
				frappe.new_doc("Company", true);
			}
		},
		{
			label:__("View Structure"),
			condition: function(node) {
				return !node.is_root;
			},
			click: function(node) {
				frappe.set_route("hr-structure");
				location.reload();
			}
		}
	],
	menu_items: [
		{
			label: __("New Company"),
			action: function() {
				frappe.new_doc("Company", true);
			},
			condition: 'frappe.boot.user.can_create.indexOf("Company") !== -1'
		}
	],
};
