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
		 {"label":_("Departement") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Permanent Address") ,"width":200,"fieldtype": "Data"},
		 {"label":_("Current Address") ,"width":200,"fieldtype": "Data"},
		 {"label":_("Cell Number") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Emergency Phone Number") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Identity No") ,"width":100,"fieldtype": "Data"},

		 
		 ]
		

	
	
	return columns

def salaries(conditions, filters):
	data=[]
	hours={}
	ss  = frappe.db.sql("""select * from `tabEmployee` where docstatus <2 %s order by name """ %
		conditions, filters, as_dict=1)


	for add in ss:
		data.append([add.employee,add.designation,add.department,add.permanent_address,add.current_address,add.cell_number,add.cell_number,add.emergency_phone_number,add.identity_no])
	
	return data


def get_conditions(filters):
	conditions = ""

	if filters.get("employee"): conditions += " and name = %(employee)s"
	if filters.get("department"): conditions += " and management = %(department)s"
	if filters.get("designation"): conditions += " and designation = %(company)s"

	return conditions, filters
