// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Private Work Shift', {
	refresh: function(frm) {

	},
	onload: function(frm) {
	   if(frm.is_new()){
	 	var day_list = ["Saturday","Sunday","Monday","Tuesday","Wednesday","Thursday","Friday"]
		for(var i=0; i<day_list.length; i++) {
		   var row = frappe.model.add_child(cur_frm.doc, "Private Work Shift Details", "work_shift_details");
		   row.day = day_list[i];
		   refresh_field("work_shift_details");
		}

	}

   },
});
