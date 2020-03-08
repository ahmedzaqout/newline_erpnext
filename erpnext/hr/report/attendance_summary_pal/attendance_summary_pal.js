// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

var d = new Date();
frappe.query_reports["Attendance Summary Pal"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": new Date(d.getFullYear(),d.getMonth(),1),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
			{
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": 'Department'
		},
		{
			"fieldname":"supervisor",
			"label": __("Supervisor"),
			"fieldtype": "Link",
			"options": 'Employee'
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": 'Employee'
		}


	]
}
