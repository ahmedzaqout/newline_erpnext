# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class EmployeeEndingServiceDetails(Document):
	def update_emp_status(self, status):
		frappe.db.set_value('Employee Employment Detail', self.employee,'status',status)
		frappe.db.set_value("Employee", self.employee, "status", status)
		frappe.db.set_value("User", {"employee":self.employee}, "enabled", 0)
