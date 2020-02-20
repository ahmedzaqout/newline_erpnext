# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class JobEmployeeAudit(Document):
	def get_records(self):
		return  frappe.get_list("Required Record", fields=["required_record"], filters={"company":self.company})

	def get_emp_data(self):
		try:
			designation,date_of_joining = frappe.db.get_value('Employee Employment Detail',self.employee,['designation','date_of_joining'],as_dict=1)
			job_number = frappe.db.get_value('Employee Salary Detail',self.employee,'job_number',as_dict=1)
			home_number,mobile_number = frappe.db.get_value('Employee Personal Detail',self.employee,['home_phone','phone_number'],as_dict=1)
			return designation, date_of_joining,job_number.job_number,home_number,mobile_number
		except:
			pass
