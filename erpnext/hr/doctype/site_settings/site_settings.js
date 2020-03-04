// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site Settings', {
	refresh: function(frm) {
	var btn_name = __("Add Site Permissions");
	if(frm.doc.client_modules_setup) btn_name = __("Edit Site Permissions");

	frm.add_custom_button( btn_name, function() {
		if(!frm.doc.client_modules_setup){
		 	frappe.new_doc("Client Modules Setup",{site: frm.doc.company_name});
		}
		else {
			frappe.set_route("Form", "Client Modules Setup",frm.doc.company_name);
		}
	});

	}
});
