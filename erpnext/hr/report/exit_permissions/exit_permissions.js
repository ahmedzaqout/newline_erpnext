// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Exit permissions"] = {
	"filters": [
		
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
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
			"options": "Department"
		},
		{
			"fieldname":"supervisor",
			"label": __("Supervisor"),
			"fieldtype": "Link",
			"options": "Employee"
		},

	
		{
			"fieldname":"permission_type",
			"label": __("Permission Type"),
			"fieldtype": "Select",
			"options": "\nEarly Departure\nExit with return\nExit without return\nMorning Late"
		},
		{
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nOpen\nApproved\nRejected"
		}
	]
}
