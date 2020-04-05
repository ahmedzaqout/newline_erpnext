// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
var ar_fname="";var ar_sname="";var ar_tname="";var ar_family_name="";
var user_email="";
var emp_num= cur_frm.doc.name;
var last_salary =0.0;

frappe.provide("erpnext.hr");

erpnext.hr.EmployeeController = frappe.ui.form.Controller.extend({
    setup: function() {		
    	cur_frm.set_df_property("employee_number", "hidden",0);

		this.frm.fields_dict.user_id.get_query = function(doc, cdt, cdn) {
			return {
				query: "frappe.core.doctype.user.user.user_query",
				filters: {ignore_user_type: 1}
			}
		}

		this.frm.page.set_secondary_action(__('Print'), () => {
			this.frm.print_doc()
		});
		
	},

	onload: function() {
        this.frm.set_value('sub_dep', 'Department');
		last_salary= this.frm.doc.basic_salary;


        this.frm.fields_dict.bank_branch.get_query = function(doc) {
            return {
                filters: {
                    "bank": doc.bank_name
                }
            }
        } 

        this.frm.fields_dict.city.get_query = function(doc) {
            return {
                filters: {
                    "governorate": doc.governorate
                }
            }
        } 


        this.frm.fields_dict.sub_dep.get_query = function(doc) {
            return {
                filters: {"name": ["in", ["Department", "Sub Department", "Sub Association"]]}
            }
        } 
        		

        this.frm.fields_dict.management.get_query = function(doc) {
            return {
                filters: {
                    "parent_management": cur_frm.doc.branch
                }
            }
        } 
        this.frm.fields_dict.circle.get_query = function(doc) {
            return {
                filters: {
                    "parent_circle": cur_frm.doc.management
                }
            }
        } 
        this.frm.fields_dict.department.get_query = function(doc) {
            return {
                filters: {
                    "parent_department": cur_frm.doc.circle
                }
            }
        } 


        this.frm.fields_dict.sub_dep.get_query = function(doc) {
            return {
                filters: {"name": ["in", ["Department", "Sub Department", "Sub Association"]]}
            }
        } 

		this.frm.set_query("salary_component", "earnings", function() {
			return {
				filters: {
					type: "earning"
				}
			}
		});
		this.frm.set_query("salary_component", "deductions", function() {
			return {
				filters: {
					type: "deduction"
				}
			}
		});

		this.frm.events.salary_remaining(this.frm);
		this.frm.events.get_emp_warnings(this.frm);
////////////////////////////
	},

	refresh: function() {
		var me = this;
		if (cur_frm.doc.company != "Danaf"){
						cur_frm.set_df_property("en_fname", "reqd", true);
						//cur_frm.set_df_property("en_sname", "reqd", true);
						//cur_frm.set_df_property("en_tname", "reqd", true);
						cur_frm.set_df_property("en_family_name", "reqd", true);

		}

		cur_frm.set_df_property("employee_number", "hidden",0);
		//cur_frm.toggle_display("naming_series", false);
		erpnext.toggle_naming_series();
		//frappe.db.get_value("HR Settings", {name: 'HR Settings'},"auto_generate_employee_no",function(r) { 
			//if (r && cur_frm.is_new())  {
				//cur_frm.set_df_property("employee", "hidden",0);
				//cur_frm.toggle_display("employee_number", false);
				//cur_frm.set_df_property("employee_number", "hidden",1);
				//cur_frm.set_df_property("employee", "read_only", r.auto_generate_employee_no ==0 ? 0 : 1); 
			//}
		//});


	     if (cur_frm.is_new()){
			frappe.call({
				method: "auto_generate_emp",
				doc: cur_frm.doc,
				callback: function(r)
					{
					if(r.message){ 
						cur_frm.set_value("employee_number", r.message);
						//if (cur_frm.doc.company != "Danaf"){
						//	cur_frm.save() ;}
						//cur_frm.set_df_property("employee", "hidden",1); 
						}
					}
					
				});
         }


		if (!cur_frm.doc.__islocal || in_list(frappe.user_roles, ["HR User","HR Manager","System Manager"])) {
				cur_frm.add_custom_button(__("Salary Slip"), function() {
					frappe.new_doc("Salary Slip",{'employee':cur_frm.doc.name});
				});	
			if(cur_frm.doc.basic_salary)
				cur_frm.add_custom_button(__("Make/Update Salary Structure"), function() {
					frappe.call({
						method: "make_salary_structure",
						doc: cur_frm.doc,
						callback: function(r) {
							frappe.show_alert({message:__("Salary Structure Created"), indicator:'green'});
							}
						});

				});
		}
	
	}


});
/*
frappe.ui.form.on('Employee',{
//////////////////////////////////////////////

cur_frm.cscript = new erpnext.hr.EmployeeController({frm: cur_frm});

*/


