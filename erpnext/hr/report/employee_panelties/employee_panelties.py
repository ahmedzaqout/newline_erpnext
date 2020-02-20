# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _

def execute(filters=None):

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)

	data = salaries(conditions,filters)
	

	return columns, data

def get_columns(filters):
	columns = [
		 {"label":_("Employee Name") ,"width":100,"fieldtype": "link","options":"Employee"},
		 {"label":_("Designation") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Departement") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Employee Violation") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Penalty Type") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Discount Amount") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Discount Period Type") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Warning Type") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Warning Date") ,"width":100,"fieldtype": "Date"}]
		
	
	return columns

def salaries(conditions, filters):
	data=[]
	hours={}
	ss  = frappe.db.sql("""select we.* , p.penalty_type,p.discount_day,p.discount_period,p.warning_type,pd.designation , pd.management from `tabWarning Information` as we left Join `tabEmployee Employment Detail` as pd on we.employee=pd.employee join tabPenalty as p on we.penalty=p.name where we.docstatus <2 %s 
		order by employee """ %
		conditions, filters, as_dict=1)

	for m in ss:
		if m.penalty_type=="Discount":
			data.append([m.employee,m.designation,m.management,m.employee_violation,m.penalty,m.discount_day,m.discount_period,"",m.warning_date])

		elif m.penalty_type=="Warning":
			data.append([m.employee,m.designation,m.management,m.employee_violation,m.penalty,"","",m.warning_type,m.warning_date])

		else:
			data.append([m.employee,m.designation,m.management,m.employee_violation,m.penalty,"","","",m.warning_date])

	return data




def get_conditions(filters):
	conditions = ""
	if filters.get("employee"): conditions += " and we.employee = %(employee)s"
	if filters.get("department"): conditions += " and pd.management = %(department)s"

 	if filters.get("designation"): conditions += " and pd.designation = %(designation)s"

	return conditions, filters
