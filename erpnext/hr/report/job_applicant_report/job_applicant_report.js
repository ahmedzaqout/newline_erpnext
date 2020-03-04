// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Job Applicant Report"] = {
	"filters": [
	
		{
			"fieldname":"job_opening",
			"label": __("Job Opening"),
			"fieldtype": "Link",
			"options": "Job Opening"
		},
                {
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nOpen\nReplied\nRejected\nHold"
		},
		
		
		
		
		
	
	]
}
