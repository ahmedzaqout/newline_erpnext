// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Allocate Shift Control Panel', {
	refresh: function(frm) {

	}
});
frappe.ui.form.on("Allocate Shift Control Panel", "refresh", function (frm) {
	frm.disable_save();
});

cur_frm.cscript.to_date = function (doc, cdt, cdn) {
	return $c('runserverobj', { 'method': 'to_date_validation', 'docs': doc },
		function (r, rt) {
			var doc = locals[cdt][cdn];
			if (r.message) {
				frappe.msgprint(__("To date cannot be before from date"));
				doc.to_date = '';
				refresh_field('to_date');
			}
		}
	);
}
