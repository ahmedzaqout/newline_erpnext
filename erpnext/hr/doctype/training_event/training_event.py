# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.hr.doctype.employee.employee import get_employee_emails
from frappe.utils import date_diff
from frappe import _, msgprint

class TrainingEvent(Document):
	def validate(self):
		self.validate_dates()
		self.employee_emails = ', '.join(get_employee_emails([d.employee
			for d in self.employees]))

	def validate_dates(self):
		if date_diff(self.end_time, self.start_time) < 0:
			frappe.throw(_("To date cannot be before From date"))
	
	def validate_trainees(self, employee=None):
		doc =frappe.get_all("Training Target",{"parent":self.training_program},'employee')
		for d in doc:
			if d.employee == employee:
				return True
			else: return False


	def get_trainees(self):
		return frappe.get_all("Training Target",['employee'],filters={"parent":self.training_program})


	def get_trainers(self):
		return frappe.get_all("Trainer",['trainer_name','trainer_email','contact_number'],filters={"parent":self.training_program})
		#for d in doc:
		#	if d.employee == employee:
		#		return True
		#	else: False


