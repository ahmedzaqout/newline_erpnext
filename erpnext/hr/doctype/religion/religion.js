// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Religion', {
	refresh: function(frm) {

	},

religion_name:function(frm){	
		if (frm.doc.religion_name)
			frappe.call({
			method: "erpnext.hr.utils.validate_only_arabic",
			args: { "ar_field": frm.doc.religion_name }
			});

	},
religion_name_en:function(frm){	
		if (frm.doc.religion_name_en)
			frappe.call({
			method: "erpnext.hr.utils.validate_only_english",
			args: { "en_field": frm.doc.religion_name_en }
			});

	}
});
