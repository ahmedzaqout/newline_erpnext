// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Job  Employee Audit', {
	refresh: function(frm) {

	},
	onload: function(frm) {
		if(frm.is_new())
			frm.trigger("get_records");
	},
	employee:function(frm) {
		if (frm.doc.employee)
			frappe.call({
				method: "get_emp_data",
				doc: frm.doc,
				callback: function(r) {
					frm.set_value("designation" ,r.message[0]);
					frm.set_value("job_number" ,r.message[1]);
					frm.set_value("home_number" ,r.message[2]);
					frm.set_value("mobile_number" ,r.message[3]);
					frm.set_value("work_starting_date" ,r.message[4]);
					frm.refresh_fields();
				}
			});
			
	},
	get_records: function(frm) {
			frappe.call({
				method: "get_records",
				doc: frm.doc,
				callback: function(r) {
					frm.set_value("table_6" ,"");
					if (r.message) { 
						$.each(r.message, function(i, d) {
							var row = frappe.model.add_child(cur_frm.doc, "Required Records", "table_6");
							row.required_record =d.required_record ;
						});
					}
					refresh_field("table_6");
				}
			});
		
	},
});
