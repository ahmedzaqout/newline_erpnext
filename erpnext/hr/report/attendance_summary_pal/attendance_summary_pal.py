# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
#Added by Maysaa 29/02/2020

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate, time_diff_in_hours, get_time,add_days
from frappe import msgprint, _
import datetime, calendar, time
from calendar import monthrange
import math 
from datetime import datetime
from erpnext.hr import get_permissions, get_overtime_hrs,get_emp_work_shift
from erpnext.hr.doctype.leave_application.leave_application import get_leaves_for_period

def execute(filters=None):
	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	data = get_data(conditions, filters)
	return columns, data

def get_columns(filters):
	columns = [
		 {"label":_("Employee Name") ,"width":150,"fieldtype": "Data"},
		 {"label":_("Supervisor") ,"width":140,"fieldtype": "Data"},
		 {"label":_("Department") ,"width":140,"fieldtype": "Data"},
 		 {"label":_("Total Work Hours") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Morning Late Count") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Morning Late") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Early Count") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Eearly Departure Hours") ,"width":90,"fieldtype": "Int"},
 		 {"label":_("Overtime Count") ,"width":90,"fieldtype": "Data"},
 		 {"label":_("Overtime Hours") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Discount Hours") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Exit Permission Count") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Exit Permission") ,"width":90,"fieldtype": "Data"},
		 {"label":_("On Leave") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Absence") ,"width":90,"fieldtype": "Int"}
		 		 ]		
	return columns

def get_data(conditions, filters):
	data=[]
	hours={}
	condition = ""
	from_date = filters.get('from_date')
	to_date = filters.get('to_date')
	if filters.get("supervisor"): condition += " and ed.supervisor = %(supervisor)s"
	if filters.get("department"): condition += " and ed.department = %(department)s"
	if filters.get("employee"): condition += " and emp.name = %(employee)s"

	employees  = frappe.db.sql("""select name as employee ,employee_name ,supervisor,department, status from `tabEmployee`  
	 					 where docstatus <2 and status = "Active" %s order by employee """% (condition),filters, as_list=1)

	for emp_data in employees:
		emp_details = get_employee_details (conditions, filters,emp_data[0])

		total_late=0.0
		total_early =0.0
		early_hrs_count=0
		total_abs=0
		onleavs=0
		exit_permision=0
		disc=0
		total_over=0
		total_ex=0
		dont_write_report=0
		write_late=0
		total_att = 0
		over_count =0
		late_hrs_count= 0
		abs_hrs = 0.0
		
		#leaves_taken = get_leaves_for_period(emp_data[0], leave_type,from_date, to_date) * -1
		total_over, over_count = get_overtime_hrs(emp_data[0],from_date,to_date) 
		exit_permision= get_permissions(emp_data[0],from_date,to_date )


		for att in emp_details:
			if att.total_hours:
				total_att += att.total_hours
				#if att.total_work_hrs > att.total_hours :
				#diff = (float(att.total_work_hrs) - float(att.total_hours))
			if att.discount:
				disc += att.discount
				#else: disc += 0.0

			if att.early_departure:
				total_early += att.early_departure
				early_hrs_count += 1

			if att.late_hrs:
				total_late += att.late_hrs
				late_hrs_count += 1

			if(att.status == "Absent"):
				total_abs+=1
				emp_wsh = get_emp_work_shift(emp_data[0],att.day)
				if emp_wsh: abs_hrs+= (total_abs* emp_wsh)
			if(att.status == "On Leave"):
				onleavs+=1  

			#if att.total_work_hrs and att.total_hours :
			#	if att.total_work_hrs > att.total_hours :
			#		disc += (float(att.total_work_hrs) - float(att.total_hours))

			if att.ext_diff> 0 :
				total_ex+=1

		if emp_data[1]:
			data.append([emp_data[1],emp_data[2],emp_data[3],round(total_att,2), late_hrs_count, round(total_late,2), early_hrs_count,round(total_early,2),over_count,round(total_over,2),round((disc + abs_hrs - (exit_permision+total_over)),2),total_ex,exit_permision,onleavs,total_abs])

	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"): conditions += " and att.attendance_date >=  %(from_date)s"
	if filters.get("to_date"): conditions += " and att.attendance_date <= %(to_date)s"
	return conditions, filters


def get_employee_details(conditions, filters,employee): 
	emp_map  = frappe.db.sql("""select distinct att.attendance_date, emp.employee_name, att.name as attname,dept.name as deptname, emp.name ,dept.departure_date, DAYNAME(att.attendance_date) as day,att.attendance_time, dept.departure_time,
		GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as total_hours ,
		GREATEST(round((TIMESTAMPDIFF(MINUTE,shd.start_work,shd.end_work))/60,3),0) as total_work_hrs,ifnull((GREATEST(round((TIMESTAMPDIFF(MINUTE,shd.start_work,shd.end_work))/60,3),0) - GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) ),0) as discount,ifnull(overtime_hours,0) as overtime_hours,ifnull(tsh.holiday_overtime_hours,0) as holiday_overtime_hours,compensatory,tsh.type, tsh.from_time ,att.status,shd.start_work, ifnull(ext.early_diff,0) as early_departure,ifnull(ext.ext_diff,0) as ext_diff, work_shift, emp.holiday_list,ifnull(GREATEST(round(TIMESTAMPDIFF(MINUTE,shd.start_work,att.attendance_time)/60,2),0),0) as late_hrs from `tabEmployee` as emp   
	join  tabAttendance as att on att.employee=emp.name and att.discount_salary_from_leaves=0 and att.docstatus = 1
	left join  tabDeparture as dept on dept.employee=emp.name and att.attendance_date=dept.departure_date and dept.docstatus = 1
	left join `tabWork Shift Details` as shd on shd.parent =  work_shift and shd.day = DAYNAME(att.attendance_date)
	left join (select t.docstatus,employee,from_time,ifnull(sum(CASE WHEN type='compensatory' THEN hours END),0) as compensatory, ifnull(sum(CASE WHEN type='Normal' THEN hours END),0) as overtime_hours, ifnull(sum(CASE WHEN type='With Leave' THEN hours END),0) as holiday_overtime_hours,type from tabTimesheet as t join `tabTimesheet Detail` as td on t.name=td.parent and t.docstatus=1 group by date(from_time),employee) as tsh on emp.name=tsh.employee and att.attendance_date=date(tsh.from_time) and tsh.docstatus = 1 
	left join (select employee,depstat,exitstat, permission_date,sum(early_diff)/60 as early_diff, sum(diff) as ext_diff from (
	select employee,docstatus as depstat,0 as exitstat, permission_date,early_diff, 0 as diff from `tabExit permission` where permission_type='Early Departure' and docstatus = 1
	union all 
	select employee,0 as depstat,docstatus as exitstat, permission_date,0 as early_diff ,TIME_TO_SEC(diff_exit)/3600 as diff from `tabExit permission` where type='Return' and permission_type='Exit with return' and docstatus = 1) as d group by permission_date,employee) as ext 
	on emp.name=ext.employee and att.attendance_date=ext.permission_date 
	where 1 %s and att.employee = '%s' order by emp.name, attendance_date"""% (conditions,employee), filters, as_dict=1)
	return emp_map


