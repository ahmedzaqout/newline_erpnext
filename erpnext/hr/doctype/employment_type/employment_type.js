// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employment Type', {
	refresh: function(frm) {

	},
	status:function(frm) {
		if (frm.doc.status == 'Not Active'){
			frappe.model.get_value('Employee', {'employment_type': frm.doc.employment_type},'name',function(r) {
				if (r.name) 
					frappe.throw(__("Can not disactivated! There is an employee connected with this"));
			
			});
		}
	}
});
