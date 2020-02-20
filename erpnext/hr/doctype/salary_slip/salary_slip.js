// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('employee', 'employee_name', 'employee_name');

cur_frm.add_fetch('employee', 'image', 'image');
cur_frm.add_fetch('time_sheet', 'total_hours', 'working_hours');


frappe.ui.form.on("Salary Slip", {

	setup: function(frm) {
		frm.set_value('currency',erpnext.get_currency(frm.doc.company));
	   	frm.refresh_field("currency");
		frm.fields_dict["timesheets"].grid.get_field("time_sheet").get_query = function(){
			return {
				filters: {
					employee: frm.doc.employee
				}
			}
		}
		var df = frappe.meta.get_docfield("Salary Detail","amount_ils", cur_frm.doc.name);
		df.in_list_view = 1;
		frm.set_query("salary_component", "earnings", function() {
			return {
				filters: {
					type: "earning"
				}
			}
		})
		frm.set_query("salary_component", "deductions", function() {
			return {
				filters: {
					type: "deduction"
				}
			}
		})
	},

	
	start_date: function(frm){
		if(frm.doc.start_date){
			frm.trigger("set_end_date");
			update_employee_data(frm);
		}
	},
	end_date: function(frm){
		if(frm.doc.end_date){
			update_employee_data(frm);
			
	 calculate_all(frm.doc);
	refresh_many(['amount','gross_pay', 'rounded_total', 'net_pay', 'loan_repayment']);
		}
	},
	set_end_date: function(frm){
		frappe.call({
			method: 'erpnext.hr.doctype.payroll_entry.payroll_entry.get_end_date',
			args: {
				frequency: frm.doc.payroll_frequency,
				start_date: frm.doc.start_date
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value('end_date', r.message.end_date);
				
				}
			}
		})
	},

	company: function(frm) {
		var company = locals[':Company'][frm.doc.company];
		if(!frm.doc.letter_head && company.default_letter_head) {
			frm.set_value('letter_head', company.default_letter_head);
		}
	},

	refresh: function(frm) {
		frm.trigger("toggle_fields")
		frm.trigger("toggle_reqd_fields")
		var salary_detail_fields = ['formula', 'abbr', 'statistical_component']
		cur_frm.fields_dict['earnings'].grid.set_column_disp(salary_detail_fields,false);
		cur_frm.fields_dict['deductions'].grid.set_column_disp(salary_detail_fields,false);

			
		
	},	


	salary_slip_based_on_timesheet: function(frm) {
		frm.trigger("toggle_fields");
		frm.set_value('start_date', '');
	},
	
	payroll_frequency: function(frm) {
		//frm.trigger("toggle_fields");
		frm.set_value('start_date', '');
		update_employee_data(frm);
	},

	employee: function(frm){
		frappe.model.get_value('Employee', frm.doc.employee, ['employee_name'],function(r) {
				if (r) frm.set_value('employee_name', r.employee_name);
			});

		frappe.model.get_value('Employee Employment Detail', frm.doc.employee, ['designation','department','employment_type'],function(r) {
				if (r){
					 frm.set_value('department', r.department);
					 frm.set_value('designation', r.designation);
					 frm.set_value('employment_type', r.employment_type);
					}
			});
		//frm.set_value('start_date', '');
		if(frm.doc.start_date) frm.trigger("set_end_date");
		update_employee_data(frm);
	},

	toggle_fields: function(frm) {
		//frm.toggle_display(['hourly_wages', 'timesheets'],
		//	cint(frm.doc.salary_slip_based_on_timesheet)==1);

		frm.toggle_display(['payment_days', 'total_working_days', 'leave_without_pay'],
			frm.doc.payroll_frequency!="");
	}
	
})

frappe.ui.form.on('Salary Detail', {
	amount: function(frm, dt, dn) {
	 var child = locals[dt][dn];
	 frappe.call({
		method: 'get_ils_exchange_rate',
		doc: frm.doc,
		callback: function(r) {
			if (r.message)
			   frappe.model.set_value(dt,dn, "amount_ils", child.amount* r.message)
			else
			frm.set_value('amount_ils', child.amount ); 


	   refresh_field("amount_ils", dn, "earnings");
			}
		});
	},
	earnings_remove: function(frm, dt, dn) {
		calculate_all(frm.doc, dt, dn);
	},
	deductions_remove: function(frm, dt, dn) {
		calculate_all(frm.doc, dt, dn);
	}
})

