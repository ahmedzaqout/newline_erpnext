# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe.model.document import Document

class Headquarter(Document):
	def autoname(self):
		if self.company:
			suffix = " - " + "HEQ"
			if not self.headquarter.endswith(suffix):
				self.name = self.headquarter + suffix
		else:
			self.name = self.headquarter

	def before_rename(self, old_name, new_name, merge=False):
		# Add company abbr if not provided
		new_Headquarter = erpnext.encode_company_abbr(new_name, self.company)

		if merge:
			if not frappe.db.exists("Headquarter", new_Headquarter):
				frappe.throw(_("Headquarter {0} does not exist").format(new_Headquarter))

			if self.company != frappe.db.get_value("Headquarter", new_Headquarter, "company"):
				frappe.throw(_("Both Headquarter must belong to same Company"))

		return new_Headquarter

	def after_rename(self, old_name, new_name, merge=False):
		new_Headquarter_name = self.get_new_headquarter_name_without_abbr(new_name)
		self.db_set("headquarter", new_Headquarter_name)
		self.reload()
				
		#if merge:
		#	self.recalculate_bin_qty(new_name)

	def get_new_headquarter_name_without_abbr(self, name):
		company_abbr = "HEQ"#frappe.db.get_value("Company", self.company, "abbr")
		parts = name.rsplit(" - ", 1)
		
		if parts[-1].lower() == company_abbr.lower():
			name = parts[0]
			
		return name
