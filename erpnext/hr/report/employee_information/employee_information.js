// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Information"] = {
	"filters": [
		// {
		// 	"fieldname":"employee",
		// 	"label": __("Employee"),
		// 	"fieldtype": "Link",
		// 	"options": "Employee"
		// },
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
			"fieldname":"branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch"
		},
		// {
		// 	"fieldname":"management",
		// 	"label": __("Management"),
		// 	"fieldtype": "Link",
		// 	"options": "Management"
		// },
		{
			"fieldname":"circle",
			"label": __("Circle"),
			"fieldtype": "Link",
			"options": "Circle"
		},
		{
			"fieldname":"sub_departement",
			"label": __("Sub Departement"),
			"fieldtype": "Link",
			"options": "Sub Departement"
		},
		{
			"fieldname":"department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"
		},
		
		{
			"fieldname":"gender",
			"label": __("Gender"),
			"fieldtype": "Link",
			"options": "Gender"
		}
		,
		{
			"fieldname":"marital_status",
			"label": __("Marital Status"),
			"fieldtype": "Select",
			"options": "\nSingle\nMarried\nDivorced\nWidowed"
		},
		{
			"fieldname":"nationality",
			"label": __("Nationality"),
			"fieldtype": "Link",
			"options": "Nationality"
		},
		{
			"fieldname":"governorate",
			"label": __("Governorate"),
			"fieldtype": "Link",
			"options": "Governorate"
		},
		{
			"fieldname":"city",
			"label": __("City"),
			"fieldtype": "Link",
			"options": "City"
		},
		{
			"fieldname":"employment_type",
			"label": __("Employment Type"),
			"fieldtype": "Link",
			"options": "Employment Type"
		}
	]
}