frappe.ui.form.on('Salary Slip Timesheet', {
	time_sheet: function(frm, dt, dn) {
		total_work_hours(frm, dt, dn);
	},
	timesheets_remove: function(frm, dt, dn) {
		total_work_hours(frm, dt, dn);
	}
});


var update_employee_data = function(frm,dt, dn) {
		frappe.model.get_value('Employee Salary Detail', frm.doc.employee, ['day_salary','hour_cost','over_hrs','bank_name','bank_ac_no','basic_salary','payroll_frequency'],function(r) {
				if (r) {
					frm.set_value('basic_salary', r.basic_salary);
					//frm.set_value('day_salary', r.basic_salary/doc.total_working_days);
					//frm.set_value('hour_cost', doc.day_salary);
					frm.set_value('hour_rate', r.over_hrs);
					frm.set_value('bank_name', r.bank_name);
					frm.set_value('bank_account_no', r.bank_ac_no);
					frm.set_value('payroll_frequency', r.payroll_frequency);
					frm.set_value('total_overtime', 0.0);
					//frm.set_value('over_hrs', r.over_hrs);
					//var total_overtime = Math.round(flt(r.hour_cost) * flt(r.over_hrs) * flt(frm.doc.total_working_hour)*100)/100;
					//frm.set_value('total_overtime', Math.round( flt(frm.doc.total_working_hour) *100)/100 );

				frappe.call({
				method: 'erpnext.hr.doctype.salary_slip.salary_slip.get_working_total_hours',
				args:{
					'employee':frm.doc.employee,
					'start_date':frm.doc.start_date,
					'end_date':frm.doc.end_date
					},
				callback: function(r) {// console.log(r.message);
					var total_hrs= r.message[0];
					var hrs_disc= r.message[1]; 
					var total_hours_discount= flt(frm.doc.hour_cost) * flt(hrs_disc) || 0.0001;

					frm.set_value('total_working_hours',total_hrs );
					frm.set_value('hrs_disc',hrs_disc );
					frm.set_value('total_hours_discount',total_hours_discount );


					refresh_many(['total_working_hours','hrs_disc','total_hours_discount']);
					
				}
			});

				refresh_many(['over_hrs','total_overtime','earnings']);

				}
			});
	

	 calculate_all(frm.doc, dt, dn);
	refresh_many(['amount','gross_pay', 'rounded_total', 'net_pay', 'loan_repayment']);

}

var calc_day_hrs_salary = function(frm) {
  if(frm.doc.start_date){
	frappe.call({
		method: "erpnext.hr.doctype.job_description.job_description.month_days",
		args:{
			"employee":frm.doc.employee,
			"cur_date":frm.doc.start_date},
		callback: function (r) { 
			if (r.message){ 
				day_sal = parseFloat(frm.doc.basic_salary) / parseFloat(frm.doc.total_working_days);
				hour_cost = day_sal / parseFloat(r.message[2]);
				frm.set_value("day_salary", day_sal); 
				frm.set_value("hour_cost", hour_cost); 				
				refresh_many(['day_salary','hour_cost']);
				}
		}
	});
  }
}
// Get leave details
//---------------------------------------------------------------------
cur_frm.cscript.start_date = function(doc, dt, dn){
	if(doc.start_date){
		return frappe.call({
			method: 'get_emp_and_leave_details',
			doc: locals[dt][dn],
			callback: function(r, rt) {
				cur_frm.refresh();
				calculate_all(doc, dt, dn);
			}
		});
	}
}

cur_frm.cscript.payroll_frequency =  cur_frm.cscript.start_date;

cur_frm.cscript.employee = function(doc,dt,dn){
//	doc.salary_structure = ''
	cur_frm.cscript.start_date(doc, dt, dn)
}

cur_frm.cscript.leave_without_pay = function(doc,dt,dn){
	if (doc.employee && doc.start_date && doc.end_date) {
		return $c_obj(doc, 'get_leave_details', {"lwp": doc.leave_without_pay}, function(r, rt) {
			var doc = locals[dt][dn];
			cur_frm.refresh();
			calculate_all(doc, dt, dn);
		});
	}
}

var calculate_all = function(doc, dt, dn) {
	calculate_earning_total(doc, dt, dn);
	calculate_ded_total(doc, dt, dn);
	calculate_net_pay(doc, dt, dn);
	
}

