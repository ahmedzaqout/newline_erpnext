// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Employee Financial Report"] = {
	"filters": [
				
		{
			"fieldname":"basic_salary",
			"label": __("Basic Salary(from)"),
			"fieldtype": "Currency"
		},
		{
			"fieldname":"basic_salary_to",
			"label": __("Basic Salary(to)"),
			"fieldtype": "Currency"
		},
		{
			"fieldname":"employee",
			"label": __("Employee Number"),
			"fieldtype": "Link",
			"options": "Employee"
		},
			
		{
			"fieldname":"designation",
			"label": __("Designation"),
			"fieldtype": "Link",
			"options": "Designation"
		},
		{
			"fieldname":"bank",
			"label": __("Bank"),
			"fieldtype": "Link",
			"options": "Bank"
		},
	{
			"fieldname":"bank_account_no",
			"label": __("Bank Account No"),
			"fieldtype": "Data"
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
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"	
				},
		
		
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"fieldtype": "Date"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"default": frappe.datetime.get_today(),
			"fieldtype": "Date"
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
