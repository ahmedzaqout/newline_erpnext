// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('employee', 'employee_name', 'employee_name');

cur_frm.cscript.onload = function(doc, cdt, cdn) {
	if(doc.__islocal) {
		cur_frm.set_value("departure_date", frappe.datetime.get_today());
		 }

	if ( frappe.user.has_role("HR Manager") || frappe.user.has_role("HR User")){
		cur_frm.set_df_property('departure_date', 'read_only', 0);	
		cur_frm.set_df_property('departure_time', 'read_only', 0);	
	}
}
frappe.ui.form.on('Departure', {
	refresh: function(frm) {

	}
});
