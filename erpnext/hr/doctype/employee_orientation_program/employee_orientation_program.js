// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Orientation Program', {
	refresh: function(frm) {

	},
	onload: function(frm) {
		frm.trigger("get_activities");
		frm.trigger("get_records");
		frm.trigger("get_communications");
	},
	employee:function(frm) {
		if (frm.doc.employee)
			frappe.call({
				method: "get_emp_designation",
				doc: frm.doc,
				callback: function(r) { 
					frm.set_value("designation" ,r.message.designation);
					refresh_field("designation");
				}
			});
			
	},
	get_activities: function(frm) {
			frappe.call({
				method: "get_activities",
				doc: frm.doc,
				callback: function(r) {
					frm.set_value("table_10" ,"");
					if (r.message) { 
						$.each(r.message, function(i, d) {
							var row = frappe.model.add_child(cur_frm.doc, "Employee Orientation Program Activity", "table_10");
							row.activity =d.activity_name ;
						});
					}
					refresh_field("table_10");
				}
			});
		
	},
	get_records: function(frm) {
			frappe.call({
				method: "get_records",
				doc: frm.doc,
				callback: function(r) {
					frm.set_value("table_14" ,"");
					if (r.message) { 
						$.each(r.message, function(i, d) {
							var row = frappe.model.add_child(cur_frm.doc, "Required Records", "table_14");
							row.required_record =d.required_record ;
						});
					}
					refresh_field("table_14");
				}
			});
		
	},
	get_communications: function(frm) {
			frappe.call({
				method: "get_communications",
				doc: frm.doc,
				callback: function(r) {
					frm.set_value("table_13" ,"");
					if (r.message) { 
						$.each(r.message, function(i, d) {
							var row = frappe.model.add_child(cur_frm.doc, "Effective Communication Memebers", "table_13");
							row.data_1 =d.effective_communication ;
						});
					}
					refresh_field("table_13");
				}
			});
		
	},
});
