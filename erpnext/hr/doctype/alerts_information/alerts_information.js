// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Alerts Information', {
	refresh: function(frm) {

	},
	alert_date:function() {
		if (alert_date > frappe.datetime.get_today())
			frappe.throw(__("Alert Date should not be in the Future dates"))
	},

});
