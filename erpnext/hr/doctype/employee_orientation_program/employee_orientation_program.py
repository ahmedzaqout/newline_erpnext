# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class EmployeeOrientationProgram(Document):
	def get_activities(self):
		return  frappe.get_list("Program Activity Details", fields=["activity_name"], filters={"company":self.company})

	def get_records(self):
		return  frappe.get_list("Required Record", fields=["required_record"], filters={"company":self.company})

	def get_communications(self):
		return  frappe.get_list("Effective Communication", fields=["effective_communication"], filters={"company":self.company})

	def get_emp_designation(self):
		return frappe.db.get_value('Employee',self.employee,'designation',as_dict=1)

