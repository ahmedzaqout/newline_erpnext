// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

var emp_num= cur_frm.doc.employee;
frappe.ui.form.on('Employee Employment Detail', {
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
		frm.set_value('sub_dep', 'Department');

        cur_frm.fields_dict.management.get_query = function(doc) {
            return {
                filters: {
                    "parent_management": cur_frm.doc.branch
                }
            }
        } 
        cur_frm.fields_dict.circle.get_query = function(doc) {
            return {
                filters: {
                    "parent_circle": cur_frm.doc.management
                }
            }
        } 
        cur_frm.fields_dict.department.get_query = function(doc) {
            return {
                filters: {
                    "parent_department": cur_frm.doc.circle
                }
            }
        } 


        cur_frm.fields_dict.sub_dep.get_query = function(doc) {
            return {
                filters: {"name": ["in", ["Department", "Sub Department", "Sub Association"]]}
            }
        } 

	},

	employment_type: function(frm) {
		frappe.model.get_value('Employment Type', frm.doc.employment_type,['work_shift','holiday_list'],function(r) {
		    if(r){
			frm.set_value("work_shift", r.work_shift);
			frm.set_value("holiday_list", r.holiday_list);
			}
		});
	},
	user_data: function(frm) {
	    if (in_list(frappe.user_roles, "HR Manager")) cur_frm.save() ; 
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
	    if (in_list(frappe.user_roles, "HR Manager")) cur_frm.save() ; 
	    if ( !frm.doc.__unsaved)
		frappe.model.get_value('Employee Personal Detail', cur_frm.doc.employee,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Personal Detail", cur_frm.doc.employee);
		}
		else frappe.new_doc('Employee Personal Detail',{employee: cur_frm.doc.employee,employee_number: cur_frm.doc.employee});
		});
	},
	salary_detail: function(frm) {
	    if (in_list(frappe.user_roles, "HR Manager")) cur_frm.save() ; 
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
	    if (in_list(frappe.user_roles, "HR Manager")) cur_frm.save() ; 
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
	    if (in_list(frappe.user_roles, "HR Manager")) cur_frm.save() ; 
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
	    if (in_list(frappe.user_roles, "HR Manager")) cur_frm.save() ; 
	    if ( !frm.doc.__unsaved)
		frappe.model.get_value('Employee Ending Service  Details', cur_frm.doc.employee,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Ending Service  Details",cur_frm.doc.employee);
		}
		else
		frappe.new_doc('Employee Ending Service  Details',{employee: cur_frm.doc.employee});
		});
	},
	next: function(frm) {
	    if (in_list(frappe.user_roles, "HR Manager")) cur_frm.save() ; 
	    if ( !frm.doc.__unsaved)
		frappe.model.get_value('Employee Salary Detail', cur_frm.doc.employee,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Salary Detail",cur_frm.doc.employee);
		}
		else
		frappe.new_doc('Employee Salary Detail',{employee: cur_frm.doc.employee});
		});
	},
	back: function(frm) {
	
if (in_list(frappe.user_roles, "HR Manager")) cur_frm.save() ; 
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
	    /*if (in_list(frappe.user_roles, "HR Manager")) cur_frm.save() ; 
	    if ( !frm.doc.__unsaved)
		frappe.model.get_value('Employee Personal Detail', cur_frm.doc.employee,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Personal Detail",cur_frm.doc.employee);
		}
		else
		frappe.new_doc('Employee Personal Detail',{employee: cur_frm.doc.employee});
		});
*/
	}, 
	contract_end_date: function(frm) {
		frappe.call({
			method: "update_end_serv",
			doc: frm.doc });
	},
	supervisor: function(frm) {
		frappe.call({
			method: "add_manager_staff",
			doc: frm.doc,
			callback: function(r)
			{
				//console.log(r);
			}
		});
	},
	branch: function(frm) {
		if(frm.doc.branch)
		  {
		frm.set_value("work_place_change_date", frappe.datetime.get_today()) ;
		frm.set_value("management", "") ;
		frm.set_value("department", "") ;
		frm.set_value("circle", "") ;
		 
		   
	  }
	},
	management: function(frm) {
		if(frm.doc.management)
		  {
		frm.set_value("work_place_change_date", frappe.datetime.get_today()) ;
		frm.set_value("department", "") ;
		frm.set_value("circle", "") ;
		   
	  }
	},
	department: function(frm) {
		if(frm.doc.department)
		  {
		frm.set_value("work_place_change_date", frappe.datetime.get_today()) ;
		 
		   
	  }
	},
	circle: function(frm) {
		if(frm.doc.circle)
		  {
		frm.set_value("work_place_change_date", frappe.datetime.get_today()) ;
		frm.set_value("department", "") ;

	  }
	},

	work_shift: function(frm) {
		if(frm.doc.work_shift)
		  {
		frm.set_value("shift_change_date", frappe.datetime.get_today()) ;
		   /* frappe.call({
			method: "erpnext.hr.clear_employee_holidays",
			args: {"employee":frm.doc.employee,"shift_change_date":frm.doc.shift_change_date} 
			});
		    frappe.call({
			method: "erpnext.hr.doctype.attendance.attendance.update_holiday",
			args: {"employee":frm.doc.employee,"holiday_list": frm.doc.holiday_list,"shift_change_date":frm.doc.shift_change_date} 
			});
			*/
		    if (!frm.doc.shift_change_date)
			frappe.throw(__("Shift Change Date must be selected"))
		}
		if (!frm.doc.private_work_shift){
			var days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
		    frappe.model.get_value('Work Shift Details', {'parent': frm.doc.work_shift,'day':days[new Date().getDay()]}, ['start_work','end_work'],function(r) {
		if(r){
			frm.set_value("start_work", r.start_work)
			frm.set_value("end_work", r.end_work)

			frappe.call({
			method: "erpnext.assets.doctype.asset_repair.asset_repair.get_downtime",
			args: { 
				"failure_date":r.start_work,
				"completion_date":r.end_work },
			callback: function(r)
			{
				frm.set_value("total_work_hrs", r.message)
			}
		});}
  		})
	  }
	},
	private_work_shift: function(frm) {
		frappe.model.get_value('Private Work Shift Details', {'parent': frm.doc.private_work_shift}, ['start_work','end_work'],function(r) {			if(r){
			frm.set_value("start_work", r.start_work)
			frm.set_value("end_work", r.end_work)

			frappe.call({
			method: "erpnext.assets.doctype.asset_repair.asset_repair.get_downtime",
			args: { 
				"failure_date":r.start_work,
				"completion_date":r.end_work },
			callback: function(r)
			{
				frm.set_value("total_work_hrs", r.message)
			}
		});}
  		})
		
	},
});
