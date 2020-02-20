// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// For license information, please see license.txt


frappe.ui.form.on("Job Opening", {
        setup: function(frm) {
		//frappe.call({
		//	method: "erpnext.hr.get_job_number_query",
		//	callback: function(r) { 
		//	    var arr = []
		//	    for (var i=0; i< r.message.length; i++) 
		//		arr.push(r.message[i][0]); 
		//	frm.set_df_property('job_number', 'options', arr);
		//	}
		//});
		if(!frappe.defaults.get_user_default("Company") == "Nawa"){
		frm.set_value('job_type', 'Job Description');
			}
		
	},
	onload: function(frm) {
		if(!frappe.defaults.get_user_default("Company") == "Nawa"){
		frm.set_value('job_type', 'Job Description');
			}	
	},
	job_number: function(frm) {
		if (frm.doc.job_number)
		frappe.call({
			method: "erpnext.hr.get_job_description_data",
			//doc: frm.doc,
			args:{"job_number":frm.doc.job_number},
			callback: function(r) { 
			     if(r.message){
				frm.set_value("special_bilities", r.message[0].special_bilities);
				frm.set_value("professiona_ex", r.message[0].professiona_ex);
				frm.set_value("dut_res", []); frm.set_value("fun_item", []);
				for (var i=0; i< r.message[1].length; i++) {
					var new_row =  frm.add_child("dut_res");
					new_row.duties_and_responsibilities= r.message[1][i].duties_and_responsibilities;
					new_row.performance_indicators= r.message[1][i].performance_indicators;}

				for (var i=0; i< r.message[2].length; i++) {
					var new_row =  frm.add_child("fun_item");
					new_row.duties_and_responsibilities= r.message[2][i].duties_and_responsibilities;
					new_row.knowledge_required= r.message[2][i].knowledge_required;
					new_row.required_skills= r.message[2][i].required_skills;}

				frm.refresh_fields('special_bilities','professiona_ex','dut_res','fun_item');
			    }
			}
		});
	},
	refresh: function(frm) {
		/*if (!frm.doc.__islocal) {
				frm.add_custom_button(__("Job Applicant"), function() {
					frappe.set_route("List", "Job Applicant");
				});
			
			
		}*/
}
});

cur_frm.fields_dict.job_type.get_query = function(doc) {
	if(frappe.defaults.get_user_default("Company") == "Nawa"){
		return {
			filters: [
				["name", "in", ["Planned Job", "Unplanned Job"]]
			]
		}
		}else{
			return {
			filters: [
				["name", "Job Description"]
			]
		}
}
}

