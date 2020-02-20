// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Tasks"] = {
	"filters": [
		{
			"fieldname":"project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options" : "Project"

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
			"fieldname":"user",
			"label": __("Created By"),
			"fieldtype": "Link",
			"options": "Employee"
		}
	
	
	]
}
