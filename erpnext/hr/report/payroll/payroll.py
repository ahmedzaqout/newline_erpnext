# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _

def execute(filters=None):
	if not filters: filters = {}

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	emp_map = get_employee_details(conditions, filters)


	data = []
	row =[]
	for i in range(1,31):
		row +=[i,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,555]
		#if i==1: 
		row[16-i]= row[17-i]+50
		row[14]= 22

		if i>=2: 
			row[15]= (row[15]*2.5/100) + row[15]
			row[16]= (row[16]*2.5/100) + row[16]
		#row +=[emp.employee_name]
			
		data.append(row)

	return columns, data

def get_columns(filters):
	columns = [
		 {"label":_("Seniorities") ,"width":70,"fieldtype": "Data"},
		 {"label":_("A1") ,"width":60,"fieldtype": "Data"},
		 {"label":_("A2") ,"width":60,"fieldtype": "Data"},
		 {"label":_("A2") ,"width":60,"fieldtype": "Data"},
		 {"label":_("A") ,"width":60,"fieldtype": "Data"},
		 {"label":_("B") ,"width":60,"fieldtype": "Data"},
		 {"label":_("C") ,"width":60,"fieldtype": "Data"}
	]

	for i in range(1,11):
		columns.append(str(i) +":Data:60")
		 

	
	return columns


def get_conditions(filters):

	conditions = ""
	if filters.get("branch"): conditions += " and branch = %(branch)s"
	

	return conditions, filters

def get_employee_details(conditions, filters):
	emp_map  = frappe.db.sql("""select emp.name,employee_name,employee_number,emp.status as emp_status, basic_salary,bank_name,bank_branch, branch,management,circle,department,work_shift,ifnull(date_of_birth,'') ,gender,grade, emp.city as emp_city,emp.governorate as gov,edu.qualification,edu.specialization,final_confirmation_date, edu.name from tabEmployee as emp left join `tabEmployee Education` as edu on emp.name=edu.employee where emp.docstatus < 1 %s  order by emp.name""" %
		conditions, filters, as_dict=1)

	return emp_map

#no-report-area msg-box no-border

