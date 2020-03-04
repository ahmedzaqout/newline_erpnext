# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class InterviewerEvaluation(Document):
	def final_result(self):
		f_res = 0
		doc = frappe.db.get_list('Trial Period Evaluation Details',filters=[{"parent": self.name}],
		fields=["degree"],order_by='name DESC')
		if doc:
			for d in doc:
				f_res = f_res+ d.degree
		return f_res
