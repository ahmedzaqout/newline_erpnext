// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

var emp_num= cur_frm.doc.employee;
frappe.ui.form.on('Employee Ending Service  Details', {
	setup: function(frm) {
		frm.page.set_secondary_action(__('Print'), () => {
			frm.print_doc()
		});
	},
	refresh: function(frm) {
		
		if (cur_frm.is_new() && !cur_frm.doc.employee){
			cur_frm.set_df_property('employee', 'read_only', 0);
			cur_frm.refresh_field('employee');
			}
		else if (cur_frm.doc.employee) {
			cur_frm.set_df_property('employee', 'read_only', 1);
			cur_frm.refresh_field('employee');
			}
	},
	relieving_date: function(frm){
	    	if (frm.doc.relieving_date)
			frappe.call({
				method:'update_emp_status',
				doc:frm.doc,
				args:{'status':'Left'}	
			});

	},

	user_data: function(frm) {
	    cur_frm.save() ; 
    	if ( !frm.doc.__unsaved)
		{
		var userid = emp_num;
		frappe.model.get_value('Employee Personal Detail', emp_num,'user_id',function(r) {
		if (r)  userid= r.user_id;});
		frappe.model.get_value('User', {employee:emp_num},'name',function(r) {
		if (r){
		frappe.set_route("Form", "User", r.name);
		}
		else 
		frappe.new_doc('User',{employee: emp_num});
		});
		}
	},
	personal_detail: function(frm) {
	    cur_frm.save() ; 
	    if ( !frm.doc.__unsaved)
		frappe.model.get_value('Employee Personal Detail', cur_frm.doc.employee,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Personal Detail", cur_frm.doc.employee);
		}
		else frappe.new_doc('Employee Personal Detail',{employee: cur_frm.doc.employee,employee_number: cur_frm.doc.employee});
		});
	},
	salary_detail: function(frm) {
	    cur_frm.save() ; 
	    if ( !frm.doc.__unsaved)
		frappe.model.get_value('Employee Salary Detail', cur_frm.doc.employee,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Salary Detail", cur_frm.doc.employee);
		}
		else 
		frappe.new_doc('Employee Salary Detail',{employee: cur_frm.doc.employee});
		});
	},
	employment_detail: function(frm) {
	    cur_frm.save() ; 
	    if ( !frm.doc.__unsaved)
		frappe.model.get_value('Employee Employment Detail', cur_frm.doc.employee,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Employment Detail",cur_frm.doc.employee);
		}
		else 
		frappe.new_doc('Employee Employment Detail',{employee: cur_frm.doc.employee});
		});
	},
	employee_data: function(frm) {
	    cur_frm.save() ; 
	    if ( !frm.doc.__unsaved)
		frappe.model.get_value('Employee Data', cur_frm.doc.employee,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Data",cur_frm.doc.employee);
		}
		else 
		frappe.new_doc('Employee Data',{employee: cur_frm.doc.employee});
		});
	},
	
	ending_service__details: function(frm) {
	    cur_frm.save() ; 
	    if ( !frm.doc.__unsaved)
		frappe.model.get_value('Employee Ending Service  Details', cur_frm.doc.employee,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Ending Service  Details",cur_frm.doc.employee);
		}
		else
		frappe.new_doc('Employee Ending Service  Details',{employee: cur_frm.doc.employee});
		});
	},

	back: function(frm) {
	    cur_frm.save() ; 
	    if ( !frm.doc.__unsaved)
		frappe.model.get_value('Employee Data', cur_frm.doc.employee,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Data",cur_frm.doc.employee);
		}
		else 
		frappe.new_doc('Employee Data',{employee: cur_frm.doc.employee});
		});
	   /* cur_frm.save() ; 
	    if ( !frm.doc.__unsaved)
		frappe.model.get_value('Employee Employment Detail', cur_frm.doc.employee,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Employment Detail",cur_frm.doc.employee);
		}
		else
		frappe.new_doc('Employee Employment Detail',{employee: cur_frm.doc.employee});
		});
*/
	},
});
