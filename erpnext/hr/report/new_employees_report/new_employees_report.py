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
		 {"label":_("Employee") ,"width":100,"fieldtype": "link","options":"Employee"},
		 {"label":_("Employee Name") ,"width":120,"fieldtype": "link","options":"Employee"},
		 {"label":_("Designation") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Management") ,"width":150,"fieldtype": "Data"},
		 {"label":_("Date Of Joining") ,"width":150,"fieldtype": "Data"},
		 {"label":_("Employment Type") ,"width":150,"fieldtype": "Data"}
		 ]
		

	
	
	return columns

def salaries(conditions, filters):
	data=[]
	hours={}
	ss  = frappe.db.sql("""select * from `tabEmployee` where docstatus <2 %s order by name """ % conditions, filters, as_dict=1)

	for add in ss:
		data.append([add.name,add.employee_name,add.designation,add.department, add.date_of_joining,add.employment_type])
	
	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("start_date"): conditions += " and date_of_joining >= %(start_date)s"
	if filters.get("end_date"): conditions += " and date_of_joining <= %(end_date)s"
	if filters.get("employee"): conditions += " and name = %(employee)s"
	if filters.get("department"): conditions += " and department = %(department)s"
	if filters.get("designation"): conditions += " and designation = %(designation)s"

	return conditions, filters
