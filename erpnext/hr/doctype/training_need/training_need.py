# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe import _


class TrainingNeed(Document):
	def validate(self):
		if not self.employee and not self.company and not self.department:
			frappe.throw(_("Employee, Department or Company should not be empty"))



def employee_qry(doctype, txt, searchfield, start, page_len, filters):
	conditions = []
	return frappe.db.sql("""select employee_name as name, status , docstatus from tabEmployee   where status = 'Active' and docstatus < 2 {fcond} order by name""".format(**{
			'fcond': get_filters_cond(doctype, filters, conditions)
		}) )

