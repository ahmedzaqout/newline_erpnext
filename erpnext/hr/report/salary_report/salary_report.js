// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Salary Report"] = {
	"filters": [
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			"default": "",
			"reqd": 1
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"default": "",
			"reqd": 1
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname":"department",
			"label": __("Management"),
			"fieldtype": "Link",
			"options": "Management"
		},

{
			"fieldtype": "Break",
		},

		{
			"fieldname":"earnings",
			"label": __("Earnings"),
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname":"deductions",
			"label": __("Deductions"),
			"fieldtype": "Check",
			"default": 1

		},
		
	
	]
}
