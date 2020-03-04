// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Department', {
	refresh: function(frm) {

	},

	director: function() {
		
	},
	onload: function(frm) { 
		frm.set_query("parent_department", function() {
			return {
			    query: "erpnext.hr.doctype.department.department.get_parent"
			}
		});
}
});
