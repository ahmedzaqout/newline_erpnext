# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _


def execute(filters=None):
	if not filters: 
		filters = {}

	columns, data = [], []

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	att_list = get_attendance_list(conditions, filters)
	
	for att in sorted(att_list):
		row = [att.employee_name, att.management,att.designation,att.day, att.attendance_date]
		data.append(row)
	return columns, data



def get_columns(filters):
	columns = [
		 {"label":_("Employee Name") ,"width":100,"fieldtype": "Data"},
 		 {"label":_("Department") ,"width":100,"fieldtype": "Data"},
 		 {"label":_("Designation") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Attendance Date") ,"width":80,"fieldtype": "Date"},
		 {"label":_("Day") ,"width":70,"fieldtype": "Data"}
	]
	
	return columns


def get_attendance_list(conditions, filters):
	return frappe.db.sql("""select distinct att.attendance_date, emp.employee_name, emp.employee ,dept.departure_date, DAYNAME(att.attendance_date) as day,
		att.status ,emp.designation,emp.department from `tabEmployee Employment Detail` as emp   
		join  tabAttendance as att on att.employee=emp.employee and discount_salary_from_leaves=0 and att.docstatus = 1
		join  tabDeparture as dept on dept.employee=emp.employee and att.attendance_date=dept.departure_date and dept.docstatus = 1
		where  %s order by emp.employee, attendance_date""" %conditions, filters, as_dict=1)


def get_conditions(filters):
	conditions = ""
	if filters.get("employee"): conditions += " emp.employee = %(employee)s"
	if filters.get("designation"): conditions += " and att.designation >= %(designation)s"
	if filters.get("department"): conditions += " and att.department <= %(department)s"

	return conditions, filters

