// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Earnings Classification', {
	refresh: function(frm) { 
		$.each(frm.doc["designation"], function(i, designation) {
			designation.category = __(designation.category) ;
			frm.refresh_field('designation');
		});
	}
});

frappe.ui.form.on("Earnings Detail","degree", function(frm) {
		if(frm.doc.category){
			frappe.model.set_value(frm.doctype,frm.docname,'category', __(frm.doc.category));
			frm.refresh_field('designation');
		}
	
});
