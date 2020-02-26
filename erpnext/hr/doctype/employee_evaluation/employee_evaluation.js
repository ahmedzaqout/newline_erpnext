// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Evaluation', {
	onload: function(frm){
		hideTheButtonWrapper = $('*[data-fieldname="personal"]');
		hideTheButtonWrapper.find('.grid-remove-row').hide();
		hideTheButtonWrapper.find('.grid-add-row').hide();


		hideTheButtonWrapper2 = $('*[data-fieldname="performance"]');
		hideTheButtonWrapper2.find('.grid-remove-row').hide();
		hideTheButtonWrapper2.find('.grid-add-row').hide();

		hideTheButtonWrapper3 = $('*[data-fieldname="technical"]');
		hideTheButtonWrapper3.find('.grid-remove-row').hide();
		hideTheButtonWrapper3.find('.grid-add-row').hide();
		$(".grid-remove-row").each(function(i, obj) {
    		this.hide();
		});
			cur_frm.fields_dict.employee.get_query = function(doc,cdt,cdn) {
	return{
				query: "erpnext.hr.doctype.employee_evaluation.employee_evaluation.get_employees"			}
		}

	},
	refresh: function(frm) {

		$('*[data-fieldname="personal"]').find('.grid-remove-row').hide();

		$('*[data-fieldname="performance"]').find('.grid-remove-row').hide();

		$('*[data-fieldname="technical"]').find('.grid-remove-row').hide();
	},
	setup: function(frm) {
		
	

	},
	
	employee: function(frm){
		var me =frm;
		frappe.model.get_value('Employee Personal Detail', frm.doc.employee, ['employee_name'],function(r) {
				if (r) frm.set_value('employee_name', r.employee_name);
			});

		frappe.model.get_value('Employee Employment Detail', frm.doc.employee, ['designation','department','employment_type'],function(r) {
				if (r){
					 frm.set_value('department', r.department);
					 frm.set_value('designation', r.designation);
					}
			});
		frappe.call({
			        method: "frappe.client.get_list",
			        args: {
			            doctype: "Evaluators",
			            filters: {"employee" : me.doc.employee},
			            fields : ['evaluation_form']
			        },
			        callback(r) {
			        	if(r.message){
			        			me.doc.evaluation_form =r.message[0].evaluation_form;

					        	me.refresh_fields(["evaluation_form"]);
		if (me.doc.evaluation_form){

			frappe.call({
					method: "erpnext.hr.doctype.employee_evaluation.employee_evaluation.get_form_items",
				args: {
					source_name: me.doc.evaluation_form,
				
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
			        

			        }

			    });
		//frm.set_value('start_date', '');
		
	},
	
	evaluation_form: function(frm){
		me = this;
		if (frm.doc.evaluation_form){
			frm.doc.personal=[];
			frm.doc.performance=[];
			frm.doc.technical=[];

			frappe.call({
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
frappe.ui.form.on('Evaluation Element', {
	rate: function(frm, dt, dn) {
		if(frm.doc.docstatus < 1){
		var doc = locals[dt][dn]; 
		var total=0;
		var count=0;
			$.each(frm.doc["personal"] || [], function(i, timesheet) {
				va= 0;
				if (timesheet.rate)
					va =parseFloat(timesheet.rate)
				total +=va;
				count+=1;
			});
			$.each(frm.doc["performance"] || [], function(i, timesheet) {
				va= 0;
				if (timesheet.rate)
					va =parseFloat(timesheet.rate)
				total +=va;
				count+=1;
			});
			$.each(frm.doc["technical"] || [], function(i, timesheet) {
				va= 0;
				if (timesheet.rate)
					va =parseFloat(timesheet.rate)
				total +=va;
				count+=1;
			});
			frm.doc.total = (total) ;
			frm.refresh_field('total');
}
	}
	});

cur_frm.fields_dict.employee.get_query = function(doc,cdt,cdn) {
	return{
				query: "erpnext.hr.doctype.employee_evaluation.employee_evaluation.get_employees"			}
		}
