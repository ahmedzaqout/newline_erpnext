// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.cscript.onload = function(doc, cdt, cdn) {
			cur_frm.set_value("permission_date", frappe.datetime.get_today());
			cur_frm.refresh_field('permission_date');
		if(doc.__islocal) {
			cur_frm.set_value("permission_date", frappe.datetime.get_today());
			cur_frm.refresh_field('permission_date');
		 }
		if ( frappe.user.has_role("HR Manager") || frappe.user.has_role("HR User")){
			console.log(frappe.user.has_role("HR Manager"));
			cur_frm.set_df_property('permission_date', 'read_only', 0);
			cur_frm.set_df_property('from_date', 'read_only', 0);
			cur_frm.set_df_property('to_date', 'read_only', 0);
		}
		else {
			cur_frm.set_df_property('permission_date', 'read_only', 1);
			cur_frm.set_df_property('from_date', 'read_only', 1);
			cur_frm.set_df_property('to_date', 'read_only', 1);
			}

}

frappe.ui.form.on('Exit permission', {
	onload: function(frm) {
		if(doc.__islocal && !frm.doc.permission_date) {
			frm.set_value("permission_date", frappe.datetime.get_today());
			frm.refresh_field('permission_date');
		 }
		if ( frappe.user.has_role("HR Manager") || frappe.user.has_role("HR User")){
			frm.set_df_property('permission_date', 'read_only', 0);
			frm.set_df_property('from_date', 'read_only', 0);
			frm.set_df_property('to_date', 'read_only', 0);
			frm.refresh_field('permission_date');
			frm.refresh_field('to_date');
		}
		else{
			 frm.set_df_property('permission_date', 'read_only', 1);
			frm.set_df_property('from_date', 'read_only', 1);
			frm.set_df_property('to_date', 'read_only', 1);
		}

	},
	refresh: function(frm) {
		//frm.set_value("permission_date", frappe.datetime.get_today());
		//frm.refresh_field('permission_date');
		
		//if (frm.is_new()) {
		//	frm.set_value("status", "Open");
		//}
	},
	
});
