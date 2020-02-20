# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words,today,time_diff_in_hours


from frappe import _
from calendar import monthrange
import datetime, calendar, time
import calendar






def execute(filters=None):

	conditions, filters = get_conditions(filters)
	columns = get_columns(conditions,filters)
	data = getdata(conditions, filters)
	return columns, data


def get_columns(conditions,filters):
	columns = [
		 {"label":_("Emplyee") ,"width":150,"fieldtype": "Data"},
		]
	
	emps = get_employees(conditions, filters)
	month=int(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov","Dec"].index(filters.get("month")))+1
	month_range= monthrange(cint(datetime.datetime.now().year), month)[1]

	sdate= datetime.datetime.strptime(str(datetime.datetime.now().year)+"-"+str(month)+"-"+"01", '%Y-%m-%d')
	emps = get_employees(conditions, filters)
	for i in range(month_range):
    		day = sdate + datetime.timedelta(days=i)
		columns += [{"label": day.strftime("%m-%d-%Y") ,"width":70,"fieldtype": "Data"},]

	#for emp in emps:
	#	if emp.employee_name:
	#		columns += [{"label": emp.employee_name ,"width":130,"fieldtype": "Data"},]
	#	else:
	#		columns += [{"label": emp.name ,"width":70,"fieldtype": "Data"},]


	return columns

def get_employees(conditions, filters):
	return frappe.db.sql("""select em.name,em.employee_name from `tabEmployee` as em left Join `tabEmployee Employment Detail` as ed on em.employee=ed.employee  where em.docstatus <2 %s order by em.name """% conditions, filters, as_dict=1)

def getdata(conditions, filters):
	data=[]
	month=int(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov","Dec"].index(filters.get("month")))+1
	month_range= monthrange(cint(datetime.datetime.now().year), month)[1]

	sdate= datetime.datetime.strptime(str(datetime.datetime.now().year)+"-"+str(month)+"-"+"01", '%Y-%m-%d')
	emps = get_employees(conditions, filters)
	for emp in emps:
		if emp.employee_name:
			row =[emp.employee_name]
		else:
			row =[emp.name]
		for i in range(0,month_range):
    			day = sdate + datetime.timedelta(days=i)
		
			total_work_hrs, start_work, end_work,next_day,next_total_work_hrs = get_wsh_history(emp.name, getdate(day))
			if not start_work:
				row.append(_("Holiday"))
			else:
				row.append("")
		
		data.append(row)
	return data

def get_wsh_history(employee,ddate):
	total_work_hrs = 0
	start_work, end_work ='', ''
	next_day=0
	next_total_work_hrs=0
	#conditions = " employee = %s and %s <= shift_change_date",(filters.get("employee"), ddate)
	work_shift = frappe.db.sql("""select work_shift from `tabWork Shift History` where  employee = %s and  %s >= shift_change_date  order by shift_change_date Desc limit 1""",(employee, ddate), as_dict=1)
	if work_shift:
		day = calendar.day_name[getdate(ddate).weekday()];
		doc = frappe.db.sql("select GREATEST(round((TIMESTAMPDIFF(MINUTE,start_work,end_work))/60,3),0) as total_work_hrs, GREATEST(24-round((TIMESTAMPDIFF(MINUTE,end_work,start_work))/60,3),0) as next_total_work_hrs, start_work,end_work ,next_day from `tabWork Shift Details`  where parent =  '{0}' and day = '{1}'".format(work_shift[0].work_shift, day),as_dict=1)
		
		if doc:
			total_work_hrs= doc[0].total_work_hrs 
			start_work= doc[0].start_work
			end_work= doc[0].end_work
			next_day= doc[0].next_day
			next_total_work_hrs= doc[0].next_total_work_hrs


	return total_work_hrs, start_work, end_work,next_day,next_total_work_hrs


def get_conditions(filters):
	conditions = ""
	if filters.get("circle"): conditions += " and ed.circle = %(circle)s"
	if filters.get("department"): conditions += " and ed.department = %(department)s"
	if filters.get("employee"): conditions += " and ed.employee = %(employee)s"


	return conditions, filters
