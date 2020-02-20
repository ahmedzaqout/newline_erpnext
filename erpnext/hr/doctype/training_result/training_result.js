// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Training Result', {
	refresh: function(frm) {
		frm.fields_dict['employee'].get_query = function(doc, cdt, cdn) {
			return {
				query: "erpnext.hr.doctype.training_result.training_result.get_employees",
				filters:{'training_event': frm.doc.training_event}
			}
		}
	},

	onload: function(frm) {
		//frm.trigger("training_event");
	//	frm.set_query("question", "training_evaluation_employee", function() {
	//		return {
	//			filters: {"parent": frm.doc.training_event}
	//			}
	//		});

		frm.fields_dict['training_evaluation_employee'].grid.get_field('question').get_query = function(doc, cdt, cdn) {
			child = locals[cdt][cdn];
			return{	
				filters:[
					['type', '=', 'Trainer'],
					['parent', '=', frm.doc.training_event]
					]
				}
			}

	},

	training_event: function(frm) {

		frm.trigger("get_questions");
	},
	get_questions: function(frm) { 
		frm.set_value("training_evaluation_employee" ,"");
		refresh_field("training_evaluation_employee");
		if (frm.doc.training_event) { 
			frappe.call({
				method: "erpnext.hr.doctype.training_result.training_result.get_questions",
				args: {
					"training_event": frm.doc.training_event
				},
				callback: function(r) {
					frm.set_value("training_evaluation_employee" ,"");
					if (r.message) { 
						$.each(r.message, function(i, d) { 
							var row = frappe.model.add_child(cur_frm.doc, "Training Evaluation Employee", "training_evaluation_employee");
							row.question = d.question;
						});
					}
					refresh_field("training_evaluation_employee");
				}
			});
		}
	},

	//training_event: function(frm) {
	//	if (frm.doc.training_event && !frm.doc.docstatus && !frm.doc.employees) { 
	//		frappe.call({
	//			method: "erpnext.hr.doctype.training_result.training_result.get_employees",
	//			args: {
	//				"training_event": frm.doc.training_event
	//			},
	//			callback: function(r) {
	//				frm.set_value("employees" ,"");
	//				if (r.message) {
	//					$.each(r.message, function(i, d) {
	//						var row = frappe.model.add_child(cur_frm.doc, "Training Result Employee", "employees");
	//						row.employee = d.employee;
	//						row.employee_name = d.employee_name;
	//					});
	//				}
	//				refresh_field("employees");
	//			}
	//		});
	//	}
//	}
});





frappe.ui.form.on("Training Evaluation Employee",  {

	question: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		var count =0;
		$.each(frm.doc["training_evaluation_employee"] || [], function(i, e) {
			if(d.question == e.question)
				count+= i;
		});
		if (count >=1) frappe.throw(__("Question existed"));
	},
	excellent: function(frm,cdt,cdn) {
		d = locals[cdt][cdn]; 
		if(d.excellent==1){
			d.very_good= 0; d.good= 0; d.fair= 0;	d.poor= 0;
			d.average =5;
			frm.refresh_fields();
			calculate_totals(frm.doc);

		}


	},
	very_good: function(frm,cdt,cdn) {
		d = locals[cdt][cdn];
		if(d.very_good==1){
			d.excellent= 0; d.good= 0; d.fair= 0;	d.poor= 0;
			d.average =4;
			frm.refresh_fields();
			calculate_totals(frm.doc);

		}

	},
	good: function(frm,cdt,cdn) {
		d = locals[cdt][cdn];
		if(d.good==1){
			d.excellent= 0; d.very_good= 0; d.fair= 0; d.poor= 0;
			d.average =3;
			frm.refresh_fields();
			calculate_totals(frm.doc);

		}

	},
	fair: function(frm,cdt,cdn) {
		d = locals[cdt][cdn];
		if(d.fair==1){
			d.excellent= 0; d.very_good= 0; d.good= 0;	d.poor= 0;
			d.average =2;
			frm.refresh_fields();
			calculate_totals(frm.doc);

		}

	},
	poor: function(frm,cdt,cdn) {
		d = locals[cdt][cdn];

		if(d.poor==1){
			d.excellent= 0; d.very_good= 0; d.good= 0;	d.fair= 0;
			d.average =1;
			frm.refresh_fields();
			calculate_totals(frm.doc);
		}
	}
});
var calculate_totals = function(doc) {
	var total_avg = 0.0; 
	doc.training_evaluation_employee.forEach(function(d) { total_avg += d.average;  });
	cur_frm.set_value("total", total_avg);
	refresh_field('total');
}

