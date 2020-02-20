// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('employee', 'employee_name', 'employee_name');

cur_frm.cscript.onload = function(doc, cdt, cdn) {
	if(doc.__islocal) {
		cur_frm.set_value("attendance_date", frappe.datetime.get_today());
		cur_frm.set_value("departure_date", frappe.datetime.get_today());
		 }

	if ( frappe.user.has_role("HR Manager") || frappe.user.has_role("HR User")){
		cur_frm.set_df_property('attendance_date', 'read_only', 0);	
		cur_frm.set_df_property('attendance_time', 'read_only', 0);	
	}
}

cur_frm.fields_dict.employee.get_query = function(doc,cdt,cdn) {
	return{
		query: "erpnext.controllers.queries.employee_query"
	}	
}
		
frappe.ui.form.on("Attendance", "departure_time",function(frm) {
     if(flt(frm.doc.departure_time) !=0){
	frappe.model.get_value("Exit permission", {'employee':frm.doc.employee,'permission_type':'Exit with return','permission_date':frm.doc.attendance_date}, "to_date",function(data) {
      if(data)
	if (flt(data.to_date) == 0)
		frappe.throw(__("Not Allowed! Exit with return permission date does not exist"));
		});
}
})
