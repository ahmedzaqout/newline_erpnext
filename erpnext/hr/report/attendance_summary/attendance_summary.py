# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate, time_diff_in_hours, get_time
from frappe import msgprint, _
import datetime, calendar, time
from calendar import monthrange
import math 
from datetime import datetime
# from math import float ,round
import time
from frappe.utils import add_days

def execute(filters=None):
	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	data = get_data(conditions, filters)
	return columns, data

def get_columns(filters):
	columns = [
		 {"label":_("Employee") ,"width":100,"fieldtype": "link","options":"Employee"},\
		 {"label":_("Employee Name") ,"width":150,"fieldtype": "Data"},
		 {"label":_("Early") ,"width":70,"fieldtype": "Data"},
		 {"label":_("Late") ,"width":70,"fieldtype": "Data"},
		 {"label":_("On Leave") ,"width":70,"fieldtype": "Data"},
		 {"label":_("Absence") ,"width":70,"fieldtype": "Int"},
		 {"label":_("Overtime") ,"width":70,"fieldtype": "Data"},
		 {"label":_("Discount") ,"width":70,"fieldtype": "Data"},
		 {"label":_("Exit Permission") ,"width":80,"fieldtype": "Int"},
		 {"label":_("Eearly Departure") ,"width":80,"fieldtype": "Int"},
		 {"label":_("Not Write Report") ,"width":80,"fieldtype": "Int"},
		 {"label":_("Write Report late") ,"width":80,"fieldtype": "Int"},
		 ]
		
	return columns

def get_data(conditions, filters):
	data=[]
	hours={}
	ss  = frappe.db.sql("""select name as employee ,employee_name , status from `tabEmployee`  where docstatus <2 and status = "Active" order by name """, as_list=1)
	
	for add in ss:
		det = get_employee_details (conditions, filters,add[0])

		total_late=0
		total_early=0
		total_abs=0
		leavess=0
		overtime=0
		exit_permision=0
		disc=0
		total_over=0
		total_ex=0
		total_earl=0
		dont_write_report=0
		write_late=0

		
		ss="""select sum(l.total_leave_days)  from `tabLeave Application` l where l.employee = '{0}' and l.docstatus =1  and l.from_date >=  '{1}' and l.to_date <= '{2}' """.format(add[0] ,filters.get('from_date'),filters.get('to_date'))
		over= """select sum(l.total_hours)  from `tabTimesheet` l where l.employee = '{0}' and l.docstatus =1  and l.start_date >=  '{1}' and l.end_date <= '{2}' """.format(add[0] ,filters.get('from_date'),filters.get('to_date'))
		lea = frappe.db.sql(ss , as_list=1)
		ovr_rate = frappe.db.get_value("HR Settings", None, "overtime_hour_price")
		overtime_hour_price_in_holidays = frappe.db.get_value("HR Settings", None, "overtime_hour_price_in_holidays")

		# if (lea):
		# if lea[0][0]:
		#  		leavess = lea[0][0]
		# if (over):
		# if over[0][0]:
		# 	overtime = over[0][0]


		for dd in det:
			if dd.late_hrs <= 0.25 and dd.status =="Present":
				total_early+=1
			if(dd.late_hrs >= 1 and dd.status =="Present"):
				total_late+=1
			if(dd.status == "Absent"):
				total_abs+=1
			if(dd.status == "On Holiday"):
				leavess+=1  
		
			if dd.overtime_hours:
				over = dd.overtime_hours * float(ovr_rate)
				total_over += over

			if dd.holiday_overtime_hours:
				over = dd.holiday_overtime_hours * float(overtime_hour_price_in_holidays)
				total_over += over


			if dd.total_work_hrs and dd.total_hours :
				if dd.total_work_hrs > dd.total_hours :
					disc += float(dd.total_work_hrs) - float(dd.total_hours)

			if dd.ext_diff> 0 :
				total_ex+=1

			if dd.early_departure > 0: 
				total_earl += 1

			if dd.status =="Present":
				report = frappe.get_list("Employee Report",['name'],filters={"date" :dd.attendance_date})
				if not report:
					dont_write_report+=1
				else:
					re=frappe.get_doc("Employee Report",report[0].name)
					if re:
						d=add_days(dd.attendance_date,1)

						mytime = datetime.strptime('12:00','%H:%M').time()
						mm =datetime.combine(d, mytime)
						if(re.posting_date > mm):
							write_late+=1









		data.append([add[0],add[1],total_early,total_late,leavess,total_abs,round(total_over,2),round(disc,2),total_ex,total_earl,dont_write_report,write_late])
		# if(len(det)>0):
		# 	pass
			# data.append(det[0].early_departure)
	return data

