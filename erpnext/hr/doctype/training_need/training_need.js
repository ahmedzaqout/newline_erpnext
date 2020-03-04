// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Training Need', {
	setup: function(frm) {
		frm.fields_dict.employee.get_query = function(doc, cdt, cdn) {
			return {
				//query: "erpnext.hr.doctype.training_need.training_need.employee_qry",
				filters: {department: frm.doc.department}
			}
		}
	},
	refresh: function(frm) {

	}
});
