# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _

def execute(filters=None):

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)

	data = salaries(conditions, filters)
	

	return columns, data


def get_columns(filters):
	columns = [
		 {"label":_("Employee Name") ,"width":100,"fieldtype": "link","options":"Employee"},
		 {"label":_("Designation") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Departement") ,"width":100,"fieldtype": "Date"},
		 {"label":_("Hour Cost") ,"width":90,"fieldtype": "Float"},
		 {"label":_("Working Hours") ,"width":90,"fieldtype": "Float"},
		 {"label":_("Actual Working Hour") ,"width":90,"fieldtype": "Float"},
		 {"label":_("Total Earning") ,"width":100,"fieldtype": "Float"},
		 {"label":_("Total Deduction") ,"width":100,"fieldtype": "Float"},
		 {"label":_("Total") ,"width":100,"fieldtype": "Float"},
	]
	
	return columns

def salaries(conditions, filters):
	data=[]
	hours={}
	ss  = frappe.db.sql("""select ss.* from `tabSalary Slip` as ss where docstatus <2 %s 
		order by employee """ %
		conditions, filters, as_dict=1)

	con = ""
	if filters.get("start_date"): con += " where att.attendance_date >= %(start_date)s"
	if filters.get("end_date"): con += " and att.attendance_date <= %(end_date)s"
	if filters.get("employee"): con += " and emp.name= %(employee)s"



	hours = {}
	rr="""select emp.name as employee ,sum(GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0)) as total_hours 
		,emp.work_hrs from tabEmployee as emp 
		join  tabAttendance as att on att.employee=emp.name  and att.docstatus = 1 
		left join  tabDeparture as dept on dept.employee=emp.name and 
		att.attendance_date=dept.departure_date and dept.docstatus = 1 """+con+""" group by emp.name"""
	emp_hours=frappe.db.sql(rr, filters, as_dict=1)
	
	
	

	for m in emp_hours:
		# frappe.msgprint()
		hours[m.employee]={"total":m.total_hours,"workshift":m.work_hrs}


	for d in ss:
		if hours.has_key(d.employee):
			data.append([d.employee,d.designation,d.department,d.hour_cost,hours[d.employee]['total'],hours[d.employee]['workshift'],d.gross_pay,d.total_deduction,d.net_pay])
		else:
			data.append([d.employee,d.designation,d.department,d.hour_cost,0,8,d.gross_pay,d.total_deduction,d.net_pay])



	return data




def get_conditions(filters):
	conditions = ""
	if filters.get("start_date"): conditions += " and ss.start_date >= %(start_date)s"
	if filters.get("end_date"): conditions += " and ss.end_date <= %(end_date)s"
	if filters.get("employee"): conditions += " and ss.employee = %(employee)s"
	if filters.get("department"): conditions += " and ss.department = %(department)s"
	if filters.get("company"): conditions += " and ss.company = %(company)s"

	return conditions, filters