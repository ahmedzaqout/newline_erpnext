// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Candidate Job Applicant"] = {
	"filters": [
	
		{
			"fieldname":"job_opening",
			"label": __("Job Opening"),
			"fieldtype": "Link",
			"options": "Job Opening"
		},
		{
			"fieldname":"age",
			"label": __("Age"),
			"fieldtype": "Int",
		},

		{
			"fieldname":"city",
			"label": __("City"),
			"fieldtype": "Link",
			"options": "City"
		},

		{
			"fieldname":"gender",
			"label": __("Gender"),
			"fieldtype": "Link",
			"options": "Gender"
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


		
		
		
		
		
		
	
	]
}
