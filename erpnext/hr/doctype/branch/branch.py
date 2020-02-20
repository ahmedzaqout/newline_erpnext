# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext

from frappe.model.document import Document

class Branch(Document):
	def autoname(self):
		if self.company:
			suffix = " - " + "BRA"
			if not self.branch.endswith(suffix):
				self.name = self.branch + suffix
		else:
			self.name = self.Branch_name

	def before_rename(self, old_name, new_name, merge=False):
		# Add company abbr if not provided
		new_Branch = erpnext.encode_company_abbr(new_name, self.company)

		if merge:
			if not frappe.db.exists("Branch", new_Branch):
				frappe.throw(_("Branch {0} does not exist").format(new_Branch))

			if self.company != frappe.db.get_value("Branch", new_Branch, "company"):
				frappe.throw(_("Both Branch must belong to same Company"))

		return new_Branch

	def after_rename(self, old_name, new_name, merge=False):
		new_Branch_name = self.get_new_branch_name_without_abbr(new_name)
		self.db_set("branch", new_Branch_name)
				

	def get_new_branch_name_without_abbr(self, name):
		company_abbr = frappe.db.get_value("Company", self.company, "abbr")
		parts = name.rsplit(" - ", 1)
		
		if parts[-1].lower() == company_abbr.lower():
			name = parts[0]
			
		return name
