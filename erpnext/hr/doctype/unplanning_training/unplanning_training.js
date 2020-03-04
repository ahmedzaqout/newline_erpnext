// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Unplanning Training', {
	refresh: function(frm) {

	}
});
frappe.ui.form.on("Training Budget", {
	cost: function(frm) {
		calculate_amount(frm);
	}
});

var calculate_amount = function(frm, cdt, cdn) {
	var tl = frm.doc.training_budget || [];
	var total_cost = 0;

	for(var i=0; i<tl.length; i++) {
		if (tl[i].cost) {
			total_cost += parseFloat(tl[i].cost);
		}
	}

	frm.set_value("total_budget", total_cost);
}