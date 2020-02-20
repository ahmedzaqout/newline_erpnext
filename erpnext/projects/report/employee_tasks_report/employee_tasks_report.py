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
		_("Project") + ":Link/Project:120", 
		_("Task") + ":Link/Task:200",
		_("Date") + ":Link/Project:120",
		_("Hours") + ":float:100"
]

def get_data(conditions, filters):
	time_sheet = frappe.db.sql("""select r.employee ,r.employee_name , td.project, td.task, r.date,
		td.hours  from `tabActivity Detail` as td left join  `tabEmployee Task` as r on r.name = td.parent where r.docstatus <2  %s order by r.date """%(conditions), filters, as_list=1)
	tot=0
	for n in time_sheet:
		tot=tot+n[5]
	time_sheet.append(["","","","", "Total" ,tot])
	data=[]


	return time_sheet

def get_conditions(filters):
	conditions=""
	if filters.get("from_date"): conditions += " and r.date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and r.date <= %(to_date)s"
	if filters.get("project"): conditions += " and td.project = %(project)s"
	if filters.get("employee"): conditions += " and r.employee = %(employee)s"	
	if filters.get("task"): conditions += " and td.task = %(task)s"	
	if filters.get("task_category"): conditions += " and td.task_category = %(task_category)s"	
	return conditions
