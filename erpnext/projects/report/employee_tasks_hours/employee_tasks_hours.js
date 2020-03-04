// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Tasks Hours"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
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
			"fieldname":"less",
			"label": __("Less than 7 Hours"),
			"fieldtype": "Check",

		}
	
	]
}
