# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _

def execute(filters=None):


	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)

	data = salaries(conditions, filters)
	

	return columns, data


def get_columns(filters):
	columns = [
		 {"label":_("Employee Name") ,"width":100,"fieldtype": "link","options":"Employee"},
		 {"label":_("Designation") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Management") ,"width":100,"fieldtype": "Date"},
		 {"label":_("Circle") ,"width":100,"fieldtype": "Date"},
		 {"label":_("Employement Type") ,"width":100,"fieldtype": "Date"}]
	
	
	return columns

def salaries(conditions, filters):
	data=[]
	ss  = frappe.db.sql("""select * from `tabEmployee` docstatus <2 %s order by name """ %
		conditions, filters, as_dict=1)

	for emp in ss:
		row=[emp.employee_name,emp.designation,emp.management,emp.circle,emp.employment_type]

		data.append(row)

	return data

def get_conditions(filters):
	conditions = ""
	if filters.get("employee"): conditions += " and name = %(employee)s"
	if filters.get("management"): conditions += " and management = %(management)s"
	if filters.get("designation"): conditions += " and designation = %(designation)s"
	if filters.get("employment_type"): conditions += " and employment_type = %(employment_type)s"

	return conditions, filters


