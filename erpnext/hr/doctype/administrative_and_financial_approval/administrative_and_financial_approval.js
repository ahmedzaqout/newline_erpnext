// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Administrative and Financial Approval', {
	refresh: function(frm) {
		if (!frm.doc.__islocal && frappe.user.has_role("HR Manager")) {
			if (frm.doc.__onload && frm.doc.__onload.offer_letter) {
				frm.add_custom_button(__("Offer Letter"), function() {
					frappe.set_route("Form", "Offer Letter", frm.doc.__onload.offer_letter);
					frm.set_value("is_recommended", 1);
					//frm.save();
				});
			} else {
				frm.add_custom_button(__("Offer Letter"), function() {
					frappe.route_options = {
						"status": "Accepted",
						"job_applicant": frm.doc.job_applicant,
						"applicant_name": frm.doc.applicant_name,
						"designation": frm.doc.designation,
						"grade": frm.doc.grade,
						"category": frm.doc.category,
						"salary": frm.doc.salary,
						"offer_date": frm.doc.joining_date,
						"job_opening": frm.doc.job_title,
						"job_number": frm.doc.job_number

					};
					frappe.new_doc("Offer Letter");
					frm.set_value("is_recommended", 1);
				});
			}
		}

	},

	onload: function(frm) {
		const default_company = frappe.defaults.get_default('company');
		frm.set_value('company', default_company);

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

	},
	after_save: function(frm) {
		const company = frappe.defaults.get_default('company');	
		if (company == 'Nawa'){
		 //    frappe.call({
			// method: "new_offer",
			// doc: frm.doc,
			// callback: function(r) { console.log(r)
			// }
		 //    });
		}
	},

	job_applicant:function(frm){
     	     if(frm.doc.job_applicant)
		frappe.call({
			method: "erpnext.hr.get_job_opening_data",
			args:{"job_applicant":frm.doc.job_applicant},
			callback: function(r) { 
			     if(r.message){
			     	console.log(r.message);
				frm.set_value("job_title", r.message[4].job_title);
				frm.set_value("designation", r.message[0].designation);
				frm.set_value("job_number", r.message[0].job_number);
				frm.set_value("department", r.message[0].department);
				
				frm.set_value("grade", r.message[7].grade);
				frm.set_value("salary", r.message[7].basic_salary);
				frm.set_value("category", r.message[7].category);
				frm.set_value("duration", r.message[7].salary_period);
				frm.set_value("working_hours_per_day", r.message[7].working_hours_per_day);
				frm.set_value("hour_cost", r.message[7].hour_cost);
				frm.set_value("monthly_work_hours", r.message[7].monthly_work_hours);
				frm.set_value("experience_year", r.message[7].experience_year);
				
				if (r.message[5]){
					if (r.message[5] == "Unplanned Job"){
							frm.set_value("joining_date", r.message[6].work_starting_date);
					}
				}

			

				frm.set_value("earnings", []); frm.set_value("deductions", []); 
				if(r.message[8]){
					for (var i=0; i< r.message[8].length; i++) {
					var earnings_new_row =  frm.add_child("earnings");
					earnings_new_row.salary_component= r.message[8][i].salary_component;
					earnings_new_row.amount= r.message[8][i].amount;}

				}
				if (r.message[9]){
						for (var j=0; j< r.message[9].length; j++) {
						var deductions_new_row =  frm.add_child("deductions");
						deductions_new_row.salary_component= r.message[9][j].salary_component;
						deductions_new_row.amount= r.message[9][j].amount;}

				}
			
				frm.refresh_fields('earnings','grade','designation','job_number','department','earnings','salary','category','duration','deductions');
			    }
			}
		});

		
}
});


