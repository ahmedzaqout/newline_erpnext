// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Unplanned Job', {
	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			// if (frm.doc.__onload ) {
			// 	frm.add_custom_button(__("Job Opening"), function() {
			// 		frappe.set_route("Form", "Job Opening", frm.doc.__onload.job_opening);

			// 	});
			// } else { 
			// 	frm.add_custom_button(__("Job Opening"), function() {
			// 		frappe.route_options = {
			// 			"job_type": "Unplanned Job",
			// 			"job_number": frm.doc.name,
			// 			"designation": frm.doc.designation,
			// 			"department": frm.doc.department,
			// 			"qualification": frm.doc.qualification,
			// 			"job_code": frm.doc.job_number,

			// 			//"table_11": frm.doc.table_20,
			// 		};
			// 		frappe.new_doc("Job Opening");

			// 	});
			// }
			frm.add_custom_button(__("Job Opening"), function(){
					frappe.model.open_mapped_doc({
					method: "erpnext.hr.doctype.unplanned_job.unplanned_job.make_job_opening",
					frm: cur_frm
				})
			});
		}

	
	},
	
	salary: function(frm){
		calc_day_salary(frm);
	},
	working_hours_per_day: function (frm) {
		calc_day_salary(frm);
	}

});
var calc_day_salary = function(frm) {
		var day_sal= 0.0
		if(frm.doc.salary){
			frappe.call({
				method: "erpnext.hr.doctype.job_description.job_description.month_days",
				callback: function (r) {
					//console.log(r.message)
					if (r.message){
						day_sal = parseFloat(frm.doc.salary) /( parseFloat(frm.doc.working_hours_per_day) * parseFloat(r.message[0]));
						frm.set_value("hour_cost", day_sal); 
						frm.refresh_field("hour_cost");


				}	
			}
		});
		
			
				
		}
	}
