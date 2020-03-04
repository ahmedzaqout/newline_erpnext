// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Tasks Report"] = {
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
			"fieldname":"project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options": "Project"
		},
{
			"fieldname":"task",
			"label": __("Task"),
			"fieldtype": "Link",
			"options": "Task"
		},
{
			"fieldname":"task_category",
			"label": __("Task Type"),
			"fieldtype": "Select",
			"options": "Normal Task\nModification\nAddition\nUnplanned Task\nOther"
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
		}
	
	]
}
