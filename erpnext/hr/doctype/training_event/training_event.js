// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Training Event', {
	onload_post_render: function(frm) {
		frm.get_field("employees").grid.set_multiple_add("employee");
	},
	refresh: function(frm) {
		if(!frm.doc.__islocal) {
			frm.add_custom_button(__("Training Result"), function() {
				frappe.route_options = {
					training_event: frm.doc.name
				}
				frappe.set_route("List", "Training Result");
			});
			frm.add_custom_button(__("Training Feedback"), function() {
				frappe.route_options = {
					training_event: frm.doc.name
				}
				frappe.set_route("List", "Training Feedback");
			});
		}
	},
	training_program: function(frm) {
		frappe.call({ 
			method:'get_trainers',
			doc: frm.doc,
			callback: function(r) {
			   if (r.message) { 
				frm.set_value("trainer_name" ,"");
				$.each(r.message, function(i, d) {
					var child = frappe.model.add_child(frm.doc, "Trainer", "trainer_name");
					child.trainer_name   = r.message[i].trainer_name;
					child.trainer_email  = r.message[i].trainer_email;
					child.contact_number = r.message[i].contact_number;
					});
				}
			} 	
		});
		refresh_field("trainer_name");

		frappe.call({ 
			method:'get_trainees',
			doc: frm.doc,
			callback: function(res) {
			   if (res.message) { 
				frm.set_value("employees" ,"");
				$.each(res.message, function(j, dd) {
					var row = frappe.model.add_child(frm.doc, "Training Event Employee", "employees");
					row.employee   = res.message[j].employee;
					});
				}
			} 	
		});
		refresh_field("employees");


	}
});

frappe.ui.form.on('Training Evaluation', {
	'question': function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		var count =0;
		$.each(frm.doc["training_evaluation"] || [], function(i, e) {
			if(d.question == e.question)
				count+= i;
		});
		if (count >=1) frappe.throw(__("Question existed"));
	}

});

frappe.ui.form.on('Training Event Employee', {
	'employee': function(frm,  cdt, cdn) { 
		var d = locals[cdt][cdn]; 
		var count =0;
		frappe.model.get_value('Employee', d.employee, ['employee_name'],function(r) {
			if (r)	d.employee_name= r.employee_name; 
		});
		//validate on trainners if existed in programm
		frappe.call({ 
			method:'validate_trainees',
			doc: frm.doc,
			args:{'employee':d.employee_name},
			callback: function(r) {
				if (r.message == true) frappe.throw(__("Employee does not existed in this training program"));
			}
   		  });

		$.each(frm.doc["employees"] || [], function(i, e) { 
			if(d.employee == e.employee)
				count+= 1; //cur_frm.get_field("employees").grid.grid_rows[i].remove();

		}); 
		if  (count >1)	frappe.throw(__("Employee existed")); 

	
	}
});










