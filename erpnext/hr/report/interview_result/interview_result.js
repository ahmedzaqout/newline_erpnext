// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Interview Result"] = {
	"filters": [
	{
			"fieldname":"job_opening",
			"label": __("Job Opening"),
			"fieldtype": "Link",
			"options": "Job Opening",
			"reqd": 1
		},
		{
			"fieldname":"job_applicant",
			"label": __("Job Applicant"),
			"fieldtype": "Link",
			"options": "Job Applicant",
			on_change: function() {
				var job_applicant = frappe.query_report_filters_by_name.job_applicant.get_value();
				if (job_applicant)
				frappe.db.get_value("Job Applicant", job_applicant, "applicant_name", function(value) {
					frappe.query_report_filters_by_name.applicant_name.set_value(value["applicant_name"]);
				});

			}
		},
		{
			"fieldname":"applicant_name",
			"label": __("Applicant Name"),
			"fieldtype": "Data",
			"read_only":1
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
			"fieldname":"age",
			"label": __("Age"),
			"fieldtype": "Int",
		},
		{
			"fieldname":"qualification",
			"label": __("Qualification"),
			"fieldtype": "Select",
			"options": "\nدبلوم\nبكالوريوس\nماجستير\nدكتوراة"
		},
		{
			"fieldname":"experience_years",
			"label": __("Experience Years"),
			"fieldtype": "Select",
			"options": "\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12\n13\n14\n15\n16\n17\n18\n19\n20\n21\n22\n23\n24\n25\n26\n27\n28\n29\n30"
		},

		{
			"fieldname":"order_desc",
			"label": __("Order Desc"),
			"fieldtype": "Check"
		},


	]
}
