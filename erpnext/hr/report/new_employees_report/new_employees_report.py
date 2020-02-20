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
	ss  = frappe.db.sql("""select emp.name,emp.employee_name , ed.* from `tabEmployee` as emp join `tabEmployee Employment Detail` as ed on emp.name=ed.employee left Join `tabEmployee Contact Details` as cd on emp.name=cd.employee left join `tabEmployee Personal Detail` as pd on  emp.name=pd.employee where emp.docstatus <2 %s order by employee """ % conditions, filters, as_dict=1)

	for add in ss:
		data.append([add.employee,add.employee_name,add.designation,add.management, add.date_of_joining,add.employment_type])
	
	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("start_date"): conditions += " and ed.date_of_joining >= %(start_date)s"
	if filters.get("end_date"): conditions += " and ed.date_of_joining <= %(end_date)s"
	if filters.get("employee"): conditions += " and emp.employee = %(employee)s"
	if filters.get("department"): conditions += " and ed.management = %(department)s"
	if filters.get("designation"): conditions += " and ed.designation = %(designation)s"

	return conditions, filters
