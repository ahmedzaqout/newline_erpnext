# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _
import datetime, calendar, time
from calendar import monthrange
#from erpnext.hr.report.employee_monthly_attendance_sheet.employee_monthly_attendance_sheet import get_penalty_discount

def execute(filters=None):
	if not filters: filters = {}

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	emp_map = get_employee_details(conditions, filters)

	data ,total_row= [],[]
	total=0.0;
	over = 0.0

	total_all,total_over, total_lat, total_earl,total_ext,total_disc,total_work_hrs_row,total_penalty,total_comp_over =0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
	comp_over, over ,penalty = 0.0, 0.0, 0.0

	ovr_rate = frappe.db.get_value("HR Settings", None, "overtime_hour_price")
	if not ovr_rate:
		frappe.throw(_("Add a value for Overtime Hour Rate in HR Settings"))

	overtime_hour_price_in_holidays = frappe.db.get_value("HR Settings", None, "overtime_hour_price_in_holidays")
	if not overtime_hour_price_in_holidays:
		frappe.throw(_("Add a value for Holiday and Leaves Overtime Hour Rate in HR Settings"))

	#try:
	for emp in sorted(emp_map):
		is_holiday = False
		holiday_list = frappe.db.get_value("Employee", emp.name, "holiday_list")
		if holiday_list and emp_map !=[]:
			holidays = frappe.get_all("Holiday", fields=["holiday_date"],filters={'parent':holiday_list})
			for holiday in holidays:
				if holiday.holiday_date == getdate(emp.get("attendance_date")):
					is_holiday = True
					break

		total_work_hrs = emp.total_work_hrs

		total_work_hrs_row += total_work_hrs
		row =[emp.type,emp.name,emp.employee_name, emp.get("attendance_date"),emp.attendance_time,emp.departure_time,convert_hms_format(emp.total_hours),convert_hms_format(total_work_hrs),_(emp.status)]

		total_row= ['','','','','','','',total_work_hrs_row,'']

		if emp.total_hours:
			total= emp.total_hours

		else: total= 0.0

		if  filters.get("morning_late") and emp.late_hrs>=0:
			row+=[convert_hms_format(round(emp.late_hrs,2))]
			if emp.late_hrs: 
				#total -= emp.late_hrs
				total_lat += emp.late_hrs
			else:
				total_lat += 0.0
			total_row+=[round(total_lat,2)]

		
		if  filters.get("overtime"):
			#if emp.type== "Normal":
			#	emp.overtime_hours = emp.overtime_hours * float(ovr_rate)

			comp_over, over, sh_over = 0.0, 0.0, 0.0

			if emp.compensatory and emp.compensatory != 0.0:
				if total >  total_work_hrs:
					total= total - (total -total_work_hrs)
				#over = float(emp.compensatory) 

				comp_over = float(emp.compensatory) 
				total += comp_over
				#total_comp_over += comp_over

			if emp.overtime_hours:
				over = emp.overtime_hours * float(ovr_rate)
				#total += 0.0
				total_over += over

			if emp.holiday_overtime_hours:
				over = emp.holiday_overtime_hours * float(overtime_hour_price_in_holidays)
				#total += 0.0
				total_over += over
				
			sh_over =comp_over
			#if not  comp_over or comp_over == 0.0: sh_over =over
			if  over or over != 0.0: sh_over =over

			row+=[convert_hms_format(round(sh_over,2))]
			total_row+=[round(total_over,2)]
			

		if  filters.get("early_dep"):
			row+=[convert_hms_format(round(emp.early_departure,2))]
			if emp.early_departure: 
				#total -= emp.early_departure
				total_earl +=emp.early_departure
			total_row+=[round(total_earl,2)]

		if  filters.get("ex_per"):

			row+=[convert_hms_format(round(emp.ext_diff,2))]
			discount_permissions_from_attendance_hours = frappe.db.get_value("HR Settings", None, "discount_permissions_from_attendance_hours")
			if emp.ext_diff and discount_permissions_from_attendance_hours: 
				total -= emp.ext_diff
			total_ext +=emp.ext_diff
			total_row+=[round(total_ext,2)]


		if  filters.get("disc_hrs"):
			if total_work_hrs > total :
				disc = float(total_work_hrs) - float(total)
			else: disc = 0.0

			row+=[convert_hms_format(round(disc,2))]			
			total_disc +=disc

			if comp_over: 
				diff = disc - comp_over
				total_disc += diff
			
			total_row+=[max(0,round(total_disc,2))]

		if  filters.get("penalty"):
			penalty= 0.0
			emp_penalty = get_penalty_discount( getdate(emp.get("attendance_date")), emp.name )
			if emp_penalty:
				penalty = float(emp_penalty[0].discount_day)
			total -= penalty

			total_penalty +=penalty
			row+=[convert_hms_format(round(penalty,2))]
			total_row+=[round(total_penalty,2)]

		if  total > total_work_hrs and not comp_over: #and not is_holiday:
			total= total - (total -total_work_hrs)

		if total <= 0: 
			total=0.0

		row+=[convert_hms_format(round(total,2))]
		total_all+=total 

			
		data.append(row)

	total_row+=[round(total_all,2)]	
	data.append(total_row)
	#except:
	#	pass#frappe.msgprint(_("No Data"))
	return columns, data

