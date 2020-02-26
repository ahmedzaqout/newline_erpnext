# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime, calendar, time
import calendar
from frappe.utils import add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words,today,time_diff_in_hours
from frappe import _

def execute(filters=None):
	columns, data = [], []
	conditions, filters = get_conditions(filters)
	columns = get_columns(conditions,filters)
	data = getdata(conditions, filters)
	return columns, data


def get_columns(conditions,filters):
	columns = [
		 {"label":_("Emplyee") ,"width":150,"fieldtype": "Data"},
		{"label": "Saturday","width":120,"fieldtype": "Data"},
		{"label": "Sunday","width":120,"fieldtype": "Data"},
		{"label": "Monday","width":120,"fieldtype": "Data"},
		{"label": "Tuesday","width":120,"fieldtype": "Data"},
		{"label": "Wednesday","width":120,"fieldtype": "Data"},
		{"label": "Thursday","width":120,"fieldtype": "Data"},
		{"label": "Friday","width":120,"fieldtype": "Data"},
		]
	





	return columns

def get_employees(conditions, filters):
	return frappe.db.sql("""select em.name,em.employee_name from `tabEmployee` as em left Join `tabEmployee Employment Detail` as ed on em.employee=ed.employee  where em.docstatus <2 %s order by em.name """% conditions, filters, as_dict=1)

def getdata(conditions, filters):
	data=[]

	emps = get_employees(conditions, filters)
	dayyy= (datetime.datetime.today().weekday()+2)%7
	today = datetime.datetime.today()
	sdate= today + datetime.timedelta(days=(-1*dayyy))
	for emp in emps:
		row2=["",]
		if emp.employee_name:
			row =[emp.employee_name]
		else:
			row =[emp.name]
		for i in range( (7)):
    			day = sdate + datetime.timedelta(days=i)
		
			total_work_hrs, start_work, end_work,next_day,next_total_work_hrs = get_wsh_history(emp.name, getdate(day))
			if next_day and next_day==1:
				emp_map  = frappe.db.sql("""select  att.attendance_date, dept.departure_date,att.attendance_time, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as total_hours ,GREATEST(24-round((TIMESTAMPDIFF(MINUTE,dept.departure_time,att.attendance_time))/60,3),0) as next_total_hrs ,att.status 
	from tabAttendance as att left join  tabDeparture as dept on att.employee=dept.employee and date_add(att.attendance_date,interval 1 day)  =dept.departure_date and dept.docstatus = 1 and att.docstatus=1  where att.docstatus=1  and dept.docstatus = 1 and att.employee= '{0}' and att.attendance_date = '{1}' """.format(emp.name,getdate(day)), as_dict=1)
			else:
				emp_map  = frappe.db.sql("""select  att.attendance_date, dept.departure_date,att.attendance_time, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as total_hours ,GREATEST(24-round((TIMESTAMPDIFF(MINUTE,dept.departure_time,att.attendance_time))/60,3),0) as next_total_hrs ,att.status 
		from tabAttendance as att join  tabDeparture as dept on att.employee=dept.employee and att.attendance_date=dept.departure_date and dept.docstatus = 1 and att.docstatus=1  where att.docstatus=1  and dept.docstatus = 1  and att.employee= '{0}' and att.attendance_date = '{1}' """.format(emp.name,getdate(day)), as_dict=1)
			attend=""
			dep=""
			total_ho=0
			next_total_hrs=0
			status=""
			total=0.0
			attend=""
			dep=""
			total_ho=0
			next_total_hrs=0
			status=""
			if not next_day:
				next_day=0
			shift_name=str(start_work)+"-"+str(end_work)
			if emp_map:
				attend=emp_map[0].attendance_time
				dep=emp_map[0].departure_time
				total_ho=emp_map[0].total_hours
				shi= frappe.get_all("Shift Time",['name'],filters={"start_time":start_work,"end_time":end_work,"next_day":next_day})
				if shi:
					shift_name= shi[0].name


			if not start_work:
				row.append(_("Holiday"))
				row2.append("")
			else:
				row.append(shift_name)
				row2.append((str(attend)+"-"+str(dep)))
		
		data.append(row)
		data.append(row2)
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
