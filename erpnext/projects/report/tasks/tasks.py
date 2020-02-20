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
	return [_("Task") + "::250", 
		_("Project") + ":Link/Project:120", 
		_("Task Created By") + "::120",
		_("Created By Employee Name") + "::120",
		_("Employee") + ":Link/Employee:120",
		_("Employee Name") + "::150", 
		_("Expected Time") + ":Float:100",
		
]

def get_data(conditions, filters):
	result=[]
	time_sheet = frappe.db.sql("""select t.name,t.subject ,t.project ,t.user,t.employee_name from `tabTask` as t  where t.docstatus <2 %s order by t.project"""%(conditions), filters, as_list=1)
	for task in time_sheet:
		flag=True
		det=None
		if filters.get("employee"):
			det=frappe.get_list("Task Details",['employee','employee_name', 'expected_time_in_hours'],filters={"parent": task[0] ,"employee":filters.get("employee")})
		else:
			det=frappe.get_list("Task Details",['employee','employee_name', 'expected_time_in_hours'],filters={"parent": task[0] ,"employee":filters.get("employee")})
	
		if len(det) == 0:
			result.append([task[1] ,task[2] ,task[3],task[4],"","",""])
		else:
		
			for d1 in det:
				if flag:
					result.append([task[1] ,task[2] ,task[3],task[4] ,d1.employee,d1.employee_name, d1.expected_time_in_hours])
					flag=False
				else:
					result.append(["","" ,"","" ,d1.employee,d1.employee_name, d1.expected_time_in_hours])
			
					
		

	return result

def get_conditions(filters):
	conditions=""
	if filters.get("project"): conditions += " and t.project >= %(project)s"
	if filters.get("user"): conditions += " and t.user >= %(user)s"

	return conditions
