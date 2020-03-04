// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Job Description', {
	setup: function(frm) {
		if (frappe.defaults.get_user_default("Company") == 'Nawa'){
			frm.custom_make_buttons = {
				'Planned Job': 'Make Planned Job'
			}

			frm.custom_make_buttons = {
				'Unplanned Job': 'Make Unplanned Job'
			}


		}
	},
	

	onload: function(frm) {


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
		frm.set_query("experience_year", "deductions", function() {
			return {
				query: "erpnext.hr.doctype.job_description.job_description.get_experience"	,
				filters	: {"grade" : cur_frm.doc.grade}
			}
		});

	},

	refresh: function(frm) {
		if (!frm.doc.__islocal) {

				frm.add_custom_button(__("Planned Job"), function(){
					frappe.model.open_mapped_doc({
					method: "erpnext.hr.doctype.job_description.job_description.make_planned_job",
					frm: cur_frm
				})
			});
				
				frm.add_custom_button(__("Unplanned Job"), function(){
					frappe.model.open_mapped_doc({
					method: "erpnext.hr.doctype.job_description.job_description.make_unplanned_job",
					frm: cur_frm
				})
				});
		
		}
	}, 
	
	//monthly_work_hours:function(frm) {
		// frm.set_value("hour_cost",parseFloat(basic_salary) / parseFloat(monthly_work_hours));
		 //frm.refresh_field("hour_cost");
	//},
	designation: function(frm) {

	frappe.model.get_value('Earnings Detail', {'designation': frm.doc.designation}, 'ratio',function(r) {
		//console.log(r.ratio)
	    if (r){
		var row = frappe.model.add_child(frm.doc, frm.fields_dict.earnings.df.options, frm.fields_dict.earnings.df.fieldname);
		row.salary_component = 'Premium nature work';
		row.abbr = 'PNW';
		//row.formula = ''; 
		row.amount =r.ratio ;

		frm.refresh_field('earnings');
		}
	});

		
	},
	department: function(frm){
		frappe.model.get_value('Department', frm.doc.department, ['parent_department'],function(r) {
				if (r){
					frm.set_value('circle', r.parent_department);

					frappe.model.get_value('Circle', r.parent_department, ['parent_circle'],function(r) {
				if (r){
					 frm.set_value('management', r.parent_circle);
					
					}
			});
				} 

			});
		frm.refresh_fields(['circle','management'])

	},

	grade: function(frm) {
		/*frappe.call({
				method: "erpnext.hr.doctype.job_description.job_description.get_experience",
				args:{
					"grade": frm.doc.grade},
				callback: function (r) {
					console.log(r.message)
					if (r.message){
		frm.set_df_property('experience_year', 'options', r.message);
		}
		}
});*/

		frm.events.calc_basic_salary(frm);
		frm.events.calc_day_salary(frm);
	},
	experience_year: function(frm) {
		frm.events.calc_basic_salary(frm);
		frm.events.calc_day_salary(frm);
	},
	working_hours_per_day : function(frm){
		frm.events.calc_day_salary(frm);

	},

	calc_basic_salary: function(frm) {
	if (frm.doc.grade & frm.doc.experience_year){
		frappe.model.get_value('Grade Category Detail', {'parent': frm.doc.grade, 'experience_year':frm.doc.experience_year}, 'basic_salary',function(r) {
			    if (!r){
				frm.set_value("basic_salary","0");

				//frappe.throw(__("Salary does not setup for that experience years"))
				//return false;
				}//console.log(r)
				frm.set_value("basic_salary", r.basic_salary);
				frm.events.calc_day_salary(frm);
  			})
		}

	},

	calc_day_salary: function(frm) {
		var day_sal= 0.0
		if(frm.doc.basic_salary){
			frappe.call({
				method: "erpnext.hr.doctype.job_description.job_description.month_days",
				callback: function (r) {
					//console.log(r.message)
					if (r.message){
			if (frm.doc.salary_period == __('Monthly'))
			day_sal = parseFloat(frm.doc.basic_salary) /( parseFloat(frm.doc.working_hours_per_day) * parseFloat(r.message[0]));
	 		else{
		 	day_sal = parseFloat(frm.doc.basic_salary) /( parseFloat(frm.doc.working_hours_per_day) * parseFloat(r.message[0] ) );
			  		 }
			frm.set_value("hour_cost", day_sal); 
			frm.refresh_field("hour_cost");


				}	}
		});
			


		//if (frm.doc.overtime_hour) 
		//	frm.set_value("overtime_hour_cost", day_sal * frm.doc.overtime_hour)				
				
		}
	}
});


// function make_planned_job () {
// 	frappe.model.open_mapped_doc({
// 		method: "erpnext.hr.doctype.job_description.job_description.make_planned_job",
// 		frm: cur_frm
// 	})
// }
//frappe.ui.form.on("Salary Detail",  {
//	salary_component: function(frm,cdt,cdn) {
//		d = locals[cdt][cdn];
//		if( d.salary_component == 'Premium nature work'){
//			frappe.model.get_value('Grade Category Detail', {'parent': grade}, 'basic_salary',function(r) {
//			}
//		}
//	
//	}

//});

