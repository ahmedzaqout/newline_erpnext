# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext

from frappe.model.document import Document

class Department(Document):
	pass

@frappe.whitelist()
def get_parent(doctype, txt, searchfield, start, page_len, filters):
	from erpnext.controllers.queries import get_match_cond
	conditions = []
	fcond=""
	return frappe.db.sql("""select name from tabCircle where docstatus < 2 and is_group=1 union all  select name from tabDepartment where docstatus < 2 and is_group=1""")

	#return frappe.db.sql("select name from tabBranch where docstatus < 2 and is_group=1 union all  select name from tabDepartment where docstatus < 2 and is_group=1", as_dict=1)
