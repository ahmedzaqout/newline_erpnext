# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.utils import  getdate



def execute(filters=None):
	if not filters: 
		filters = {}

	columns, data = [], []

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	data = get_attendance_list(conditions, filters,data)
	
	#for att in sorted(att_list):
	#	row = [att.employee_name, att.management,att.designation,att.day, att.attendance_date]
	#	data.append(row)
	return columns, data



def get_columns(filters):
	columns = [
		 {"label":_("Employee Name") ,"width":150,"fieldtype": "Data"},
 		 {"label":_("Department") ,"width":150,"fieldtype": "Data"},
 		 {"label":_("Designation") ,"width":150,"fieldtype": "Data"},
		 {"label":_("Day") ,"width":80,"fieldtype": "Data"},
		 {"label":_("Attendance Date") ,"width":120,"fieldtype": "Date"},
		 {"label":_("Status") ,"width":70,"fieldtype": "Data"}
	]
	return columns


def get_attendance_list(conditions, filters, data):
	attList= frappe.db.sql("""select distinct att.attendance_date, emp.employee_name, emp.name as employee ,dept.departure_date, DAYNAME(att.attendance_date) as day,
		att.status, emp.designation,emp.department from `tabEmployee` as emp   
		join  tabAttendance as att on att.employee=emp.name and att.discount_salary_from_leaves=0 and att.docstatus = 1
		join  tabDeparture as dept on dept.employee=emp.name and att.attendance_date=dept.departure_date and dept.docstatus = 1
		where att.status ='Absent' %s order by emp.name, attendance_date""" %conditions, filters, as_dict=1)
	for att in attList:
		if att.employee_name and  not is_inleave_list(att.employee,att.attendance_date):
			row = [att.employee_name, att.department,att.designation,att.day, att.attendance_date, att.status]
			data.append(row)
	return data


def is_inleave_list(employee,attendance_date):
	isExist= False
	leave_list = frappe.db.sql("""select employee,from_date,to_date,docstatus from `tabLeave Application` where employee =%s and
	 docstatus = 1 and (%s between from_date and to_date) """ , (employee,getdate(attendance_date)), as_dict=1)
	if leave_list:
		isExist= True
	else: isExist= False
	return isExist


def get_conditions(filters):
	conditions = ""
	if filters.get("employee"): conditions += " emp.name = %(employee)s"
	if filters.get("designation"): conditions += " and emp.designation = %(designation)s"
	if filters.get("department"): conditions += " and emp.department = %(department)s"
	if filters.get("from_date"): conditions += " and att.attendance_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and att.attendance_date <= %(to_date)s"

	return conditions, filters

