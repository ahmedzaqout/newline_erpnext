# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _
import datetime

def execute(filters=None):

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)

	data = salaries(conditions, filters)
	

	return columns, data


def get_columns(filters):
	columns = [
		 {"label":_("Employee Name") ,"width":100,"fieldtype": "link","options":"Employee"},
		 {"label":_("Designation") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Department") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Circle") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Employment Type") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Contract End Date") ,"width":100,"fieldtype": "Date"},
		 {"label":_("Date Of Retirement") ,"width":100,"fieldtype": "Date"},

		 
]

	return columns

def salaries(conditions, filters):
	data=[]
	tod=datetime.datetime.today().strftime('%Y-%m-%d')
	ss  = frappe.db.sql("""select * from `tabEmployee`  where docstatus <2 %s order by name """ %
		conditions, filters, as_dict=1)

	for emp in ss:
		row=[emp.employee_name,emp.designation,emp.department,emp.circle,emp.employment_type,emp.contract_end_date,emp.date_of_retirement]
		data.append(row)

	return data




def get_conditions(filters):
	conditions = ""
	tod=datetime.date.today().strftime('%Y-%m-%d')
	conditions += " and contract_end_date <= '{0}'".format(tod)
	if filters.get("employee"): conditions += " and name = %(employee)s"
	if filters.get("department"): conditions += " and department = %(department)s"
	return conditions, filters