//Edited By Maysaa 08032020***********
frappe.ui.form.on("Employee", {
	refresh: function(frm) {
		init_btns(frm);
	},
	date_of_birth: function() {
		return cur_frm.call({
			method: "get_retirement_date",
			args: {date_of_birth: this.frm.doc.date_of_birth}
		});
	},

	salutation: function() {
		if(this.frm.doc.salutation) {
			this.frm.set_value("gender", {
				"Mr": "Male",
				"Ms": "Female"
			}[this.frm.doc.salutation]);
		}
	},
	governorate:function(frm) {
		frm.set_value('city','');
		frm.refresh_field('city')
	},

	validate: function(frm) {
	    if(frm.doc.marital_status == 'Married')
		cur_frm.call({
			method: "add_depenents_bonus",
			args: {"sal_comp": 'Bonus Wife', "employee": frm.doc.name}
		});
	},
	ar_fname:function(frm){	
		if (frm.doc.ar_fname){
			frappe.call({
			method: "erpnext.hr.utils.validate_only_arabic",
			args: { "ar_field": frm.doc.ar_fname }
			});
			frm.set_value("first_name",frm.doc.ar_fname);
			frm.set_value("username",frm.doc.ar_fname);
		}
		frm.trigger("update_employee_name");
	},
	ar_sname:function(frm){
		if (frm.doc.ar_sname)	{
			frappe.call({
			method: "erpnext.hr.utils.validate_only_arabic",
			args: { "ar_field": frm.doc.ar_sname }
			});
		}	

		frm.trigger("update_employee_name");

	},
	ar_tname:function(frm){
		if (frm.doc.ar_tname)	{
			frappe.call({
			method: "erpnext.hr.utils.validate_only_arabic",
			args: { "ar_field": frm.doc.ar_tname }
			});
		}		

		frm.trigger("update_employee_name");
	},
	ar_family_name:function(frm){
		if (frm.doc.ar_family_name)	{
			frappe.call({
			method: "erpnext.hr.utils.validate_only_arabic",
			args: { "ar_field": frm.doc.ar_family_name }
			});
			frm.set_value("last_name",frm.doc.ar_family_name);

		}	
		frm.trigger("update_employee_name");
	},
	en_fname:function(frm){	
		if (frm.doc.en_fname)
			frappe.call({
			method: "erpnext.hr.utils.validate_only_english",
			args: { "en_field": frm.doc.en_fname }
			});
	},
	en_sname:function(frm){
		if (frm.doc.en_sname)	{
			frappe.call({
			method: "erpnext.hr.utils.validate_only_english",
			args: { "en_field": frm.doc.en_sname }
			});
		}	

	},
	en_tname:function(frm){
		if (frm.doc.en_tname)	{
			frappe.call({
			method: "erpnext.hr.utils.validate_only_english",
			args: { "en_field": frm.doc.en_tname }
			});
		}		

	},
	en_family_name:function(frm){
		if (frm.doc.en_family_name)	{
			frappe.call({
			method: "erpnext.hr.utils.validate_only_english",
			args: { "en_field": frm.doc.en_family_name }
			});
		}	

	},
	update_employee_name:function(frm){
		ar_fname = frm.doc.ar_fname ? frm.doc.ar_fname: " ";
		ar_sname = frm.doc.ar_sname ? frm.doc.ar_sname: " ";
		ar_tname = frm.doc.ar_tname ? frm.doc.ar_tname: " ";
		ar_family_name = frm.doc.ar_family_name ? frm.doc.ar_family_name: " ";

 		employee_name =ar_fname+" "+ar_sname+" "+ar_tname+" "+ar_family_name;
		frm.set_value("employee_name",employee_name)
	},

	create_user: function(frm) {
		if (!frm.doc.email)
		{
			frappe.throw(__("Please enter Your Email"))
		}
		frappe.call({
			method: "erpnext.hr.doctype.employee.employee.create_user",
			args: { 
				email:frm.doc.email,
				employee: frm.doc.name },
			callback: function(r)
			{ 
				frm.set_value("user_id", r.message);
				frm.set_df_property("email", "read_only",1);
				frm.save();
			}
		});
	},
	employment_type: function(frm) {
		frappe.model.get_value('Employment Type', frm.doc.employment_type,['work_shift','holiday_list'],function(r) {
		    if(r){
			frm.set_value("work_shift", r.work_shift);
			frm.set_value("holiday_list", r.holiday_list);
			}
		});
	},
	contract_end_date: function(frm) {
		frappe.call({
			method: "update_end_serv",
			doc: frm.doc });
	},
	supervisor: function(frm) {
		//frappe.call({
		//	method: "add_manager_staff",
		//	doc: frm.doc,
		//	callback: function(r)
		//	{}
		//});
	},
	branch: function(frm) {
		if(frm.doc.branch)
		  {
		frm.set_value("work_place_change_date", frappe.datetime.get_today()) ;
		frm.set_value("management", "") ;
		frm.set_value("department", "") ;
		frm.set_value("circle", "") ;	 
		   
	  }
	},
	management: function(frm) {
		if(frm.doc.management)
		  {
		frm.set_value("work_place_change_date", frappe.datetime.get_today()) ;
		frm.set_value("department", "") ;
		frm.set_value("circle", "") ;
		   
	  }
	},
	department: function(frm) {
		if(frm.doc.department)
		  {
		frm.set_value("work_place_change_date", frappe.datetime.get_today()) ;
		 
		   
	  }
	},
	circle: function(frm) {
		if(frm.doc.circle)
		  {
		frm.set_value("work_place_change_date", frappe.datetime.get_today()) ;
		frm.set_value("department", "") ;

	  }
	},

	work_shift: function(frm) {
		if(frm.doc.work_shift)
		  {
			frm.set_value("shift_change_date", frappe.datetime.get_today()) ;
	    	if (!frm.doc.shift_change_date)
				frappe.throw(__("Shift Change Date must be selected"))
		}
		if (!frm.doc.private_work_shift){
			var days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
		    frappe.model.get_value('Work Shift Details', {'parent': frm.doc.work_shift,'day':days[new Date().getDay()]}, ['start_work','end_work'],function(r) {
		if(r){
			frm.set_value("start_work", r.start_work)
			frm.set_value("end_work", r.end_work)

			frappe.call({
			method: "erpnext.assets.doctype.asset_repair.asset_repair.get_downtime",
			args: { 
				"failure_date":r.start_work,
				"completion_date":r.end_work },
			callback: function(r)
			{
				frm.set_value("total_work_hrs", r.message)
			}
		});}
  		})
	  }
	},
	private_work_shift: function(frm) {
		frappe.model.get_value('Private Work Shift Details', {'parent': frm.doc.private_work_shift}, ['start_work','end_work'],function(r) {			
			if(r){
			frm.set_value("start_work", r.start_work)
			frm.set_value("end_work", r.end_work)

			frappe.call({
			method: "erpnext.assets.doctype.asset_repair.asset_repair.get_downtime",
			args: { 
				"failure_date":r.start_work,
				"completion_date":r.end_work },
			callback: function(r)
			{
				frm.set_value("total_work_hrs", r.message)
			}
			});}
  		})
		
	},


	basic_salary: function(frm) { 
		if (!cur_frm.doc.__islocal){
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
		}

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


	get_earnings:function(frm) {
		frappe.call({
			method:'erpnext.hr.doctype.salary_structure.salary_structure.get_earnings',
			args:{
				"employee":frm.doc.name,
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
					"employee":frm.doc.name,
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
			if (frm.doc.basic_salary)
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
				args:{"employee":frm.doc.name},
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
	},
	relieving_date: function(frm){
		if (frm.doc.relieving_date){
		frappe.confirm(
			__('This action will stop the employee. Are you sure you want to continue?'),
			function() {
				frappe.call({
					method:'update_emp_status',
					doc:frm.doc,
					args:{'status':'Left'}	
				});
			},
    		function(){
        		show_alert(__('Employee has been stoped'))
   			}
			)
		}
	},
	type:function(frm){
		//if (frm.doc.type == 'End of the decade')
		//	frappe.model.get_value('Employee', cur_frm.doc.name,'scheduled_confirmation_date',function(r) {
		//		frm.set_value('date_of_joining',r.date_of_joining);
		//	});

	},

//////////////////
	personal_detail_btn: function(frm){
		personal_detail_sections(frm, 0);
		user_data_sections(frm, 1);
		employment_detail_sections(frm, 1);
		employee_data_sections(frm, 1);
		ending_service_details_sections(frm, 1);
	},
	user_data_btn: function(frm){
		personal_detail_sections(frm, 1);
		user_data_sections(frm, 0);
		employment_detail_sections(frm, 1);
		salary_detail_sections(frm, 1);
		employee_data_sections(frm, 1);
		ending_service_details_sections(frm, 1);

	},
	employment_detail_btn: function(frm){
		personal_detail_sections(frm, 1);
		user_data_sections(frm, 1);		
		employment_detail_sections(frm, 0);
		salary_detail_sections(frm, 1);
		employee_data_sections(frm, 1);
		ending_service_details_sections(frm, 1);

	},
	salary_detail_btn: function(frm){
		personal_detail_sections(frm, 1);
		user_data_sections(frm, 1);
		employment_detail_sections(frm, 1);
		salary_detail_sections(frm, 0);
		employee_data_sections(frm, 1);
		ending_service_details_sections(frm, 1);
	},
	employee_data_btn:function(frm){
		personal_detail_sections(frm, 1);
		user_data_sections(frm, 1);
		employment_detail_sections(frm, 1);
		salary_detail_sections(frm, 1);
		employee_data_sections(frm, 0);
		ending_service_details_sections(frm, 1);

	},
	ending_service_details_btn:function(frm){
		personal_detail_sections(frm, 1);
		user_data_sections(frm, 1);
		employment_detail_sections(frm, 1);
		salary_detail_sections(frm, 1);
		employee_data_sections(frm, 1);
		ending_service_details_sections(frm, 0);

	}
});
cur_frm.cscript = new erpnext.hr.EmployeeController({frm: cur_frm});

function personal_detail_sections(frm,hidden) {
	frm.set_df_property("personal_detail_section", "hidden", hidden);
	frm.set_df_property("personal_detail_section2", "hidden", hidden);
	frm.set_df_property("personal_detail_section3", "hidden", hidden);
	frm.set_df_property("personal_detail_section4", "hidden", hidden);
	frm.set_df_property("personal_detail_section5", "hidden", hidden);
	frm.set_df_property("personal_detail_section6", "hidden", hidden);
	frm.set_df_property("personal_detail_section7", "hidden", hidden);
	frm.set_df_property("personal_detail_section8", "hidden", hidden);
	frm.set_df_property("personal_detail_section9", "hidden", hidden);
}
function user_data_sections(frm,hidden) {
	frm.set_df_property("user_data_section", "hidden", hidden);
	frm.set_df_property("user_data_section2", "hidden", hidden);
	frm.set_df_property("user_data_section3", "hidden", hidden);
	frm.set_df_property("user_data_section4", "hidden", hidden);
}

function employment_detail_sections(frm,hidden) {
	frm.set_df_property("employment_detail_section", "hidden", hidden);
	frm.set_df_property("employment_detail_section2", "hidden", hidden);
	frm.set_df_property("employment_detail_section3", "hidden", hidden);
	frm.set_df_property("employment_detail_section4", "hidden", hidden);
	frm.set_df_property("employment_detail_section5", "hidden", hidden);
	frm.set_df_property("employment_detail_section6", "hidden", hidden);
	frm.set_df_property("employment_detail_section7", "hidden", hidden);
	frm.set_df_property("employment_detail_section8", "hidden", hidden);
	frm.set_df_property("employment_detail_section9", "hidden", hidden);
	frm.set_df_property("employment_detail_section10", "hidden", hidden);
}
function salary_detail_sections(frm,hidden) {
	frm.set_df_property("salary_detail_section", "hidden", hidden);
	frm.set_df_property("salary_detail_section2", "hidden", hidden);
	frm.set_df_property("salary_detail_section3", "hidden", hidden);
	frm.set_df_property("salary_detail_section4", "hidden", hidden);
	frm.set_df_property("salary_detail_section5", "hidden", hidden);
	frm.set_df_property("salary_detail_section6", "hidden", hidden);
	frm.set_df_property("salary_detail_section7", "hidden", hidden);
	frm.set_df_property("salary_detail_section8", "hidden", hidden);
	frm.set_df_property("salary_detail_section9", "hidden", hidden);
} 
function employee_data_sections(frm,hidden) {
	frm.set_df_property("employee_data_section", "hidden", hidden);
	frm.set_df_property("employee_data_section1", "hidden", hidden);
	frm.set_df_property("employee_data_section2", "hidden", hidden);
	frm.set_df_property("employee_data_section3", "hidden", hidden);
	frm.set_df_property("employee_data_section4", "hidden", hidden);
	frm.set_df_property("employee_data_section5", "hidden", hidden);
	frm.set_df_property("employee_data_section6", "hidden", hidden);
}
function ending_service_details_sections(frm,hidden) {
	frm.set_df_property("ending_service_details_section", "hidden", hidden);
	frm.set_df_property("ending_service_details_section2", "hidden", hidden);
	frm.set_df_property("ending_service_details_section3", "hidden", hidden);
	frm.set_df_property("ending_service_details_section4", "hidden", hidden);
	frm.set_df_property("ending_service_details_section5", "hidden", hidden);
}

function init_btns(frm){
	personal_detail_sections(frm, 0);
	user_data_sections(frm, 1);
	employment_detail_sections(frm, 1);
	salary_detail_sections(frm, 1);
	employee_data_sections(frm, 1);
	ending_service_details_sections(frm, 1);
}


frappe.ui.form.on("Salary Detail",  {

	salary_component: function(frm,cdt,cdn) {
		d = locals[cdt][cdn];
		var childs_num = 0.0;
		if (d.salary_component == __('Bonus Children') )
		     frappe.model.get_value('HR Settings', {'name': 'HR Settings'}, 'bonus_children_ratio', function(c) {
			if (c.bonus_children_ratio){ 
				frappe.call({
					method: "erpnext.hr.doctype.employee_salary_detail.employee_salary_detail.employee_child",
					args: {employee:cur_frm.doc.name},
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


frappe.ui.form.on('Employee Education', {
	class_per: function(frm, dt, dn) {
		doc = locals[dt][dn];
		if (parseFloat(doc.class_per) >100){
			doc.class_per=0;
			refresh_field("class_per", dn, "employee_education");
		}
	}
});

frappe.ui.form.on('Employee Training Courses', {
	end_date: function(frm, dt, dn) {
		doc = locals[dt][dn];
		if (doc.end_date < doc.start_date)
			frappe.msgprint(__("End Date can not be less than Start Date"))
	}
});




