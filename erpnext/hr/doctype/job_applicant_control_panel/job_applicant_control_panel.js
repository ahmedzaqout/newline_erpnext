// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.fields_dict['applicant_name'].get_query = function(doc, cdt, cdn) {
	return{
		filters:{"job_title":cur_frm.doc.job_opening}
	}
}
frappe.ui.form.on('Job Applicant Control Panel', {
	refresh: function(frm) {
		frm.disable_save();

	},
	message: function(frm){
		if (frm.doc.message){
		frm.set_value("characters_count",frm.doc.message.length)
		frm.refresh_field("characters_count")
}
}
});





