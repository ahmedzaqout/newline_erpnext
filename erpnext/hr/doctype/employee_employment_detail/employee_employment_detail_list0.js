frappe.listview_settings['Employee Employment Detail'] = {
	add_fields: ["sub_dep"],
	filters:[["sub_dep","=","Department"]],
	onload: function(listview) {
		frappe.route_options = {'sub_dep': 'Department'};
		listview.refresh();
	}
};
