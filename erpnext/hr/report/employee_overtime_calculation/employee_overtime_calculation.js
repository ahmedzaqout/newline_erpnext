// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Employee Overtime Calculation"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
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
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		}
		
	],

}

