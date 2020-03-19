# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _

def execute(filters=None):

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)

	data = penalties(conditions,filters)
	

	return columns, data

def get_columns(filters):
	columns = [
		 {"label":_("Employee Name") ,"width":120,"fieldtype": "Data","options":"Employee"},
		 {"label":_("Designation") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Departement") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Warning Date") ,"width":100,"fieldtype": "Date"},
		 {"label":_("Employee Violation") ,"width":180,"fieldtype": "Data"},
		 {"label":_("Penalty") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Penalty Type") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Warning Type") ,"width":150,"fieldtype": "Data"},
		 {"label":_("Discount Amount") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Discount Period Type") ,"width":100,"fieldtype": "Data"}	
		 ]	
	
	return columns

def penalties(conditions, filters):
	data=[]
	hours={}
	penalties  = frappe.db.sql("""select we.* , p.penalty_type,p.discount_day,p.discount_period,p.warning_type,pd.designation ,pd.employee_name, pd.management from `tabWarning Information` as we left Join `tabEmployee` as pd on we.employee=pd.name join tabPenalty as p on we.penalty=p.name where we.docstatus <2 %s 
		order by we.employee """ %
		conditions, filters, as_dict=1)
	for m in penalties:
		#employee_name = frappe.db.get_value("Employee",m.employee,"employee_name")
		data.append([m.employee_name ,m.designation,m.management,m.warning_date,m.employee_violation,m.penalty,m.penalty_type,m.warning_type,m.discount_day,m.discount_period])
		#if m.penalty_type=="Discount":
		#	data.append(["",m.discount_day,m.discount_period])

		#elif m.penalty_type=="Warning":
		#	data.append([m.warning_type,"",""])

	return data




def get_conditions(filters):
	conditions = ""
	if filters.get("employee"): conditions += " and we.employee = %(employee)s"
	if filters.get("department"): conditions += " and pd.management = %(department)s"

 	if filters.get("designation"): conditions += " and pd.designation = %(designation)s"

	return conditions, filters
