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
		 {"label":_("Employee ") ,"width":100,"fieldtype": "link","options":"Employee"},
		 {"label":_("Employee Name") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Designation") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Department") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Employment Type") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Date of Joining") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Contract End Date") ,"width":100,"fieldtype": "Date"},
		 {"label":_("Date Of Retirement") ,"width":100,"fieldtype": "Date"}
		 ]

		
	return columns

def salaries(conditions, filters):
	data=[]
	hours={}
	ss  = frappe.db.sql("""select emp.name , emp.employee_name,ed.* from `tabEmployee` as emp join `tabEmployee Employment Detail` as ed on emp.name=ed.employee
	 					left join `tabEmployee Personal Detail` as pd on  emp.name=pd.employee where emp.docstatus <2 %s 
						order by employee """ %
		conditions, filters, as_dict=1)


	for add in ss:
		data.append([add.employee, add.employee_name,add.designation,add.department,add.employment_type,add.date_of_joining,add.contract_end_date,add.scheduled_confirmation_date])
	
	return data


def get_conditions(filters):
	conditions = ""

	if filters.get("employee"): conditions += " and emp.employee = %(employee)s"
	if filters.get("department"): conditions += " and ed.management = %(department)s"
	if filters.get("designation"): conditions += " and ed.designation = %(designation)s"
	if filters.get("employment_type"): conditions += " and ed.employment_type = %(employment_type)s"

	return conditions, filters
