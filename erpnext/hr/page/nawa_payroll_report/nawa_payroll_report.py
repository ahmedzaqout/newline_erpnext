# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, json, ast
import frappe.defaults
from frappe.utils import flt
from erpnext import get_default_company

@frappe.whitelist(allow_guest=True)
def get_designation():
	designation = []
	company= get_default_company()
	dep = frappe.get_all('Designation',{'company':company},"designation_name")
	for d in dep:
		designation.append(d.designation_name)
	return designation


