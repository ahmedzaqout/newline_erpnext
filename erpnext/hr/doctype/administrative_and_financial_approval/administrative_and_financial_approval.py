# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class AdministrativeandFinancialApproval(Document):
	def autoname(self):
		#keys = filter(None, (self.applicant_name, self.job_title))
		#key= '-'.join(str(keys))
		self.name = make_autoname('AdminApproval/'+self.job_applicant+'-'+self.job_title + '/.#####')
		#self.name = make_autoname('Admin Approval/' +self.job_title+'/'+self.job_applicant + '/.#####')

	def validate(self):
		self.validate_duplicate()
		if not self.is_new():
			self.is_recommended= 1

		#if self.is_new() and self.company == 'Nawa':
		#	self.new_offer()

	def new_offer(self):
		doc = frappe.new_doc('Offer Letter')
		jo= frappe.get_doc("Job Opening" ,self.job_title)
		doc.update({
			'job_applicant': self.job_applicant ,
			'applicant_name':self.applicant_name,
			'job_number': self.job_number,
			'job_number': self.job_number,
			"grade": self.grade,
			"category": self.category,
			"salary": self.salary,
			'job_opening':self.job_title,
			'status': 'Accepted',
			'docstatus': 1
			})
		doc.insert(ignore_permissions=True)

	def validate_duplicate(self):
		duplicate = frappe.db.get_value("Administrative and Financial Approval",
			filters = {
				"job_applicant": self.job_applicant,
				"job_number": self.job_number,
				"name": ["!=", self.name]
			}
		)
		if duplicate:
			frappe.throw(_("Duplicate Administrative and Financial Approval of job number {0} for employee {1}").format(self.job_number,self.applicant_name))		



