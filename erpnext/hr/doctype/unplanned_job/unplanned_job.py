# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class UnplannedJob(Document):
	pass


@frappe.whitelist()
def make_job_opening(source_name, target_doc=None):
	def set_missing_values(source, target):
		job_opening = frappe.get_doc(target)	
		job_opening.job_type = "Unplanned Job"
		job_opening.run_method("set_missing_values")


	doclist = get_mapped_doc("Unplanned Job", source_name, {
		"Unplanned Job": {
			"doctype": "Job Opening",
			"field_map": {
				"designation": "designation",
				"grade": "grade",
				"name" : "job_number",
				"job_number" :"job_code",
				"linked_doctype": "Planned Job",
				"department": "department",
				"qualification": "qualification",

			}
		},
		"Duties and Responsibilities": {
			"doctype": "Duties and Responsibilities",
			"field_map": {
				"parent": "prevdoc_docname",
				"parenttype": "prevdoc_doctype",

			},
			"add_if_empty": True
		},
		"Functional Specification Items": {
			"doctype": "Functional Specification Items",
			"field_map": {
				"parent": "prevdoc_docname",
				"parenttype": "prevdoc_doctype",

			},
			"add_if_empty": True
		},
		"Job Performance Requirements": {
			"doctype": "Job Performance Requirements",
			"field_map": {
				"parent": "prevdoc_docname",
				"parenttype": "prevdoc_doctype",

			},
			"add_if_empty": True
		},


	}, target_doc, set_missing_values)

	return doclist

