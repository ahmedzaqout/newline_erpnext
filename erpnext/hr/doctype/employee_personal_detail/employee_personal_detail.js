// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.provide("erpnext.hr");
frappe.ui.form.on('Employee Personal Detail', {
	setup: function(frm) {
		frm.page.set_secondary_action(__('Print'), () => {
			frm.print_doc()
		});
	},
	refresh: function() {
		var me = this;
			if (cur_frm.doc.company != "Danaf"){
							cur_frm.set_df_property("en_fname", "reqd", true);
							cur_frm.set_df_property("en_sname", "reqd", true);
							cur_frm.set_df_property("en_tname", "reqd", true);
							cur_frm.set_df_property("en_family_name", "reqd", true);

			}

		if (cur_frm.is_new() && !cur_frm.doc.employee){
			cur_frm.set_df_property('employee', 'read_only', 0);
			cur_frm.refresh_field('employee');
			}
		else if (cur_frm.doc.employee) {
			cur_frm.set_df_property('employee', 'read_only', 1);
			cur_frm.refresh_field('employee');
			}
		//erpnext.toggle_naming_series();
		
	//if (cur_frm.is_new()){
	//	frappe.call({
	//		method: "erpnext.hr.doctype.employee.employee.auto_generate_emp",
	//		callback: function(r)
	//		{console.log(r.message)
	//			if(r.message)
	//				cur_frm.set_value("employee_number", r.message)
	//		}
	//	});}


        cur_frm.fields_dict.city.get_query = function(doc) {
            return {
                filters: {
                    "governorate": cur_frm.doc.governorate
                }
            }
        } 

	
	},


	date_of_birth: function(frm) {
		return cur_frm.call({
			method: "get_retirement_date",
			args: {date_of_birth: cur_frm.doc.date_of_birth}
		});
	},
	governorate:function(frm) {
		frm.set_value('city','');
		frm.refresh_field('city')
	},

	salutation: function(frm) {
		if(this.frm.doc.salutation) {
			this.frm.set_value("gender", {
				"Mr": "Male",
				"Ms": "Female"
			}[this.frm.doc.salutation]);
		}
	},

	validate: function(frm) {
	    if(frm.doc.marital_status == 'Married')
		cur_frm.call({
			method: "add_depenents_bonus",
			args: {"sal_comp": 'Bonus Wife', "employee": frm.doc.employee}
		});
	},
	ar_fname:function(frm){	
		if (frm.doc.ar_fname)
			frappe.call({
			method: "erpnext.hr.utils.validate_only_arabic",
			args: { "ar_field": frm.doc.ar_fname }
			});

		frm.trigger("update_employee_name");
	},
	ar_sname:function(frm){
		if (frm.doc.ar_sname)	{
			frappe.call({
			method: "erpnext.hr.utils.validate_only_arabic",
			args: { "ar_field": frm.doc.ar_sname }
			});
		}	

		frm.trigger("update_employee_name");

	},
	ar_tname:function(frm){
		if (frm.doc.ar_tname)	{
			frappe.call({
			method: "erpnext.hr.utils.validate_only_arabic",
			args: { "ar_field": frm.doc.ar_tname }
			});
		}		

		frm.trigger("update_employee_name");
	},
	ar_family_name:function(frm){
		if (frm.doc.ar_family_name)	{
			frappe.call({
			method: "erpnext.hr.utils.validate_only_arabic",
			args: { "ar_field": frm.doc.ar_family_name }
			});
		}	
		frm.trigger("update_employee_name");
	},
	en_fname:function(frm){	
		if (frm.doc.en_fname)
			frappe.call({
			method: "erpnext.hr.utils.validate_only_english",
			args: { "en_field": frm.doc.en_fname }
			});
	},
	en_sname:function(frm){
		if (frm.doc.en_sname)	{
			frappe.call({
			method: "erpnext.hr.utils.validate_only_english",
			args: { "en_field": frm.doc.en_sname }
			});
		}	

	},
	en_tname:function(frm){
		if (frm.doc.en_tname)	{
			frappe.call({
			method: "erpnext.hr.utils.validate_only_english",
			args: { "en_field": frm.doc.en_tname }
			});
		}		

	},
	en_family_name:function(frm){
		if (frm.doc.en_family_name)	{
			frappe.call({
			method: "erpnext.hr.utils.validate_only_english",
			args: { "en_field": frm.doc.en_family_name }
			});
		}	

	},

	update_employee_name:function(frm){
		ar_fname = frm.doc.ar_fname ? frm.doc.ar_fname: " ";
		ar_sname = frm.doc.ar_sname ? frm.doc.ar_sname: " ";
		ar_tname = frm.doc.ar_tname ? frm.doc.ar_tname: " ";
		ar_family_name = frm.doc.ar_family_name ? frm.doc.ar_family_name: " ";

 		employee_name =ar_fname+" "+ar_sname+" "+ar_tname+" "+ar_family_name;
		frm.set_value("employee_name",employee_name)
	},

	user_data: function(frm) {
	    //cur_frm.save() ; 
	    if (!frm.doc.__unsaved)
		{
		var userid = cur_frm.doc.employee_number;
		//frappe.model.get_value('Employee Personal Detail', cur_frm.doc.employee_number,'user_id',function(r) {
		//if (r)  userid= r.user_id;});
 		//frappe.model.get_value('Employee Personal Detail', cur_frm.doc.employee,'user_id',function(r) {
		frappe.model.get_value('User',{employee:cur_frm.doc.employee_number},'name',function(r) {
		if (r){ 
		//frappe.route_options = {'first_name' :cur_frm.doc.ar_fname,'last_name':cur_frm.doc.ar_family_name}
		frappe.set_route("Form", "User", r.name , {'first_name' :frm.doc.ar_fname});
		}
		else 
		frappe.new_doc('User',{employee: cur_frm.doc.employee_number,first_name :cur_frm.doc.ar_fname,full_name:cur_frm.doc.ar_family_name,last_name:cur_frm.doc.ar_family_name});
		});
		}
	},
	personal_detail: function(frm) {
	    //cur_frm.save() ; 
	    if ( !frm.doc.__unsaved)
		frappe.model.get_value('Employee Personal Detail', cur_frm.doc.employee,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Personal Detail", cur_frm.doc.employee);
		}
		else frappe.new_doc('Employee Personal Detail',{employee: cur_frm.doc.employee,employee_number: cur_frm.doc.employee});
		});
	},
	salary_detail: function(frm) {
	    //cur_frm.save() ; 
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
	   // cur_frm.save() ; 
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
	   // cur_frm.save() ; 
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
	   // cur_frm.save() ; 
	    if ( !frm.doc.__unsaved)
		frappe.model.get_value('Employee Ending Service  Details', cur_frm.doc.employee,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Ending Service  Details",cur_frm.doc.employee);
		}
		else
		frappe.new_doc('Employee Ending Service  Details',{employee: cur_frm.doc.employee});
		});
	},

	next: function(frm) {//erpnext.utils.validate_mandatory(frm);
	   // cur_frm.save() ; 
	    if ( !frm.doc.__unsaved)
		frappe.model.get_value('User',{employee:cur_frm.doc.employee_number},'name',function(r) {
		if (r) {
		frappe.set_route("Form", "User", r.name);
		}
		else 
		frappe.new_doc('User',{employee: cur_frm.doc.employee_number,first_name :cur_frm.doc.ar_fname,full_name:cur_frm.doc.ar_family_name,last_name:cur_frm.doc.ar_family_name});
		

		/*if (r) {
		frappe.set_route("Form", "Employee Salary Detail",cur_frm.doc.employee);
		}
		else
		frappe.new_doc('Employee Salary Detail',{employee: cur_frm.doc.employee});
*/
		});

	},
	back: function(frm) {
	   // cur_frm.save() ; 
	    if ( !frm.doc.__unsaved)
		frappe.model.get_value('Employee Personal Detail', cur_frm.doc.employee,'user_id',function(r) {
		/*if (r) {
		frappe.set_route("Form", "User", r.user_id);
		}
		else 
		frappe.new_doc('User');
*/
		});

	},
	create_user: function(frm) {
		if (!frm.doc.user_id)
		{
			frappe.throw(__("Please enter Your Email"))
		}
		//if (!cur_frm.doc.employee)
		//	return ''
		frappe.call({
			method: "erpnext.hr.doctype.employee.employee.create_user",
			args: { 
				user:frm.doc.user_id,
				employee: cur_frm.doc.employee },
			callback: function(r)
			{
				frm.set_value("user_id", r.message)
			}
		});
	},




});
