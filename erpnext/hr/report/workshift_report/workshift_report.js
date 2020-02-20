// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
var d = new Date();

frappe.query_reports["Workshift Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd" : 1,
			"default": new Date(d.getFullYear(),d.getMonth(),1)
			
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd" : 1
		},
{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Management"
		},
		{
			"fieldname":"designation",
			"label": __("Designation"),
			"fieldtype": "Link",
			"options": "Designation"
		},
{
			"fieldtype": "Break",
		},

		{
			"fieldname":"less",
			"label": __("Less Hours"),
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname":"more",
			"label": __("More Hours"),
			"fieldtype": "Check",
			"default": 1

		},
		{
			"fieldname":"exact",
			"label": __("Exact Hours"),
			"fieldtype": "Check",
			"default": 1

		},
	]
}
