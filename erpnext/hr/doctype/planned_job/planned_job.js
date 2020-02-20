// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch('job_number', 'grade', 'grade');
cur_frm.add_fetch('job_number', 'designation', 'designation');
cur_frm.add_fetch('job_number', 'employment_type', 'employment_type');
cur_frm.add_fetch('job_number', 'department', 'department');
cur_frm.add_fetch('job_number', 'category', 'category');

frappe.ui.form.on('Planned Job', {
	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			// if (frm.doc.__onload ) {
			// 	frm.add_custom_button(__("Job Opening"), function() {
			// 		frappe.set_route("Form", "Job Opening", frm.doc.__onload.job_opening);

			// 	});
			// } else { 
			// 	frm.add_custom_button(__("Job Opening"), function() {
			// 		frappe.route_options = {
			// 			"job_type" :"Planned Job", 
			// 			"linked_doctype": "Planned Job",
			// 			"job_number": cur_frm.doc.name,
			// 			"designation": frm.doc.designation,
			// 			"department": frm.doc.department,
			// 			"qualification": frm.doc.qualification,
			// 			"job_code": frm.doc.job_number,

			// 			//"table_11": frm.doc.table_20,
			// 		}
			// 		frappe.new_doc("Job Opening");
			// 	});
			// }
			frm.add_custom_button(__("Job Opening"), function(){
					frappe.model.open_mapped_doc({
					method: "erpnext.hr.doctype.planned_job.planned_job.make_job_opening",
					frm: cur_frm
				})
			});
		}

	}, 
		job_number:function(frm){
		var me =frm;

			// erpnext.utils.map_current_doc({
			// 		method: "erpnext.hr.doctype.job_description.job_description.make_planned_job",
			// 		source_doctype: "Sales Order",
			// 		target: me,
			// 		source: me.doc.job_number,
					
			// 	});
				frappe.call({
			        method: "frappe.client.get_list",
			        args: {
			            doctype: "Duties and Responsibilities",
			            filters: {"parent" : me.doc.job_number , "parenttype": "Job Description" ,"company": me.doc.company},
			            fields : ['duties_and_responsibilities','performance_indicators']
			        },
			        callback(r) {
			        	me.doc.dut_res =r.message;
			        	me.refresh_fields("dut_res");

			        }

			    });
    //         if(r.message) {
    //            	erpnext.utils.map_current_doc({
				// 	method: "erpnext.hr.doctype.job_description.job_description.make_planned_job",
				// 	source_doctype: "Sales Order",
				// 	target: me,
				// 	source:r.message
					
				// })
    //         }
    //     }
    // });
	}
});
