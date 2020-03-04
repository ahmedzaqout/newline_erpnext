// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Permisions', {
	onload: function(frm) {
		
	},
});

cur_frm.set_query('application', "roles", function(doc, cdt, cdn) {
			return {
				filters: {
					"module": "HR",
				}
			};
		});

frappe.ui.form.on('Permision App', {
	onload: function(frm) {
		
	}
	
});