// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// For license information, please see license.txt

// for communication
cur_frm.email_field = "email_id";
cur_frm.fields_dict['city'].get_query = function(doc, cdt, cdn) {
	return{
		filters:{"governorate":cur_frm.doc.governorate}
	}
}

frappe.ui.form.on("Job Applicant", {

	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			if (frm.doc.__onload && frm.doc.__onload.interview) {
				frm.add_custom_button(__("Interview"), function() {
					frappe.set_route("Form", "Interview", frm.doc.__onload.interview);
				});
			} else {
				frm.add_custom_button(__("Interview"), function() {
					frappe.route_options = {
						"job_applicant": frm.doc.name,
						"applicant_name": frm.doc.applicant_name,
						"job_opening": frm.doc.job_title,
					};
					frappe.new_doc("Interview");
				});
			}
		}

	},

	onload: function(frm){
		const default_company = frappe.defaults.get_default('company');
		frm.set_value('company', default_company);
		cur_frm.get_field("employee_education").grid.toggle_enable("employee", false);

	},
	governorate: function (frm){
		if (frm.doc.governorate){
			frm.set_value('city', null);
			frm.refresh_field('city');

		}
	},
	ar_fname: function(frm){
		if (frm.doc.ar_fname)
			frappe.call({
			method: "erpnext.hr.utils.validate_only_arabic",
			args: { "ar_field": frm.doc.ar_fname }
			});
		frm.trigger("update_applicant_name");
	},
	ar_sname: function(frm){
		if (frm.doc.ar_sname)	{
			frappe.call({
			method: "erpnext.hr.utils.validate_only_arabic",
			args: { "ar_field": frm.doc.ar_sname }
			});
		}
		frm.trigger("update_applicant_name");
	},
	ar_tname: function(frm){
		if (frm.doc.ar_tname)	{
			frappe.call({
			method: "erpnext.hr.utils.validate_only_arabic",
			args: { "ar_field": frm.doc.ar_tname }
			});
		}
		frm.trigger("update_applicant_name");
	},
	ar_family_name: function(frm){
		if (frm.doc.ar_family_name)	{
			frappe.call({
			method: "erpnext.hr.utils.validate_only_arabic",
			args: { "ar_field": frm.doc.ar_family_name }
			});
		}
		frm.trigger("update_applicant_name");
	},
	update_applicant_name:function(frm){
		ar_fname = frm.doc.ar_fname ? frm.doc.ar_fname: "";
		ar_sname = frm.doc.ar_sname ? frm.doc.ar_sname: "";
		ar_tname = frm.doc.ar_tname ? frm.doc.ar_tname: "";
		ar_family_name = frm.doc.ar_family_name ? frm.doc.ar_family_name: "";

 		employee_name =ar_fname;
 		if (employee_name.length > 0 &&  ar_sname.length >0 )
  		 		employee_name +=" ";
  		employee_name +=ar_sname;
  		if (employee_name.length > 0 &&  ar_tname.length >0 )
  		 		employee_name +=" ";
  		employee_name +=ar_tname;
  		if (employee_name.length > 0 &&  ar_family_name.length >0 )
  		 		employee_name +=" ";
  		employee_name +=ar_family_name;


		frm.set_value("applicant_name",employee_name)
	}
});


