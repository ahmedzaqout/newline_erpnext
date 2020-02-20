// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


cur_frm.add_fetch('employee', 'employee_name', 'employee_name');
cur_frm.fields_dict['time_logs'].grid.get_field('task').new_doc = function(doc, cdt, cdn){
console.log("Triggered");
	
}
;




frappe.ui.form.on('Employee Task', {
	setup: function(frm) {
		frm.fields_dict.employee.get_query = function() {
			return {
				filters:{
					'status': 'Active'
				}
			}
		}


				
			

		//frm.fields_dict['time_logs'].grid.get_field('task').get_query = function(frm, cdt, cdn) {
		//	var child = locals[cdt][cdn]; 

		//}

	},

	onload: function(frm){
		if (frm.doc.__islocal && frm.doc.time_logs) {
			calculate_time_and_amount(frm);
		}
		

	},

	refresh: function(frm) {
if(! frm.doc.__islocal) {
cur_frm.fields_dict["time_logs"].grid.docfields[3].hidden=1;
refresh_field("time_logs");

		}

		cur_frm.fields_dict['time_logs'].grid.get_field('task').get_query = function(doc, cdt, cdn) {
			var d  = locals[cdt][cdn];
			return {
				query: "erpnext.projects.doctype.employee_task.employee_task.task_query",
				filters: { 'project': d.project , 'employee': cur_frm.doc.employee }
			}
		}



cur_frm.fields_dict['time_logs'].grid.get_field('specialization').get_query = function(doc, cdt, cdn) {
		var d  = locals[cdt][cdn];
		return {					

		query:"erpnext.projects.doctype.employee_task.employee_task.get_specialization",
		filters: { 'project': d.project , 'employee': cur_frm.doc.employee }
			}
		}



		cur_frm.fields_dict['time_logs'].grid.get_field('project').get_query = function(doc, cdt, cdn) {
			var d  = locals[cdt][cdn];console.log(cur_frm.doc.employee);
			return {
				query: "erpnext.projects.doctype.employee_task.employee_task.emp_project_query",
				filters: { 'employee': cur_frm.doc.employee }
			}
		}
		
	},
	total_hours:function(frm){
	if (frm.doc.total_hours < 7)
		frm.set_df_property("reson_for_less_than_7_hours", "reqd", true)
	else{
		frm.set_df_property("reson_for_less_than_7_hours", "reqd", false)


}

}
})




frappe.ui.form.on("Activity Detail", {
	time_logs_remove: function(frm) {
		calculate_time_and_amount(frm);
	},

	hourss: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		
	if(! /[0-9]*/.test(""+child.hourss))
		{
			frappe.msgprint("Please type english number");
		}
		var hours=0;
		var hour=0;
		var totall=0;
		if (child.hourss){
			hours=child.hourss
			console.log(""+hours);

		}
		if (child.minutes){
			 hour= parseFloat(child.minutes) /60.0;
}
		totall=hours + hour;
		frappe.model.set_value(cdt, cdn, "hours",""+totall);
		refresh_field("time_logs");
		calculate_time_and_amount(frm, cdt, cdn)

	},

	minutes: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		var hours=0;
		var hour=0;
		var totall=0;
		if(! /[0-9]*/.test(""+child.minutes))
		{
			frappe.msgprint("Please type english number");
		}
		if (child.hourss > 0){
			hours=child.hourss;}
		if (child.minutes > 0 ){
			 hour= parseFloat(child.minutes) /60.0;
		
		}	
		
			if(! /[0-9]*/.test(""+hour))
		{
			frappe.msgprint("Please type english number");
		}
		totall=hours + hour;
		frappe.model.set_value(cdt, cdn, "hours",""+totall);
		refresh_field("time_logs");
		calculate_time_and_amount(frm, cdt, cdn)

	},

	hours: function(frm, cdt, cdn) {
		calculate_time_and_amount(frm, cdt, cdn)
	},

	project : function (frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		var ee=frappe.model.get_value("Project", child.project, "task_mandatory")
		if (child.project){
		frappe.call({
			method:"erpnext.projects.doctype.employee_task.employee_task.check_mand",
			args: {
				project: child.project,
				employee:cur_frm.doc.employee
			},
			callback: function(r){
console.log(r.message[0][0]);
if(r.message.length == 1){
console.log(r.message)	;
child.specialization=r.message[0][0];

cur_frm.fields_dict["time_logs"].grid.grid_rows[(child.idx-1)].docfields[3].hidden=1;
 frm.refresh_field("time_logs");

					
			}
else{
cur_frm.fields_dict["time_logs"].grid.grid_rows[(child.idx-1)].docfields[3].hidden=0;
 frm.refresh_field("time_logs");
}

	}

});
}

	},


});


var calculate_end_time = function(frm, cdt, cdn) {
	let child = locals[cdt][cdn];

	if(!child.from_time) {
		// if from_time value is not available then set the current datetime
           frappe.model.set_value(cdt, cdn, "from_time", frappe.datetime.get_datetime_as_string());
	}
	let d = moment(child.from_time);
	if(child.hours) {
		d.add(child.hours, "hours");
		frm._setting_hours = true;
	}
}


var calculate_time_and_amount = function(frm, cdt, cdn) {
	var tl = frm.doc.time_logs || [];
	var total_working_hr = 0;

	for(var i=0; i<tl.length; i++) {
		if (tl[i].hours) {
			total_working_hr += parseFloat(tl[i].hours);
		}
	}

	frm.set_value("total_hours", total_working_hr);
}





