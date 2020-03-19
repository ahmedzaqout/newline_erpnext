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
	data = get_departure_list(conditions, filters)

	return columns, data



def get_columns():
	columns = [
		 {"label":_("Employee Name") ,"width":140,"fieldtype": "Data"},
 		 {"label":_("Department") ,"width":100,"fieldtype": "Data"},
 		 {"label":_("Designation") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Day") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Departure Date") ,"width":100,"fieldtype": "Date"},
		 {"label":_("Departure Time") ,"width":100,"fieldtype": "Time"}
	]
	
	return columns


def get_departure_list(conditions, filters):
	data= []
	att_list= frappe.db.sql("""select distinct att.departure_date, emp.employee_name, att.name as attname,emp.name, DAYNAME(att.departure_date) as day,att.departure_time,
		att.status ,emp.designation,emp.department from `tabEmployee` as emp 
		join tabDeparture as att on att.employee=emp.name and att.docstatus = 1 
		where 1 %s order by emp.name, att.departure_date""" %conditions, filters, as_dict=1)
	for att in att_list:
		if att.employee_name and not  is_inattendance_list(att.name,att.departure_date):
			row = [att.employee_name, att.department,att.designation,_(att.day), att.departure_date, att.departure_time]
			data.append(row)
	return data


def is_inattendance_list( employee, departure_date):
	conditions = ""
	isExist= False
	dep_list = frappe.db.sql("""select distinct attendance_date  ,employee from tabAttendance 
		where employee=%s and docstatus = 1 and attendance_date =%s""" , (employee,departure_date), as_dict=1)
	if dep_list:
		isExist= True
	else: isExist= False
	return isExist


def get_conditions(filters):
	conditions = ""
	if filters.get("employee"): conditions += " and emp.name = %(employee)s"
	if filters.get("designation"): conditions += " and emp.designation >= %(designation)s"
	if filters.get("department"): conditions += " and emp.department <= %(department)s"
	if filters.get("from_date"): conditions += " and att.departure_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and att.departure_date <= %(to_date)s"

	return conditions, filters
