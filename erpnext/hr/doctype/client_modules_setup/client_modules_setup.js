// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Client Modules Setup', {
	refresh: function(frm) {
	},
	onload:function(frm){
frm.save();
},
after_save:function(frm){
		frappe.call({
			method: "set_site",
			doc: frm.doc,
callback: function(r)
			{
			console.log("set_site");	
			}
		});
	}

});
