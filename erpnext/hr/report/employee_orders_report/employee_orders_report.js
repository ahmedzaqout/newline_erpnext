// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Orders Report"] = {
	"filters": [
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
			"fieldname":"designation",
			"label": __("Designation"),
			"fieldtype": "Link",
			"options": "Designation"
		},
{
			"fieldname":"type",
			"label": __("Order Type"),
			"fieldtype": "Select",
			"options": "\nEmployee Edit Time\nTimesheet\nExit Permission\nLeave Application",
			"reqd" :1
		}
	]
}
