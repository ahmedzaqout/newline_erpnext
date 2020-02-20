// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warning Information', {
	refresh: function(frm) {
		//if (frm.doc.employee_violation && frm.doc.employee) frm.events.get_penalty(frm);
	},
	employee: function(frm){
		frm.events.get_penalty(frm);
	},
	employee_violation: function(frm){
		frm.events.get_penalty(frm);
		frm.events.penalty_times(frm);
	      /** frappe.db.get_value('Warning Information', {'employee':frm.doc.employee,'employee_violation':frm.doc.employee_violation }, ['employee_violation','times'], (r) => {
		      if(r){			
			var employee_violation = r.employee_violation;
			var times = r.times;
			    if (employee_violation){		
				frappe.model.set_value(frm.doctype, frm.docname, "times", times + 1);
				//frm.events.get_penalty(frm);
			     }
		        }
		      else {
				frappe.model.set_value(frm.doctype,frm.docname, "times",1);
				//frm.events.get_penalty(frm);
			}

		});**/

		},


	penalty_times:function(frm){
	    if (frm.doc.employee_violation && frm.doc.employee && frm.doc.warning_date){console.log(frm.doc.warning_date);
		   frappe.call({
				method: "erpnext.hr.doctype.warning_information.warning_information.get_penalty_count",
				args: {
					"employee_violation": frm.doc.employee_violation,
					"employee":frm.doc.employee,
					"warning_date":frm.doc.warning_date
				},
				callback: function(r) {
					//console.log(r);
				}
			});
		}
	},

	get_penalty:function(frm){
	    if (frm.doc.employee_violation && frm.doc.employee && frm.doc.warning_date){ console.log(frm.doc.warning_date);
		frappe.call({
				method: "erpnext.hr.doctype.warning_information.warning_information.get_emp_penalty",
				args: {
					"employee_violation": frm.doc.employee_violation,
					"employee":frm.doc.employee,
					"warning_date":frm.doc.warning_date
				},
				callback: function(d) {

		frappe.db.get_value('Employee Violation', {'violation_type':frm.doc.employee_violation},['penalty_first_time','penalty_second_time','penalty_third_time','penalty_forth_time'], (r) => {console.log(r);
                                    if (d.message == 'penalty_first_time') frm.set_value('penalty', r.penalty_first_time);
                                    if (d.message == 'penalty_second_time') frm.set_value('penalty', r.penalty_second_time);	
                                    if (d.message == 'penalty_third_time') frm.set_value('penalty', r.penalty_third_time);	
                                    if (d.message == 'penalty_forth_time') frm.set_value('penalty', r.penalty_forth_time);
				    frm.refresh_field('penalty');	
frappe.db.get_value('Penalty', {'penalty_name':frm.doc.penalty},['penalty_type','discount_day','discount_period','warning_type'], (c) => {
                                   if (c.discount_day) frm.set_value('discount_hour', c.discount_day);
                                   if (c.discount_period) frm.set_value('discount_period_type', c.discount_period);
 				   if (c.penalty_type) frm.set_value('penalty_type', c.penalty_type);
 			 	   if (c.warning_type) frm.set_value('warning_type', c.warning_type);
                                  
			});	
			});
		} });

		
				
		}}
});
