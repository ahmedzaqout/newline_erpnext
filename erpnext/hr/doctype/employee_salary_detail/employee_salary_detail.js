// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

var emp_num= cur_frm.doc.employee;
var last_salary =0.0;
frappe.ui.form.on('Employee Salary Detail', {
	setup: function(frm) {
		frm.page.set_secondary_action(__('Print'), () => {
			frm.print_doc()
		});
	},
	onload: function(frm) {
		last_salary= frm.doc.basic_salary;



		if (cur_frm.is_new() && !cur_frm.doc.employee){
			cur_frm.set_df_property('employee', 'read_only', 0);
			cur_frm.refresh_field('employee');
			}
		else if (cur_frm.doc.employee) {
			cur_frm.set_df_property('employee', 'read_only', 1);
			cur_frm.refresh_field('employee');
			}

		frm.set_query("salary_component", "earnings", function() {
			return {
				filters: {
					type: "earning"
				}
			}
		});
		frm.set_query("salary_component", "deductions", function() {
			return {
				filters: {
					type: "deduction"
				}
			}
		});

		frm.events.salary_remaining(frm);
		frm.events.get_emp_warnings(frm);

	},

	refresh: function(frm) {	
		if (cur_frm.is_new() && !cur_frm.doc.employee){
			cur_frm.set_df_property('employee', 'read_only', 0);
			cur_frm.refresh_field('employee');
			}
		else if (cur_frm.doc.employee) {
			cur_frm.set_df_property('employee', 'read_only', 1);
			cur_frm.refresh_field('employee');
			}


		if (!frm.doc.__islocal || in_list(frappe.user_roles, ["HR User","HR Manager","System Manager"])) {
				frm.add_custom_button(__("Salary Slip"), function() {
					frappe.new_doc("Salary Slip",{'employee':frm.doc.employee});
				});	
			if(frm.doc.basic_salary)
				frm.add_custom_button(__("Make/Update Salary Structure"), function() {
					frappe.call({
						method: "make_salary_structure",
						doc: frm.doc,
						callback: function(r) {
							frappe.show_alert({message:__("Salary Structure Created"), indicator:'green'});
							}
						});

				});
		}
	

        cur_frm.fields_dict.bank_branch.get_query = function(doc) {
            return {
                filters: {
                    "bank": cur_frm.doc.bank_name
                }
            }
        } 

	},

	employee: function(frm) {
		frappe.model.get_value('Employee Personal Detail', frm.doc.employee, 'employee_name',function(r) {
			if (r)frm.set_value("employee_name", r.employee_name); });
	},

	basic_salary: function(frm) {
			frm.events.calc_day_salary(frm);
			frm.set_value("basic_salary_modified_date",frappe.datetime.nowdate());
			frm.set_value("last_salary",last_salary);
			cur_frm.refresh_fields('basic_salary_modified_date','last_salary');
			frappe.call({
				method:'update_salary_history',
				doc:frm.doc,
				args:{
					'last_salary':last_salary,
					'new_salary':frm.doc.basic_salary
					}	
			});

	},

	job_number: function(frm) {
		frappe.model.get_value('Job Description', frm.doc.job_number, ['grade','experience_year','category','salary_period'],function(r) {
		    if (r){
			frm.set_value("grade", r.grade);
			frm.set_value("experience_years", r.experience_year);
			frm.set_value("grade_category", __(r.category));
			frm.set_value("payroll_frequency", r.salary_period);
			frm.events.calc_basic_salary(frm);
			frm.events.get_earnings(frm);
			frm.events.get_deductions(frm);
			frm.events.salary_remaining(frm);

			}
			 });

	},
	grade: function(frm) {
		if(!frm.doc.grade) frm.set_value("grade_category","");
		frm.events.calc_basic_salary(frm);
	},
	experience_years: function(frm) {
		if(!frm.doc.experience_years) frm.set_value("grade_category","");
		frm.events.calc_basic_salary(frm);
	},
	discount_salary_from_leaves:function(frm) {
		if (frm.get_value('discount_salary_from_overtime_hours') ==1)
				frm.set_value('discount_salary_from_overtime_hours',0);
	},

	user_data: function(frm) { 
	    if (in_list(frappe.user_roles, ["HR User","HR Manager"])) cur_frm.save() ; 
	   	    if ( !frm.doc.__unsaved)
		{
		var userid = emp_num;
		frappe.model.get_value('Employee Personal Detail', emp_num,'user_id',function(r) {
		if (r)  userid= r.user_id;});
		frappe.model.get_value('User', {employee:emp_num},'name',function(r) {
		if (r){
		frappe.set_route("Form", "User", r.name);
		}
		else 
		frappe.new_doc('User',{employee: emp_num});
		});
		}
	},
	personal_detail: function(frm) { 
	    if (in_list(frappe.user_roles, ["HR User","HR Manager"])) cur_frm.save() ; 
	    if ( !frm.doc.__unsaved)
		frappe.model.get_value('Employee Personal Detail', emp_num,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Personal Detail",emp_num);
		}
		else frappe.new_doc('Employee Personal Detail',{employee: emp_num,employee_number: emp_num});
		});
	},
	salary_detail: function(frm) { 
	    if (in_list(frappe.user_roles, ["HR User","HR Manager"])) cur_frm.save() ; 
		frappe.model.get_value('Employee Salary Detail', emp_num,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Salary Detail", emp_num);
		}
		else 
		frappe.new_doc('Employee Salary Detail',{employee: emp_num});
		});
	},
	employment_detail: function(frm) {
	    if (in_list(frappe.user_roles, ["HR User","HR Manager"])) cur_frm.save() ; 
		frappe.model.get_value('Employee Employment Detail', emp_num,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Employment Detail",emp_num);
		}
		else 
		frappe.new_doc('Employee Employment Detail',{employee: emp_num});
		});
	},
	employee_data: function(frm) { 
	    if (in_list(frappe.user_roles, ["HR User","HR Manager"])) cur_frm.save() ; 
		frappe.model.get_value('Employee Data', emp_num,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Data",emp_num);
		}
		else 
		frappe.new_doc('Employee Data',{employee: emp_num});
		});
	},
	
	ending_service__details: function(frm) {
	    if (in_list(frappe.user_roles, ["HR User","HR Manager"])) cur_frm.save() ; 
		frappe.model.get_value('Employee Ending Service  Details', emp_num,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Ending Service  Details",emp_num);
		}
		else
		frappe.new_doc('Employee Ending Service  Details',{employee: emp_num});
		});
	},
	next: function(frm) { 
	    if (in_list(frappe.user_roles, ["HR User","HR Manager"])) cur_frm.save() ; 
		frappe.model.get_value('Employee Data', emp_num,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Data",emp_num);
		}
		else 
		frappe.new_doc('Employee Data',{employee: emp_num});
		});
	},
	back: function(frm) { 
	    if (in_list(frappe.user_roles, ["HR User","HR Manager"])) cur_frm.save() ; 
		frappe.model.get_value('Employee Employment Detail', cur_frm.doc.employee,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Employment Detail",cur_frm.doc.employee);
		}
		else
		frappe.new_doc('Employee Employment Detail',{employee: cur_frm.doc.employee});
		});
	},

	get_earnings:function(frm) {

	frappe.call({
		method:'erpnext.hr.doctype.salary_structure.salary_structure.get_earnings',
		args:{
			"employee":frm.doc.employee,
			"job_number":frm.doc.job_number
			},
		callback:function (r) {
			var earnings = $.map(frm.doc.earnings, function(d) { return d.salary_component });
			for (var i=0; i< r.message.length; i++) {
				if (earnings.includes(r.message[i].salary_component)){ 
					cur_frm.get_field("earnings").grid.grid_rows[i].doc.amount = r.message[i].amount
					cur_frm.get_field("earnings").grid.grid_rows[i].refresh_field("amount")
					}
				else if (earnings.indexOf(r.message[i].name) === -1) {
					var row = frappe.model.add_child(frm.doc, frm.fields_dict.earnings.df.options, frm.fields_dict.earnings.df.fieldname);
					row.salary_component = r.message[i].salary_component;
					row.abbr = r.message[i].abbr;
					row.formula = r.message[i].formula; 
					row.amount = r.message[i].amount;

				}
			}
			frm.refresh_field('earnings');
			}
		})

},


	get_deductions:function(frm) {

	frappe.call({
			method:'erpnext.hr.doctype.salary_structure.salary_structure.get_deductions',
			args:{
				"employee":frm.doc.employee,
				"job_number":frm.doc.job_number
				},
			callback:function (r) {
				var deductions = $.map(frm.doc.deductions, function(d) { return d.salary_component });
				for (var i=0; i< r.message.length; i++) {
					if (deductions.includes(r.message[i].salary_component)){ 
						cur_frm.get_field("deductions").grid.grid_rows[i].doc.amount = r.message[i].amount
						cur_frm.get_field("deductions").grid.grid_rows[i].refresh_field("amount")
					}
					else if (deductions.indexOf(r.message[i].name) === -1) {
						var row = frappe.model.add_child(frm.doc, frm.fields_dict.deductions.df.options, frm.fields_dict.deductions.df.fieldname);
						row.salary_component = r.message[i].salary_component;
						row.abbr = r.message[i].abbr;
						row.formula = r.message[i].formula; 
						row.amount = r.message[i].amount;


					}
				}
				frm.refresh_field('deductions');

			}
		})
},


	salary_remaining:function(frm) {
		frappe.call({
			method:'get_salary_remaining',
			doc:frm.doc,
			callback:function (r) {
				var salary_remaining = $.map(frm.doc.salary_remaining_table, function(d) { return d.remaining_salary });
				for (var i=0; i< r.message.length; i++) {
					var row = frappe.model.add_child(frm.doc, frm.fields_dict.salary_remaining_table.df.options, frm.fields_dict.salary_remaining_table.df.fieldname);
						row.month = r.message[i].month;
						row.salary_slip = r.message[i].name;
						row.remaining_salary = r.message[i].remaining_salary;
						row.salary_ratio = r.message[i].salary_ratio;
						row.salary = r.message[i].basic_salary;
					}
				frm.refresh_field('salary_remaining_table');

				}
		});
},


	get_emp_warnings:function(frm) {
		frappe.call({
			method:'get_emp_warnings',
			doc:frm.doc,
			callback:function (r) {
				var warnings = $.map(frm.doc.warnings, function(d) { return d.employee_violation });
				for (var i=0; i< r.message.length; i++) {
					var row = frappe.model.add_child(frm.doc, frm.fields_dict.warnings.df.options, frm.fields_dict.warnings.df.fieldname);
						row.employee_violation = r.message[i].employee_violation;
						row.penalty = r.message[i].penalty;
						row.penalty_type = r.message[i].penalty_type;
						row.warning_date = r.message[i].warning_date;
						row.discount_hour = r.message[i].discount_hour;
						row.warning_type = r.message[i].warning_type;
						//discount_period_type
					}
				frm.refresh_field('warnings');

				}
		});
},

 	calc_basic_salary: function(frm) {
		if (frm.doc.grade && frm.doc.experience_years)
		{
		
		frappe.model.get_value('Grade Category Detail', {'parent': frm.doc.grade, 'experience_year':frm.doc.experience_years}, 'basic_salary',function(r) {
			    if (!r){
				frm.set_value("basic_salary","0");
				frappe.throw(__("Salary does not setup for that experience years"))
				return false;
				}
				frm.set_value("basic_salary", r.basic_salary)
				frm.events.calc_day_salary(frm);
  			});
		}

		},

	calc_day_salary: function(frm) {
		var day_sal= 0.0
		if(frm.doc.basic_salary){
			frappe.call({
				method: "erpnext.hr.doctype.job_description.job_description.month_days",
				args:{"employee":frm.doc.employee},
				callback: function (r) { 
					total_days_in_month = r.message[0];
					number_of_days = r.message[1];

			if (r.message){ 
				day_sal = parseFloat(frm.doc.basic_salary) / parseFloat(total_days_in_month);
				hour_cost = day_sal /  parseFloat(r.message[2])
			frm.set_value("hour_cost", hour_cost); 				
			frm.set_value("day_salary",day_sal); 


				frappe.db.get_value('HR Settings', {name: 'HR Settings'}, 'overtime_hour_price', (r) => {
					frm.set_value("over_hrs", r.overtime_hour_price); });
			}

		if (r.message && frm.doc.job_number){

	frappe.model.get_value('Job Description', frm.doc.job_number, ['working_hours_per_day','salary_period','overtime_hour'],function(r) {

		     if (r.salary_period == 'Monthly'){
			day_sal = parseFloat(frm.doc.basic_salary) / parseFloat(total_days_in_month);
			hour_cost = day_sal / parseFloat(r.working_hours_per_day)
		     }else{
			 day_sal = parseFloat(frm.doc.basic_salary) /parseFloat(number_of_days) ;
			hour_cost = day_sal / parseFloat(r.working_hours_per_day)
		      }
			frm.set_value("hour_cost", Math.round(hour_cost,3)); 				
			frm.set_value("day_salary", Math.round(day_sal,3)); 
			if (r.overtime_hour)	
				frm.set_value("over_hrs", Math.round(r.overtime_hour,3)); 
			else
				frappe.db.get_value('HR Settings', {name: 'HR Settings'}, 'overtime_hour_price', (r) => {
					frm.set_value("over_hrs", r.overtime_hour_price); });
			
	});  
				}
							}

				});
			}
	}

});



frappe.ui.form.on("Salary Detail",  {

	salary_component: function(frm,cdt,cdn) {
		d = locals[cdt][cdn];
		var childs_num = 0.0;
		if (d.salary_component == __('Bonus Children') )
		     frappe.model.get_value('HR Settings', {'name': 'HR Settings'}, 'bonus_children_ratio', function(c) {
			if (c.bonus_children_ratio){ 
				frappe.call({
					method: "erpnext.hr.doctype.employee_salary_detail.employee_salary_detail.employee_child",
					args: {employee:cur_frm.doc.employee},
					callback: function(r) {
						if (!r.exc && r.message) { 
							childs_num = r.message[0].count;
							d.amount = parseFloat(childs_num) * parseFloat(c.bonus_children_ratio);
							refresh_field("amount", cdn, "earnings");
						}	
					}	
				})

			}
		     }); 
	if (d.salary_component == __('Bonus Wife') )
		     frappe.model.get_value('HR Settings', {'name': 'HR Settings'}, 'bonus_wife_ratio', function(c) {
			if (c.bonus_wife_ratio){ 
				d.amount = parseFloat(c.bonus_wife_ratio);
				refresh_field("amount", cdn, "earnings");
			}
		     }); 

	}

});



