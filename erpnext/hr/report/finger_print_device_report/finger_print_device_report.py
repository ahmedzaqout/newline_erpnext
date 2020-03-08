# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from datetime import datetime
import time
from time import strptime


#from erpnext.hr.doctype.finger_print_device_control_panel.finger_print_device_control_panel import upload_attendance

def execute(filters=None):
	if not filters: 
		filters = {}

	columns, data= [], []

	conditions, filters = get_conditions(filters)
	columns = get_columns()
	device_data = get_data(conditions, filters)
	for d in sorted(device_data):
		row =[d.employee_name,d.fp_id,d.date,d.day,d.att,d.dep,d.exitt,d.ret]
		data.append(row)
	return columns, data



def get_columns():
	columns = [
		 {"label":_("Employee Name") ,"width":140,"fieldtype": "Data"},
		 {"label":_("Finger Print ID") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Attendance Date") ,"width":100,"fieldtype": "Date"},
		 {"label":_("Day") ,"width":70,"fieldtype": "Data"},
		 {"label":_("Attendance Time") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Departure Time") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Exit Permision Time") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Return Permision Time") ,"width":130,"fieldtype": "Data"}
	]
	return columns


def get_conditions(filters):
	conditions = ""
	if filters.get("employee"): conditions += "  and emp.employee = %(employee)s"
	#if filters.get("company"): conditions += " and emp.company >= %(company)s"
	#if filters.get("month"): conditions+= "  and DATE_FORMAT(fpd.time, '%%d') = %(month)s" 
	if filters.get("year"): conditions+= "  and year(fpd.time) = %(year)s"

	return conditions, filters


def get_data(conditions, filters): 
	if filters.get("month"): 
		month = strptime(filters.get("month"),'%b').tm_mon 
		conditions+= "  and month(fpd.time) = %s"%(month )

	return frappe.db.sql("""select employee_name,fp_id, max(att) as att, max(dep) as dep, max(exitt) as exitt, max(ret) as ret,date,day from 
	 (select employee_name,fp_id,employee, if(punch=1,Time(fpd.time),Time(0)) as att,if(punch=2,Time(fpd.time),Time(0)) as dep,
	 if(punch=3,Time(fpd.time),Time(0)) as exitt, if(punch=4,Time(fpd.time),Time(0)) as ret, Date(fpd.time) as date,
	 DAYNAME(Date(fpd.time)) as day, punch from `tabEmployee Personal Detail` as emp join `tabFinger Print Data` as fpd 
	 on emp.fp_id = fpd.user_id  %s order by emp.employee ) as s group by employee_name,fp_id,date """% conditions, filters, as_dict=1)




		
		


