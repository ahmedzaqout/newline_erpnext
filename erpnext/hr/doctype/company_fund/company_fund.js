// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Company Fund', {
	refresh: function(frm) {

	},
	employee: function (frm) {
	frappe.model.get_value('Employee', {'employee': frm.doc.employee}, 'date_of_joining',
	function(data) {   frm.set_value("date_of_joining", data.date_of_joining);  });
	},
});
