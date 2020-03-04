// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Earnings Deductions Tool', {
	refresh: function(frm) {
		frm.trigger("set_to_date");
		//frm.set_value('employee', '');
		//frm.set_value('department', '');
	

	},
	setup: function(frm) {

		frm.set_query("salary_component", "earnings", function() {
			return {
				filters: {
					type: "earning"
				}
			}
		});

		frm.set_query("salary_component", "deductionss", function() {
			return {
				filters: {
					type: "deduction"
				}
			}
		});
	},
	onload: function(frm) {
		frm.set_query("salary_component", "earnings", function() {
			return {
				filters: {
					type: "earning"
				}
			}
		});

		frm.set_query("salary_component", "deductionss", function() {
			return {
				filters: {
					type: "deduction"
				}
			}
		});
	},
	fromdate: function(frm) {
		if(frm.doc.fromdate){
			frm.trigger("set_to_date");
		}
		
	},
	all_employee: function(frm) {
			frm.set_value('department', '');
			frm.set_value('employee', '');
			
	},
	department: function(frm) {
		if(frm.doc.department)
			frm.set_value('employee', '');
			
	},
	set_to_date: function(frm){
	    if(frm.doc.fromdate){
		frappe.call({
			method: 'erpnext.hr.doctype.payroll_entry.payroll_entry.get_end_date',
			args: {
				frequency: "monthly",
				start_date: frm.doc.fromdate
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value('todate', r.message.end_date);
				}
			}
		});
	   }
	},

	add: function(frm) {
		cur_frm.save();
		frappe.call({
			method: "add_earning_deduction",
			doc: frm.doc,
			args:{
				fromdate: frm.doc.fromdate,
				todate: frm.doc.todate,
				employee: frm.doc.employee,
				department: frm.doc.department,
				all_employee: frm.doc.all_employee
				
				},
			callback: function(r) { 
				if (r)
					frappe.show_alert({message:__("Salary Slip updated"), indicator:'green'});
					}
			});
	}
});
