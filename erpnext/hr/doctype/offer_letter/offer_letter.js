// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.offer_letter");

frappe.ui.form.on("Offer Letter", {
	select_terms: function (frm) {
		erpnext.utils.get_terms(frm.doc.select_terms, frm.doc, function (r) {
			if (!r.exc) {
				frm.set_value("terms", r.message);
			}
		});
	},

	refresh: function (frm) {
		const default_company = frappe.defaults.get_default('company');
		frm.set_value('company', default_company);
		//cur_frm.add_fetch("applicant_name", "job_opening", "job_title")
		//cur_frm.add_fetch("job_opening", "designation", "designation")
		if ((!frm.doc.__islocal) && (frm.doc.status == 'Accepted') && (frm.doc.docstatus === 3)) {
			frm.add_custom_button(__('Make Employee'),
				function () {
					//frappe.call({
					//	method: "make_employee",
					//	doc: frm.doc	
					//});
					erpnext.offer_letter.make_employee(frm)
				}
			);
		}
	},
	job_applicant:function(frm){
	    if(frm.doc.job_applicant)
		frappe.call({
			method: "erpnext.hr.get_applicant_data",
			args:{"job_applicant":frm.doc.job_applicant},
			callback: function(r) { 
			     if(r.message){
				frm.set_value("designation", r.message[0].designation);
				frm.set_value("job_number", r.message[0].job_number);
				frm.set_value("job_opening", r.message[1].job_title);
				frm.set_value("work_place", r.message[1].work_place);
				frm.set_value("department", r.message[1].department);



				}
			}
		});
	}

});

erpnext.offer_letter.make_employee = function (frm) {
	frappe.model.open_mapped_doc({
		method: "erpnext.hr.doctype.offer_letter.offer_letter.make_employee",
		frm: frm
	});
};
