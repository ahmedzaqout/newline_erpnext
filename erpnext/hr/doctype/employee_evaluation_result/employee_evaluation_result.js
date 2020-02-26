// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Evaluation Result', {
	refresh: function(frm) {

	},
	setup: function(frm) {
		

		frm.set_query("evaluation_form", function() {
			return {
				filters: {
					"evaluation_type" : frm.doc.evaluation_type
				}
				
			}
		});
	

	},
	
	employee: function(frm){
		frappe.model.get_value('Employee Personal Detail', frm.doc.employee, ['employee_name'],function(r) {
				if (r) frm.set_value('employee_name', r.employee_name);
			});

		frappe.model.get_value('Employee Employment Detail', frm.doc.employee, ['designation','department','employment_type'],function(r) {
				if (r){
					 frm.set_value('department', r.department);
					 frm.set_value('designation', r.designation);
					}
			});
		//frm.set_value('start_date', '');
		
	},
	evaluation_form: function(frm){
		me = this;
			if (frm.doc.evaluation_form){
			frm.call({
					method: "erpnext.hr.doctype.employee_evaluation.employee_evaluation.get_form_items",
				args: {
					source_name: frm.doc.evaluation_form,
				
				},
				callback: function(r, rt) {
					if(r.message) {
						personal= r.message.personal;
						performance =r.message.performance ; 
						technical =r.message.technical ; 

						for(var i=0; i<personal.length; i++) {
						   var row = frappe.model.add_child(cur_frm.doc, "Staff Assessment Evaluation", "personal");
						   row.evaluation_item = personal[i]['evaluation_item'];
						}
						for(var i=0; i<performance.length; i++) {
						   var row = frappe.model.add_child(cur_frm.doc, "Staff Assessment Evaluation", "performance");
						   row.evaluation_item = performance[i]['evaluation_item'];
						}
						for(var i=0; i<technical.length; i++) {
						   var row = frappe.model.add_child(cur_frm.doc, "Staff Assessment Evaluation", "technical");
						   row.evaluation_item = technical[i]['evaluation_item'];
						}
					refresh_field("performance");
					// cur_frm.set_df_property("the_personal", "read_only", 0);
					// cur_frm.set_df_property("the_performance", "read_only", 0);
					// cur_frm.set_df_property("the_technical", "read_only", 0);
					refresh_field("technical");
					refresh_field("personal");

		// $('*[data-fieldname="personal"]').find('.grid-remove-row').hide();

		// $('*[data-fieldname="performance"]').find('.grid-remove-row').hide();

		// $('*[data-fieldname="technical"]').find('.grid-remove-row').hide();
						console.log(r.message);
					}
				}
			});

		}

	}
});
