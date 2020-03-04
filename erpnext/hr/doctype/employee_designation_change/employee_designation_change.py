# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Employeedesignationchange(Document):
	def validate(self):
		emp = frappe.get_doc("Employee", {"employee":self.employee})
		if emp:
	    		employee = frappe.db.sql("""update `tabEmployee` set designation='{designation}' where employee= '{employee}'""".format	(designation=self.to_designation, employee=self.employee),  as_dict=1)
