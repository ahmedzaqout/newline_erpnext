// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Employee Functional Report"] = {
	"filters": [
		
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			on_change: function() {
				var employee = frappe.query_report_filters_by_name.employee.get_value();
				frappe.db.get_value("Employee", employee, "employee_name", function(value) {
					frappe.query_report_filters_by_name.employee_name.set_value(value["employee_name"]);
				});

			}


		},
		{
			"fieldname":"employee_name",
			"label": __("Employee Name"),
			"fieldtype": "Data",
			"read_only":1
		},
		{
			"fieldname":"status",
			"label": __("Employee Status"),
			"fieldtype": "Select",
			"options":["","Active", "Left","Stopped"]
		},
{
			"fieldname":"date_of_birth",
			"label": __("Date Of Birth"),
			"fieldtype": "Date"
		},
		{
			"fieldname":"gender",
			"label": __("Gender"),
			"fieldtype": "Link",
			"options": "Gender"
		},
		{
			"fieldname":"work_shift",
			"label": __("Work Shift"),
			"fieldtype": "Link",
			"options": "Work Shift"
		},

		{
			"fieldname":"grade",
			"label": __("Grade"),
			"fieldtype": "Link",
			"options": "Grade Category"
		},
		{
			"fieldname":"qualification",
			"label": __("Qualification"),
			"fieldtype": "Link",
			"options": "Qualification"
		},
		{
			"fieldname":"specialization",
			"label": __("Specialization"),
			"fieldtype": "Link",
			"options": "Specialization"
		},

		{
			"fieldname":"city",
			"label": __("City"),
			"fieldtype": "Link",
			"options": "City"
		},
		{
			"fieldname":"governorate",
			"label": __("Governorate"),
			"fieldtype": "Link",
			"options": "Governorate"
		},
		{
			"fieldtype": "Break",
		},


				{
			"fieldname":"branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch"
					},

			{
			"fieldname":"management",
			"label": __("Management"),
			"fieldtype": "Link",
			"options": "Management"	,
			"get_query": function() {
				var company = frappe.query_report_filters_by_name.company.get_value();
				return {
					"doctype": "Management",
					"filters": {
						"management": frappe.query_report_filters_by_name.branch.get_value(),
					}
				}
			}	
				},
				{
			"fieldname":"circle",
			"label": __("Circle"),
			"fieldtype": "Link",
			"options": "Circle"	,
			"get_query": function() {
				var company = frappe.query_report_filters_by_name.company.get_value();
				return {
					"doctype": "Circle",
					"filters": {
						"circle": frappe.query_report_filters_by_name.management.get_value(),
					}
				}
			}	
				},		
		
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1,
			"hidden":1
		},

//	Confirmation Date
	]
	

}