cur_frm.cscript.amount = function(doc,dt,dn){
	var child = locals[dt][dn];
	if(!doc.salary_structure){
		frappe.model.set_value(dt,dn, "default_amount", child.amount)
	}
	calculate_all(doc, dt, dn);
}

cur_frm.cscript.depends_on_lwp = function(doc,dt,dn){
	calculate_earning_total(doc, dt, dn, true);
	calculate_ded_total(doc, dt, dn, true);
	calculate_net_pay(doc, dt, dn);
	refresh_many(['amount','gross_pay', 'rounded_total', 'net_pay', 'loan_repayment']);
};

// Calculate earning total
// ------------------------------------------------------------------------
var calculate_earning_total = function(doc, dt, dn, reset_amount) {

	var tbl = doc.earnings || [];
	var total_earn = 0;
	for(var i = 0; i < tbl.length; i++){
		if(cint(tbl[i].depends_on_lwp) == 1) {
			tbl[i].amount =  Math.round(tbl[i].default_amount)*(flt(doc.payment_days) /
				cint(doc.total_working_days)*100)/100;
		} else if(reset_amount) {
			tbl[i].amount = tbl[i].default_amount;
		}
		if(!tbl[i].do_not_include_in_total) {
			total_earn += flt(tbl[i].amount);

		}
	}
	doc.gross_pay = total_earn;
	refresh_many(['earnings', 'amount','gross_pay']);

}

// Calculate deduction total
// ------------------------------------------------------------------------
var calculate_ded_total = function(doc, dt, dn, reset_amount) {
	var tbl = doc.deductions || [];
	var total_ded = 0;
	for(var i = 0; i < tbl.length; i++){
		if(cint(tbl[i].depends_on_lwp) == 1) {
			tbl[i].amount = Math.round(tbl[i].default_amount)*(flt(doc.payment_days)/cint(doc.total_working_days)*100)/100;
		} else if(reset_amount) {
			tbl[i].amount = tbl[i].default_amount;
		}
		if(!tbl[i].do_not_include_in_total) {
			total_ded += flt(tbl[i].amount);
		}
	}
	doc.total_deduction = total_ded;
	refresh_many(['deductions', 'total_deduction']);
}

// Calculate net payable amount
// ------------------------------------------------------------------------
var calculate_net_pay = function(doc, dt, dn) {
	doc.net_pay = flt(doc.gross_pay) -flt(doc.total_hours_discount)- flt(doc.total_loan_repayment)- flt(doc.total_deduction) +flt(doc.total_overtime);
	if (doc.net_pay <0) cur_frm.set_value('net_pay',0.0001);
	doc.rounded_total = doc.net_pay;
	refresh_many(['net_pay', 'rounded_total']);
}

// validate
// ------------------------------------------------------------------------
cur_frm.cscript.validate = function(doc, dt, dn) {
	calculate_all(doc, dt, dn);
}

//cur_frm.fields_dict.employee.get_query = function(doc,cdt,cdn) {
//	return{
		//query: "erpnext.controllers.queries.employee_query"
//	}
//}

// calculate total working hours, earnings based on hourly wages and totals
// ------------------------------------------------------------------------
var total_work_hours = function(frm, dt, dn) {
	frm.set_value('total_working_hour', 0);

	$.each(frm.doc["timesheets"] || [], function(i, timesheet) {
		frm.doc.total_working_hour += timesheet.working_hours;
	});
	frm.refresh_field('total_working_hour');

	var wages_amount = frm.doc.total_working_hour * frm.doc.over_hrs;

	frappe.db.get_value('Salary Structure', {'name': frm.doc.salary_structure}, 'salary_component', (r) => {
		frm.set_value('gross_pay', 0);

		$.each(frm.doc["earnings"], function(i, earning) {
			if (earning.salary_component == r.salary_component) {
				earning.amount = wages_amount;
				frm.refresh_fields('earnings');
			}
			if (frm.doc.payroll_frequency=='Monthly' && earning.salary_component=='Basic')
				frm.doc.gross_pay +=frm.doc.total_working_hours * frm.doc.hour_cost ;
			else
				frm.doc.gross_pay += earning.amount;
		});

		frm.refresh_field('gross_pay');
		calculate_net_pay(frm.doc, dt, dn);
	});
}