def get_columns(filters):
	columns = [
		 {"label":_("Type") ,"width":80,"fieldtype": "Data","hidden":1},
		 {"label":_("Employee Number") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Employee Name") ,"width":160,"fieldtype": "Data"},
		 {"label":_("Attendance Date") ,"width":80,"fieldtype": "Date"},
		# {"label":_("Day") ,"width":70,"fieldtype": "Data"},
		 {"label":_("Attendance Time") ,"width":90,"fieldtype": "Time"},
		 {"label":_("Departure Time") ,"width":90,"fieldtype": "Time"},
		 {"label":_("Total Hours") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Total Work Hours") ,"width":110,"fieldtype": "Data"},
		 {"label":_("Status") ,"width":70,"fieldtype": "Data"}
	]

	if  filters.get("morning_late"):
		columns += [{"label":_("Late Hours") ,"width":80,"fieldtype": "Data"}]
	if  filters.get("overtime"):
		columns += [{"label":_("Overtime Hours") ,"width":70,"fieldtype": "Data"},]
	if  filters.get("early_dep"):
		columns += [{"label":_("Early Departure") ,"width":70,"fieldtype": "Data"},]
	if  filters.get("ex_per"):
		columns += [{"label":_("Exit Permissions") ,"width":70,"fieldtype": "Data"},]
	if  filters.get("disc_hrs"):
		columns += [{"label":_("Discount Hours") ,"width":100,"fieldtype": "Data"},]
	if  filters.get("penalty"):
		columns += [ {"label":_("Penalty Discount") ,"width":70,"fieldtype": "Data"}]

	columns += [ {"label":_("Total") ,"width":70,"fieldtype": "Data"}]

	return columns


def get_conditions(filters):

	conditions = ""
	if filters.get("company"): conditions += " and att.company = %(company)s"
	if filters.get("employee"): conditions += " and emp.name = %(employee)s"
	if filters.get("from_date"): conditions += " and att.attendance_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and att.attendance_date <= %(to_date)s"

	return conditions, filters

def get_employee_details(conditions, filters):
	return frappe.db.sql("""select distinct att.attendance_date, emp.employee_name, att.name as attname,dept.name as deptname, emp.name,emp.name as employee ,dept.departure_date, DAYNAME(att.attendance_date) as day,att.attendance_time, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as total_hours ,GREATEST(round((TIMESTAMPDIFF(MINUTE,shd.start_work,shd.end_work))/60,3),0) as total_work_hrs,ifnull(overtime_hours,0) as overtime_hours,ifnull(tsh.holiday_overtime_hours,0) as holiday_overtime_hours,compensatory,tsh.type, tsh.from_time ,att.status,shd.start_work, ifnull(ext.early_diff,0) as early_departure,ifnull(ext.ext_diff,0) as ext_diff, work_shift, emp.holiday_list,ifnull(GREATEST(round(TIMESTAMPDIFF(MINUTE,shd.start_work,att.attendance_time)/60,2),0),0) as late_hrs from `tabEmployee` as emp   
join  tabAttendance as att on att.employee=emp.name and att.discount_salary_from_leaves=0 and att.docstatus = 1
left join  tabDeparture as dept on dept.employee=emp.name and att.attendance_date=dept.departure_date and dept.docstatus = 1
left join `tabWork Shift Details` as shd on shd.parent =  work_shift and shd.day = DAYNAME(att.attendance_date)
left join (select t.docstatus,employee,from_time,ifnull(sum(CASE WHEN type='compensatory' THEN hours END),0) as compensatory, ifnull(sum(CASE WHEN type='Normal' THEN hours END),0) as overtime_hours, ifnull(sum(CASE WHEN type='With Leave' THEN hours END),0) as holiday_overtime_hours,type from tabTimesheet as t join `tabTimesheet Detail` as td on t.name=td.parent and t.docstatus=1 group by date(from_time),employee) as tsh on emp.name=tsh.employee and att.attendance_date=date(tsh.from_time) and tsh.docstatus = 1 
left join (select employee,depstat,exitstat, permission_date,sum(early_diff)/60 as early_diff, sum(diff) as ext_diff from (
select employee,docstatus as depstat,0 as exitstat, permission_date,early_diff, 0 as diff from `tabExit permission` where permission_type='Early Departure' and docstatus = 1
union all 
select employee,0 as depstat,docstatus as exitstat, permission_date,0 as early_diff ,TIME_TO_SEC(diff_exit)/3600 as diff from `tabExit permission` where type='Return' and permission_type='Exit with return' and docstatus = 1) as d group by permission_date,employee) as ext 
on emp.name=ext.employee and att.attendance_date=ext.permission_date 
where 1=1 %s order by emp.name, attendance_date"""% conditions, filters, as_dict=1)



@frappe.whitelist()
def convert_hms_format(number=0):
	num ="0:00:00"
	if number:
		num = str(datetime.timedelta(seconds=number*3600))
	return num
	

@frappe.whitelist()
def employee_name(emp_num):
	emp_name= emp_num
	try:
		employee_name = frappe.db.sql("""select employee_name from `tabEmployee` where name=%s""",emp_num,  as_dict=1)
		if employee_name:
			emp_name= employee_name[0].employee_name
	except:
		pass

	return emp_name