def get_conditions(filters):
	conditions = ""

	# if filters.get("employee"): conditions += " and emp.employee = '%(employee)s'"
	if filters.get("from_date"): conditions += " and att.attendance_date >=  %(from_date)s"
	if filters.get("to_date"): conditions += " and att.attendance_date <= %(to_date)s"

	return conditions, filters

def get_employee_details(conditions, filters,employee): 

	# attendance_day = calendar.day_name[getdate().weekday()];
	# emp_details = frappe.db.get_value("Employee Employment Detail", employee,["work_shift","morning_delay_in_minutes"], as_dict=1)
	# morning_delay_minutes= emp_details.morning_delay_in_minutes
	# if not emp_details.work_shift:
	# 	return

	# employee_end_time = frappe.db.get_value("Work Shift Details", {"parent":emp_details.work_shift,"day":attendance_day}, "end_work")
	# if not employee_end_time:
	# 	return

	# employee_start_time = frappe.db.get_value("Work Shift Details", {"parent":emp_details.work_shift,"day":attendance_day}, "start_work")
	# if not employee_start_time:
	# 	return
	
	# if not emp_details.morning_delay_in_minutes:
	# 	morning_delay_minutes = frappe.db.get_value("HR Settings", None, "morning_delay")
	# 	if not morning_delay_minutes:
	# 		return
	# early_departure_in_minutes = frappe.db.get_value("HR Settings", None, "early_departure_in_minutes")
	# if not early_departure_in_minutes:
	# 	return 

	emp_map  = frappe.db.sql("""select distinct att.attendance_date, emp.employee_name, att.name as attname,dept.name as deptname, emp.name,emp.name ,dept.departure_date, DAYNAME(att.attendance_date) as day,att.attendance_time, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as total_hours ,GREATEST(round((TIMESTAMPDIFF(MINUTE,shd.start_work,shd.end_work))/60,3),0) as total_work_hrs,ifnull(overtime_hours,0) as overtime_hours,ifnull(tsh.holiday_overtime_hours,0) as holiday_overtime_hours,compensatory,tsh.type, tsh.from_time ,att.status,shd.start_work, ifnull(ext.early_diff,0) as early_departure,ifnull(ext.ext_diff,0) as ext_diff, work_shift, emp.holiday_list,ifnull(GREATEST(round(TIMESTAMPDIFF(MINUTE,shd.start_work,att.attendance_time)/60,2),0),0) as late_hrs from `tabEmployee` as emp   
	join  tabAttendance as att on att.employee=emp.name and discount_salary_from_leaves=0 and att.docstatus = 1
	left join  tabDeparture as dept on dept.employee=emp.name and att.attendance_date=dept.departure_date and dept.docstatus = 1
	left join `tabWork Shift Details` as shd on shd.parent =  work_shift and shd.day = DAYNAME(att.attendance_date)
	left join (select t.docstatus,employee,from_time,ifnull(sum(CASE WHEN type='compensatory' THEN hours END),0) as compensatory, ifnull(sum(CASE WHEN type='Normal' THEN hours END),0) as overtime_hours, ifnull(sum(CASE WHEN type='With Leave' THEN hours END),0) as holiday_overtime_hours,type from tabTimesheet as t join `tabTimesheet Detail` as td on t.name=td.parent and t.docstatus=1 group by date(from_time),employee) as tsh on emp.name=tsh.employee and att.attendance_date=date(tsh.from_time) and tsh.docstatus = 1 
	left join (select employee,depstat,exitstat, permission_date,sum(early_diff)/60 as early_diff, sum(diff) as ext_diff from (
	select employee,docstatus as depstat,0 as exitstat, permission_date,early_diff, 0 as diff from `tabExit permission` where permission_type='Early Departure' and docstatus = 1
	union all 
	select employee,0 as depstat,docstatus as exitstat, permission_date,0 as early_diff ,TIME_TO_SEC(diff_exit)/3600 as diff from `tabExit permission` where type='Return' and permission_type='Exit with return' and docstatus = 1) as d group by permission_date,employee) as ext 
	on emp.employee=ext.employee and att.attendance_date=ext.permission_date 
	where 1 %s and att.employee = '%s' order by emp.name, attendance_date"""% (conditions,employee), filters, as_dict=1)
	return emp_map


