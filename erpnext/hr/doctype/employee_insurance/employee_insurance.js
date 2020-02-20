// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Insurance', {
	refresh: function(frm) {
		frappe.call({
				method: "erpnext.hr.doctype.employee_insurance.employee_insurance.get_insurance_deduction",
				callback: function(r) {
					frm.set_value("insurance_deduction",r.message )
				}
			});

		frappe.call({
				method: "erpnext.hr.doctype.employee_insurance.employee_insurance.get_insurance_allowance",
				callback: function(r) {
					frm.set_value("insurance_allowance",r.message )
				}
			});

	}
});
