# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext

from frappe.model.document import Document

class Department(Document):
	def autoname(self):
		if self.company:
			suffix = " - " + "DEP"
			if not self.department_name.endswith(suffix):
				self.name = self.department_name + suffix
		else:
			self.name = self.department_name

	def before_rename(self, old_name, new_name, merge=False):
		# Add company abbr if not provided
		new_Department = self.encode_name_abbr(new_name)

		if merge:
			if not frappe.db.exists("Department", new_Department):
				frappe.throw(_("Department {0} does not exist").format(new_Department))

			if self.company != frappe.db.get_value("Department", new_Department, "company"):
				frappe.throw(_("Both Department must belong to same Company"))

		return new_Department

	def after_rename(self, old_name, new_name, merge=False):
		new_Department_name = self.get_new_department_name_without_abbr(new_name)
		self.db_set("department_name", new_Department_name)
				

	def get_new_department_name_without_abbr(self, name):
		company_abbr = "DEP"#frappe.db.get_value("Company", self.company, "abbr")
		parts = name.rsplit(" - ", 1)
		
		if parts[-1].lower() == company_abbr.lower():
			name = parts[0]
			
		return name
		
	def get_parentt(self):
		frappe.msgprint("nnnnnnn")

	
	def encode_name_abbr(self,name):
		'''Returns name encoded with company abbreviation'''
		company_abbr = "DEP"#frappe.db.get_value("Company", company, "abbr")
		parts = name.rsplit(" - ", 1)

		if parts[-1].lower() != company_abbr.lower():
			parts.append(company_abbr)

		return " - ".join(parts)

@frappe.whitelist()
def get_parent(doctype, txt, searchfield, start, page_len, filters):
	from erpnext.controllers.queries import get_match_cond
	conditions = []
	fcond=""
	return frappe.db.sql("""select name from tabCircle where docstatus < 2 and is_group=1 union all  select name from tabDepartment where docstatus < 2 and is_group=1""")

	#return frappe.db.sql("select name from tabBranch where docstatus < 2 and is_group=1 union all  select name from tabDepartment where docstatus < 2 and is_group=1", as_dict=1)
