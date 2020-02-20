# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Circle(Document):
	def autoname(self):
		if self.company:
			suffix = " - " + "CIR"
			if not self.circle.endswith(suffix):
				self.name = self.circle + suffix
		else:
			self.name = self.circle

	def before_rename(self, old_name, new_name, merge=False):
		# Add company abbr if not provided
		new_Circle = erpnext.encode_company_abbr(new_name, self.company)

		if merge:
			if not frappe.db.exists("Circle", new_Circle):
				frappe.throw(_("Circle {0} does not exist").format(new_Circle))

			if self.company != frappe.db.get_value("Circle", new_Circle, "company"):
				frappe.throw(_("Both Circle must belong to same Company"))

		return new_Circle

	def after_rename(self, old_name, new_name, merge=False):
		new_Circle_name = self.get_new_circle_name_without_abbr(new_name)
		self.db_set("circle", new_Circle_name)
				

	def get_new_circle_name_without_abbr(self, name):
		company_abbr = frappe.db.get_value("Company", self.company, "abbr")
		parts = name.rsplit(" - ", 1)
		
		if parts[-1].lower() == company_abbr.lower():
			name = parts[0]
			
		return name
