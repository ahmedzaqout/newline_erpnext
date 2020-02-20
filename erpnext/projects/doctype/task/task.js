// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.projects");


frappe.ui.form.on("Task", {
	subject:function(frm) {
		if (frm.doc.subject && frm.doc.project ){
			frm.set_value("s_name",frm.doc.subject + "-"+frm.doc.project);
}
	},
	project:function(frm) {
		if (frm.doc.subject && frm.doc.project ){
			frm.set_value("s_name",frm.doc.subject + "-"+frm.doc.project);
	}
				
			
	},

	onload: function(frm) {
		if (!"Project Manager" in frappe.user_roles)		
			frappe.throw(_("You dont have a permision."));
		frm.set_query("task", "depends_on", function() {
			var filters = {
				name: ["!=", frm.doc.name]
			};
			if(frm.doc.project) filters["project"] = frm.doc.project;
			return {
				filters: filters
			};
		})
	},
	

	refresh: function(frm) {
		frm.toggle_display('subject', frm.doc.__islocal);
	if (!"Project Manager" in frappe.user_roles)		
			frappe.throw(_("You dont have a permision."));
		
		if(!frm.is_group){
			var doc = frm.doc;
		

			if(!doc.__islocal) {
				if(frappe.model.can_read("Employee Task")) {
					frm.add_custom_button(__("Employee Task"), function() {
						frappe.set_route("List", "Employee Task");
					}, __("View"), true);
				}
			
			}
		}
		if(!doc.__islocal) {
			frm.add_custom_button(__("Merge Task"), function() {
				if( ! frm.doc.merge_task) {
		frappe.msgprint("Please specify the task you will merge with !!");
					
}else{

frappe.call({
		method: "erpnext.projects.doctype.task.task.merge",
		args:{
			"task": frm.doc.name,
			"merge_with":frm.doc.merge_task
		},
		callback: function(r) {
			if (r.message == true){
			frappe.msgprint("You merged The task successfully .")			
			}
		}
	})



}
					});
				
			
			}




cur_frm.fields_dict['task_details'].grid.get_field('employee').get_query = function(doc, cdt, cdn) {
			var d  = locals[cdt][cdn];console.log(cur_frm.doc.employee);
			return {
				query: "erpnext.projects.doctype.task.task.get_employee",
				filters: { 'project': cur_frm.doc.project }
			}

		}
frm.fields_dict.merge_task.get_query = function() {
			return {
				query: "erpnext.projects.doctype.task.task.get_merge_task",
				filters: { 'project': cur_frm.doc.project }
			}
		};


	},

	setup: function(frm) {
		frm.fields_dict.project.get_query = function() {
			return {
				query: "erpnext.projects.doctype.task.task.get_projects"
			}
		
		};

	},


	is_group: function(frm) {
		frappe.call({
			method:"erpnext.projects.doctype.task.task.check_if_child_exists",
			args: {
				name: frm.doc.name
			},
			callback: function(r){
				if(r.message){
					frappe.msgprint(__('Cannot convert it to non-group. Child Tasks exist.'));
					frm.reload_doc();
				}
			}
		})
	},

	
	validate: function(frm) {
		frm.doc.project && frappe.model.remove_from_locals("Project",
			frm.doc.project);
	},
	

});

frappe.ui.form.on("Task Details", {
	expected_time_in_hours: function(frm, cdt, cdn) {
		console.log();
		calculate_time_and_amount(frm, cdt, cdn)
	},
});

var calculate_time_and_amount = function(frm, cdt, cdn) {
	var tl = frm.doc.task_details || [];
	var total_working_hr = 0;

	for(var i=0; i<tl.length; i++) {
		if (tl[i].expected_time_in_hours) {
			total_working_hr += parseFloat(tl[i].expected_time_in_hours);
			console.log(total_working_hr);
		}
	}

	console.log("ss");
	frm.set_value("time_expected", total_working_hr);



}

