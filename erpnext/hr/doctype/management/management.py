# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Management(Document):
	def autoname(self):
		if self.company:
			suffix = " - " + "MGT"
			if not self.management.endswith(suffix):
				self.name = self.management + suffix
		else:
			self.name = self.management

	def before_rename(self, old_name, new_name, merge=False):
		# Add company abbr if not provided
		new_Management = erpnext.encode_company_abbr(new_name, self.company)

		if merge:
			if not frappe.db.exists("Management", new_Management):
				frappe.throw(_("Management {0} does not exist").format(new_Management))

			if self.company != frappe.db.get_value("Management", new_Management, "company"):
				frappe.throw(_("Both Management must belong to same Company"))

		return new_Management

	def after_rename(self, old_name, new_name, merge=False):
		new_Management_name = self.get_new_management_name_without_abbr(new_name)
		self.db_set("management", new_Management_name)
				

	def get_new_management_name_without_abbr(self, name):
		company_abbr = frappe.db.get_value("Company", self.company, "abbr")
		parts = name.rsplit(" - ", 1)
		
		if parts[-1].lower() == company_abbr.lower():
			name = parts[0]
			
		return name
