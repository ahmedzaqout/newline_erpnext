// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sanctions and Penalties', {
	refresh: function(frm) {

	}
});


frappe.ui.form.on("Employee Violation", "go", function(frm,cdt,cdn) {
		cur_frm.refresh();
		d = locals[cdt][cdn];
		doc = frappe.new_doc("Warning Information",{employee: d.violation_type});
		frappe.route_options = {"employee_violation": d.violation_type }
		//frappe.set_route("Form", "Warning Information",doc);
	
	
});
