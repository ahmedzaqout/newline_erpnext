// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Evaluation Form', {
	refresh: function(frm) {

	},
	setup: function(frm) {
		
		frm.set_query("evaluation_item", "personal", function() {
			return {
				filters: {
					item_type: "Personal"

				}
			}
		})
		frm.set_query("evaluation_item", "performance", function() {
			return {
				filters: {
					item_type: "Performance"

				}
			}
		})
		frm.set_query("evaluation_item", "technical", function() {
			return {
				filters: {
					item_type: "Administrative / Technical"

				}
			}
		})
		

		

	},

});
