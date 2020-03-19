# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _


def execute(filters=None):
	if not filters: 
		filters = {}

	columns, data= [], []

	conditions, filters = get_conditions(filters)
	columns = get_columns()
	data = get_attendance_list(conditions, filters)

	return columns, data



def get_columns():
	columns = [
		 {"label":_("Employee Name") ,"width":140,"fieldtype": "Data"},
 		 {"label":_("Department") ,"width":100,"fieldtype": "Data"},
 		 {"label":_("Designation") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Day") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Attendance Date") ,"width":100,"fieldtype": "Date"},
 		 {"label":_("Attendance Time") ,"width":100,"fieldtype": "Time"},
		# {"label":_("Departure Time") ,"width":100,"fieldtype": "Time"}
	]
	
	return columns


def get_attendance_list(conditions, filters):
	data= []
	att_list= frappe.db.sql("""select distinct att.attendance_date, emp.employee_name, att.name as attname,emp.name,
		emp.name , DAYNAME(att.attendance_date) as day,att.attendance_time,
		att.status ,emp.designation,emp.department from `tabEmployee` as emp 
		join tabAttendance as att on att.employee=emp.name and discount_salary_from_leaves=0 and att.docstatus = 1 
		where 1 %s order by emp.name, att.attendance_date""" %conditions, filters, as_dict=1)
	for att in att_list:
		if att.employee_name and  not is_indeparture_list(att.name,att.attendance_date):
			row = [att.employee_name, att.department,att.designation,_(att.day), att.attendance_date, att.attendance_time]
			data.append(row)
	return data


def is_indeparture_list(employee,attendance_date):
	isExist= False
	dep_list = frappe.db.sql("""select departure_date ,employee from tabDeparture 
		where employee=%s and docstatus = 1 and departure_date =%s""" , (employee,attendance_date), as_dict=1)
	if dep_list:
		isExist= True
	else: isExist= False
	return isExist

def get_conditions(filters):
	conditions = ""
	if filters.get("employee"): conditions += " and emp.name = %(employee)s"
	if filters.get("designation"): conditions += " and emp.designation >= %(designation)s"
	if filters.get("department"): conditions += " and emp.department <= %(department)s"
	if filters.get("from_date"): conditions += " and att.attendance_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and att.attendance_date <= %(to_date)s"

	return conditions, filters

