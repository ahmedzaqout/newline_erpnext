# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.desk.reportview import build_match_conditions


def execute(filters=None):

	columns = get_column()
	conditions = get_conditions(filters)
	data = get_data(conditions, filters)

	return columns, data

def get_column():
	return [_("Employee") + ":Link/Employee:120",
		_("Employee Name") + "::150", 
		_("Date") + ":Link/Project:120",
		_("Hours") + ":float:100",
		_("Reson For less than 7") + "::250", 
]

def get_data(conditions, filters):
	if filters.get("less")== 1:
		time_sheet = frappe.db.sql("""select r.employee ,r.employee_name , r.date, r.total_hours , r.reson_for_less_than_7_hours from  `tabEmployee Task` as r  where r.docstatus <2 and r.total_hours < 7 %s order by r.date """%(conditions), filters, as_list=1)
	else:
		time_sheet = frappe.db.sql("""select r.employee ,r.employee_name , r.date, r.total_hours , r.reson_for_less_than_7_hours from  `tabEmployee Task` as r  where r.docstatus <2  %s order by r.date """%(conditions), filters, as_list=1)
	
	tot=0
	for n in time_sheet:
		tot=tot+n[3]
	time_sheet.append(["","", "Total" ,tot])
	data=[]


	return time_sheet

def get_conditions(filters):
	conditions=""
	if filters.get("from_date"): conditions += " and r.date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and r.date <= %(to_date)s"
	if filters.get("employee"): conditions += " and r.employee = %(employee)s"	
		
	return conditions
