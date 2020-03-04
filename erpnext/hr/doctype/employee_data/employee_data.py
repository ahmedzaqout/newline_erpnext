# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.hr.doctype.employee_personal_detail.employee_personal_detail import add_depenents_bonus

class EmployeeData(Document):
	def validate(self):
		if self.employee_dependent: 
			child_num =0
			for d in self.get("employee_dependent"): #('Employee Dependent')
				if d.relation =='Son' or d.relation =='Daughter':
					child_num += 1
			add_depenents_bonus(self.employee, 'Bonus Children', child_num)

	
