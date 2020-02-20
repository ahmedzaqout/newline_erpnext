// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
var ar_fname="";var ar_sname="";var ar_tname="";var ar_family_name="";
var user_email="";

frappe.provide("erpnext.hr");

erpnext.hr.EmployeeController = frappe.ui.form.Controller.extend({
        setup: function() {
		
		this.frm.fields_dict.user_id.get_query = function(doc, cdt, cdn) {
			return {
				query: "frappe.core.doctype.user.user.user_query",
				filters: {ignore_user_type: 1}
			}
		}
		this.frm.fields_dict.reports_to.get_query = function(doc, cdt, cdn) {
			return { query: "erpnext.controllers.queries.employee_query"} }

		
	},

	onload: function() {
		
		this.frm.set_query("leave_approver", "leave_approvers", function(doc) {
			return {
				query:"erpnext.hr.doctype.employee_leave_approver.employee_leave_approver.get_approvers",
				filters:{
					user: doc.user_id
				}
			}
		});



////////////////////////////


        this.frm.fields_dict.bank_branch.get_query = function(doc) {
            return {
                filters: {
                    "bank": doc.bank_name
                }
            }
        } 
        this.frm.fields_dict.management.get_query = function(doc) {
            return {
                filters: {
                    "branch": doc.branch
                }
            }
        } 
        this.frm.fields_dict.circle.get_query = function(doc) {
            return {
                filters: {
                    "parent_circle": doc.management
                }
            }
        } 
        this.frm.fields_dict.department.get_query = function(doc) {
            return {
                filters: {
                    "circle": doc.circle
                }
            }
        } 

        this.frm.fields_dict.city.get_query = function(doc) {
            return {
                filters: {
                    "governorate": doc.governorate
                }
            }
        } 

        this.frm.fields_dict.sub_dep.get_query = function(doc) {
            return {
                filters: {"name": ["in", ["Department", "Sub Department", "Sub Association"]]}
            }
        } 

////////////////////////////
	},

	refresh: function() {

		var me = this;
		cur_frm.set_df_property("employee", "hidden",1);
			cur_frm.toggle_display("employee_number", true);
		erpnext.toggle_naming_series();
		frappe.db.get_value("HR Settings", {name: 'HR Settings'},"auto_generate_employee_no",function(r) { 
			if (r && cur_frm.is_new())  {
			cur_frm.set_df_property("employee", "hidden",0);
			cur_frm.toggle_display("employee_number", false);
			cur_frm.set_df_property("employee_number", "hidden",1);
			cur_frm.set_df_property("employee", "read_only", r.auto_generate_employee_no ==0 ? 0 : 1); 
			}
			});


	     if (cur_frm.is_new()){
		frappe.call({
			method: "auto_generate_emp",
			doc: cur_frm.doc,
			callback: function(r)
			{
				if(r.message){ 
					cur_frm.set_value("employee_number", r.message);
					if (cur_frm.doc.company != "Danaf"){
						cur_frm.save() ;
						}
					cur_frm.set_df_property("employee", "hidden",1); }
				}
				
			});
	         }
	
	},
	after_save: function(frm) {
		if (cur_frm.is_new() || !cur_frm.doc.employee_name){//console.log( cur_frm.doc.name);
			frappe.call({
				method: "erpnext.hr.doctype.employee.employee.make_employee_docs",
				args: {employee_number:  cur_frm.doc.name},
				callback: function(r){cur_frm.disable_save();}
			});
		}
	},
	date_of_birth: function() {
		return cur_frm.call({
			method: "get_retirement_date",
			args: {date_of_birth: this.frm.doc.date_of_birth}
		});
	},

	salutation: function() {
		if(this.frm.doc.salutation) {
			this.frm.set_value("gender", {
				"Mr": "Male",
				"Ms": "Female"
			}[this.frm.doc.salutation]);
		}
	},


});
frappe.ui.form.on('Employee',{
//////////////////////////////////////////////

	ar_fname:function(frm){	
		if (frm.doc.ar_fname)
			frappe.call({
			method: "erpnext.hr.doctype.employee.employee.validate_only_arabic",
			args: { "ar_field": frm.doc.ar_fname }
			});

		frm.trigger("update_employee_name");
		//frm.doc.make_new('');
//frappe.set_route("Form","Appraisal")

//frappe.new_doc('Appraisal')
//window.open('#Form/Appraisal/New Appraisal 1', '_blank')
	},
	ar_sname:function(frm){
		if (frm.doc.ar_sname)	{
			frappe.call({
			method: "erpnext.hr.doctype.employee.employee.validate_only_arabic",
			args: { "ar_field": frm.doc.ar_sname }
			});
		}	

		frm.trigger("update_employee_name");

	},
	ar_tname:function(frm){
		if (frm.doc.ar_tname)	{
			frappe.call({
			method: "erpnext.hr.doctype.employee.employee.validate_only_arabic",
			args: { "ar_field": frm.doc.ar_tname }
			});
		}		

		frm.trigger("update_employee_name");
	},
	ar_family_name:function(frm){
		if (frm.doc.ar_family_name)	{
			frappe.call({
			method: "erpnext.hr.doctype.employee.employee.validate_only_arabic",
			args: { "ar_field": frm.doc.ar_family_name }
			});
		}	
		frm.trigger("update_employee_name");
	},
	en_fname:function(frm){	
		if (frm.doc.en_fname)
			frappe.call({
			method: "erpnext.hr.doctype.employee.employee.validate_only_english",
			args: { "en_field": frm.doc.en_fname }
			});
	},
	en_sname:function(frm){
		if (frm.doc.en_sname)	{
			frappe.call({
			method: "erpnext.hr.doctype.employee.employee.validate_only_english",
			args: { "en_field": frm.doc.en_sname }
			});
		}	

	},
	en_tname:function(frm){
		if (frm.doc.en_tname)	{
			frappe.call({
			method: "erpnext.hr.doctype.employee.employee.validate_only_english",
			args: { "en_field": frm.doc.en_tname }
			});
		}		

	},
	en_family_name:function(frm){
		if (frm.doc.en_family_name)	{
			frappe.call({
			method: "erpnext.hr.doctype.employee.employee.validate_only_english",
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

	work_shift: function(frm) {
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
	grade: function(frm) {
		frm.events.calc_basic_salary(frm);
	},
	experience_years: function(frm) {
		frm.events.calc_basic_salary(frm);
	},
 	calc_basic_salary: function(frm) {
		if (!frm.doc.grade)
		{
			//frappe.throw(__("Please enter the Grade"))
		}
		
		frappe.model.get_value('Grade Category Detail', {'parent': frm.doc.grade, 'experience_year':frm.doc.experience_years}, 'basic_salary',
  			function(r) {
			    if (!r){
				frm.set_value("basic_salary","0");
				frappe.throw(__("Salary does not setup for that experience years"))
				return false;
				}
				frm.set_value("basic_salary", r.basic_salary)


  			})
		

	},


///////////////////////////////////


	prefered_contact_email:function(frm){		
		frm.events.update_contact(frm)		
	},
	personal_email:function(frm){
		frm.events.update_contact(frm)
	},
	company_email:function(frm){
		//frm.events.update_contact(frm)
		frm.set_value("prefered_email",frm.doc.company_email)
	},
	user_id:function(frm){
		frm.events.update_contact(frm)
	},
	update_contact:function(frm){
		var prefered_email_fieldname = frappe.model.scrub(frm.doc.prefered_contact_email) || 'user_id';
		frm.set_value("prefered_email",
			frm.fields_dict[prefered_email_fieldname].value)
	},
	status: function(frm) {
		return frm.call({
			method: "deactivate_sales_person",
			args: {
				employee: frm.doc.employee,
				status: frm.doc.status
			}
		});
	},
	user_data: function(frm) {
		var userid= cur_frm.doc.employee_number;
		frappe.model.get_value('Employee Personal Detail',{'name': cur_frm.doc.employee_number},['user_id', 'ar_fname', 'ar_family_name'],function(r) {
		if (r){
			frappe.model.get_value('User', {employee:cur_frm.doc.employee_number},'name',function(d) {
				if (d){	frappe.set_route("Form", "User", d.name);}
				else {
					//frappe.new_doc('User',{employee: cur_frm.doc.employee_number});
					frappe.new_doc('User',{employee:cur_frm.doc.employee_number,first_name :r.ar_fname,full_name:r.ar_family_name,last_name:r.ar_family_name});
					}
			});
		    }
		else{
			frappe.model.get_value('User', {employee:cur_frm.doc.employee_number},'name',function(s) {
				if(s)	frappe.set_route("Form", "User", s.name);
				else    frappe.new_doc('User',{employee: cur_frm.doc.employee_number});
					
			});


			}
		
		});

	},
	personal_detail: function(frm) {
		frappe.model.get_value('Employee Personal Detail', cur_frm.doc.employee_number,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Personal Detail", cur_frm.doc.employee_number);
		}
		else frappe.new_doc('Employee Personal Detail',{employee: cur_frm.doc.employee_number,employee_number: cur_frm.doc.employee_number,user_id:user_email});
		});
	},
	salary_detail2: function(frm) {
		frappe.model.get_value('Employee Salary Detail', cur_frm.doc.employee_number,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Salary Detail", cur_frm.doc.employee_number);
		}
		else 
		frappe.new_doc('Employee Salary Detail',{employee: cur_frm.doc.employee_number});
		});
	},
	employment_detail: function(frm) {
		frappe.model.get_value('Employee Employment Detail', cur_frm.doc.employee_number,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Employment Detail",cur_frm.doc.employee_number);
		}
		else 
		frappe.new_doc('Employee Employment Detail',{employee: cur_frm.doc.employee_number});
		});
	},
	employee_data: function(frm) {
		frappe.model.get_value('Employee Data', cur_frm.doc.employee_number,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Data",cur_frm.doc.employee_number);
		}
		else 
		frappe.new_doc('Employee Data',{employee: cur_frm.doc.employee_number});
		});
	},
	
	ending_service_details: function(frm) {
		frappe.model.get_value('Employee Ending Service  Details', cur_frm.doc.employee_number,'name',function(r) {
		if (r) {
		frappe.set_route("Form", "Employee Ending Service  Details",cur_frm.doc.employee_number);
		}
		else
		frappe.new_doc('Employee Ending Service  Details',{employee: cur_frm.doc.employee_number});
		});
	},

	create_user: function(frm) {
		if (!frm.doc.prefered_email)
		{
			frappe.throw(__("Please enter Preferred Contact Email"))
		}
		frappe.call({
			method: "erpnext.hr.doctype.employee.employee.create_user",
			args: { employee: cur_frm.doc.name },
			callback: function(r)
			{
				frm.set_value("user_id", r.message)
			}
		});
	}
});
cur_frm.cscript = new erpnext.hr.EmployeeController({frm: cur_frm});

