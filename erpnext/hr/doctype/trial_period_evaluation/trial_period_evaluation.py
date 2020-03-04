# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TrialPeriodEvaluation(Document):
	def get_emp_designation(self):
		return frappe.db.get_value('Employee Employment Detail',self.employee,'designation',as_dict=1)

