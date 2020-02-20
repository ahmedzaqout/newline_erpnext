// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.ui.form.on('Companies Control Panel', {
	onload:function(frm){

	},
	projects_module:function(frm){
		frappe.call({
			method: "erpnext.hr.update_module_roles",
			args: {'projects_module':frm.doc.projects_module},
			callback: function(r){}
		});
	},
	
	refresh: function(frm) {
		hideTheButtonWrapper = $('*[data-fieldname="company_branch"]');
		hideTheButtonWrapper.find('.grid-add-row').hide();
		//frm.disable_save();
	},

	branches_number:function(frm) {
	 	var branches = frm.doc.branches_number;
	        var curr_len = frm.doc.company_branch.length;
		var changes =  branches - curr_len;
		if(changes > 0){
		for(var i=0; i< changes; i++) {
		   var row = frappe.model.add_child(frm.doc, "Company Branch", "company_branch");
		   refresh_field("company_branch");
		}
		}
		else {
		changes = -(changes);
		for(var i=0; i< changes; i++) {
		   var row = frappe.model.delete_child(frm.doc, "Company Branch", "company_branch");
		   refresh_field("company_branch");
		}
		}
},

send:function(frm){
		frappe.call({
			method: "create_new_site",
			doc: frm.doc,
			callback: function(r)
			{
				
			}
		});
	}

});
