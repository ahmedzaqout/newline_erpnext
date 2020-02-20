# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _

def execute(filters=None):
	data, columns, row =[], [] ,[]
	if not filters: filters = {}
	conditions, filters = get_conditions(filters)
	columns = get_columns()
	leave_data = get_data(conditions, filters)
	for d in sorted(leave_data):
		row =[ d.employee,d.employee_name,d.attendance_date,float(d.disc_leavs) ]
		data.append(row)

	return columns, data


def get_columns():
	return [
		 {"label":_("Employee Number") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Employee Name") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Discount Date") ,"width":80,"fieldtype": "Data"},
		 {"label":_("Discount Value") ,"width":80,"fieldtype": "Float"}
	]


def get_conditions(filters):
	conditions = ""
	if filters.get("month"):
		month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
			"Dec"].index(filters["month"]) + 1
		conditions += " and month(att.attendance_date) = '%s'" % month
	if filters.get("year"): conditions += " and  year(att.attendance_date) = %(year)s"
	if filters.get("employee"): conditions += " and emp.employee = %(employee)s" 
	if filters.get("company"): conditions += " and emp.company = %(company)s"
	if filters.get("department"): conditions += " and emp.department = %(department)s"
	return conditions, filters


def get_data(conditions, filters): 
	return frappe.db.sql("""select distinct att.attendance_date, emp.employee_name,emp.employee, att.attendance_time, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as disc_leavs from `tabEmployee Employment Detail` as emp join  tabAttendance as att on att.employee=emp.employee and discount_salary_from_leaves=1 and att.docstatus = 1 join  tabDeparture as dept on dept.employee=emp.employee and att.attendance_date=dept.departure_date and dept.docstatus = 1 %s order by att.attendance_date asc""" %conditions, filters, as_dict=1)


