// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */
var d = new Date();

frappe.query_reports["Attendance Summary"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": new Date(d.getFullYear(),d.getMonth(),1),//frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		}
		// ,
		// {
		// 	"fieldname":"employee",
		// 	"label": __("Employee"),
		// 	"fieldtype": "Link",
		// 	"options": "Employee",
		// 	"read_only": 0,
		// 	on_change: function() {
		// 		var employee = frappe.query_report_filters_by_name.employee.get_value();
		// 		frappe.db.get_value("Employee", employee, "employee_name", function(value) {
		// 			frappe.query_report_filters_by_name.employee_name.set_value(value["employee_name"]);
		// 		});
		// 	}
		// },
		// {
		// 	"fieldname":"employee_name",
		// 	"label": __("Employee Name"),
		// 	"fieldtype": "Data",
		// 	"read_only":1
		// }

	]
}
