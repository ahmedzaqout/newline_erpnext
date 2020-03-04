// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Interviewer Evaluation', {
	refresh: function(frm) {
		if (!frm.doc.__islocal && frappe.user.has_role("HR Manager")) {
			if (frm.doc.__onload && frm.doc.__onload.administrative_and_financial_approval) {
				frm.add_custom_button(__("Administrative and Financial Approval"), function() {
					frappe.set_route("Form", "Administrative and Financial Approval", frm.doc.__onload.administrative_and_financial_approval);
				}, __("View"));
			} else if (!frm.doc.__islocal && frm.doc.docstatus==1){
				frm.add_custom_button(__("Administrative and Financial Approval"), function() {
					frappe.route_options = {
						"job_applicant": frm.doc.job_applicant,
						"applicant_name": frm.doc.applicant_name,
						"designation": frm.doc.job_opening,
					};
					frappe.new_doc("Administrative and Financial Approval");
					frm.set_value("is_recommended", 1);
				});
				frm.add_custom_button(__("Add Applicants"), function() {
					
				});
		
			}

				
		}
	},

});
frappe.ui.form.on('Trial Period Evaluation Details', {
	table_2_remove:function(frm, dt, dn) {
		update_final_result(frm, dt, dn);
	},
	table_4_remove:function(frm, dt, dn) {
		update_final_result(frm, dt, dn);
	},
	table_6_remove:function(frm, dt, dn) {
		update_final_result(frm, dt, dn);
	}
});

frappe.ui.form.on("Trial Period Evaluation Details", "degree", function(frm, dt, dn) { 
		update_final_result(frm, dt, dn);
});

var update_final_result = function(frm, dt, dn) {
	var final_result1 = 0;
	$.each(cur_frm.doc["table_2"] || [], function(i, t1) {
		final_result1 += t1.degree;
	});		
	var final_result2 = 0;
	$.each(cur_frm.doc["table_4"] || [], function(i, t2) {
		final_result2 += t2.degree;
	});
	var final_result3 = 0;
	$.each(cur_frm.doc["table_6"] || [], function(i, t3) {
		final_result3 += t3.degree;
	});

	//var d = locals[cdt][cdn];
	final_result = final_result1+ final_result2 +final_result3; 
	cur_frm.set_value("final_result", final_result);
}


