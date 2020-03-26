# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from erpnext.hr import get_emp_work_shift

def execute(filters=None):
	data, columns, row =[], [] ,[]
	if not filters: filters = {}
	conditions, filters = get_conditions(filters)
	columns = get_columns()
	leave_data = get_data(conditions, filters)
	for d in sorted(leave_data):
		disc_leavs_indays = 0.0
		emp_shif_hrs= get_emp_work_shift(d.name, d.day)
		if (d.disc_leavs != "NULL" or d.disc_leavs is not None) and emp_shif_hrs:
			disc_leavs_indays = d.disc_leavs / emp_shif_hrs
		row =[ d.name,d.employee_name,d.attendance_date, disc_leavs_indays, d.disc_leavs ]
		data.append(row)

	return columns, data


def get_columns():
	return [
		 {"label":_("Employee Number") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Employee Name") ,"width":160,"fieldtype": "Data"},
		 {"label":_("Discount Date") ,"width":140,"fieldtype": "Data"},
		 {"label":_("Discount Value/ Days") ,"width":140,"fieldtype": "Data"},
		 {"label":_("Discount Value/ Hours") ,"width":140,"fieldtype": "Data"}
	]


def get_conditions(filters):
	conditions = ""
	if filters.get("month"):
		month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
			"Dec"].index(filters["month"]) + 1
		conditions += " and month(att.attendance_date) = '%s'" % month
	if filters.get("year"): conditions += " and  year(att.attendance_date) = %(year)s"
	if filters.get("employee"): conditions += " and emp.name = %(employee)s" 
	if filters.get("company"): conditions += " and emp.company = %(company)s"
	if filters.get("department"): conditions += " and emp.department = %(department)s"
	return conditions, filters


def get_data(conditions, filters): 
	return frappe.db.sql("""select distinct att.attendance_date, emp.employee_name,emp.name , DAYNAME(att.attendance_date) as day,\
att.attendance_time, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as disc_leavs \
from `tabEmployee` as emp join tabAttendance as att on att.employee=emp.name and att.discount_salary_from_leaves=1 and att.docstatus = 1 \
left join  tabDeparture as dept on dept.employee=emp.name and att.attendance_date=dept.departure_date and dept.docstatus = 1 where 1  %s order by emp.name, att.attendance_date """ %conditions, filters, as_dict=1)



	 # """select distinct mm.attendance_date, dayname(mm.attendance_date) as att_day, mm.attendance_time,emp.employee_name,emp.name ,emp.department,emp.company, mm.departure_time, ifnull(mm.disc_leavs,'0') as disc_leavs from `tabEmployee` as emp \
	 #  join (select distinct att.attendance_date, att.attendance_time,att.employee, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as disc_leavs\
	 #  from tabAttendance as att join tabDeparture as dept on att.attendance_date=dept.departure_date and  att.discount_salary_from_leaves=1 and att.docstatus = 1 and dept.docstatus = 1) as mm\
	 #  on emp.name= mm.employee and 1 %s \
	 # order by mm.attendance_date asc""" 
