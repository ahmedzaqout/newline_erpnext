# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate, time_diff_in_hours
from frappe import msgprint, _
import datetime, calendar, time
from calendar import monthrange
import math
import time


def execute(filters=None):
	if not filters: filters = {}

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	emp_map = get_employee_details(conditions, filters)


	data ,total_row= [],[]
	total=0.0
	over = 0.0

	total_all,total_over, total_lat, total_earl,total_ext,total_disc,total_work_hrs_row,total_penalty,total_comp_over =0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
	comp_over, over ,penalty = 0.0, 0.0, 0.0

	ovr_rate = frappe.db.get_value("HR Settings", None, "overtime_hour_price")
	if not ovr_rate:
		frappe.throw(_("Add a value for Overtime Hour Rate in HR Settings"))

	overtime_hour_price_in_holidays = frappe.db.get_value("HR Settings", None, "overtime_hour_price_in_holidays")
	if not overtime_hour_price_in_holidays:
		frappe.throw(_("Add a value for Holiday and Leaves Overtime Hour Rate in HR Settings"))

	for emp in sorted(emp_map):
		#frappe.msgprint(getdate(emp.attendance_date).day)
		is_holiday = False
		holiday_list = frappe.db.get_value("Employee", emp.name, "holiday_list")
		if holiday_list:
			holidays = frappe.get_all("Holiday", fields=["holiday_date"],filters={'parent':holiday_list})
			for holiday in holidays:
				if holiday.holiday_date == getdate(emp.get("attendance_date")):
					is_holiday = True
					break


		
		###############
		#if getdate(emp.attendance_date).day < 14  and getdate(emp.attendance_date).month== 6 : 
		#	total_work_hrs = emp.total_work_hrs - (emp.total_work_hrs-7)
		total_work_hrs = emp.total_work_hrs

		total_work_hrs_row += total_work_hrs
					
		row =[emp.type,emp.get("attendance_date"),_(emp.day),emp.attendance_time,emp.departure_time,convert_hms_format(emp.total_hours),convert_hms_format(total_work_hrs),_(emp.status)]

		total_row= ['','','','','','',total_work_hrs_row,'']

		if emp.total_hours:
			total= emp.total_hours

		else: total= 0.0
		#if is_holiday:
		#	total= 0.0

		###############
		#if getdate(emp.attendance_date).day > 16 and total > 7: 
		#	total = total - (total-7)


		if  filters.get("morning_late") and emp.late_hrs>=0:
			row+=[convert_hms_format(round(emp.late_hrs,2))]
			if emp.late_hrs: 
				#total -= emp.late_hrs
				total_lat += emp.late_hrs
			total_row+=[round(total_lat,2)]

		
		if  filters.get("overtime"):
			#if emp.type== "Normal":
			#	emp.overtime_hours = emp.overtime_hours * float(ovr_rate)

			comp_over, over = 0.0, 0.0
			if emp.compensatory and int(emp.compensatory) != 0:
				
				if total >  total_work_hrs:
					total= total - (total -total_work_hrs)
				#over = float(emp.compensatory) 

				comp_over = float(emp.compensatory) 
				total += comp_over
				#total_comp_over += comp_over
				#frappe.msgprint(str(comp_over))

			if emp.overtime_hours:
				over = emp.overtime_hours * float(ovr_rate)
				#total += 0.0
				total_over += over

			if emp.holiday_overtime_hours:
				over = emp.holiday_overtime_hours * float(overtime_hour_price_in_holidays)
				#total += 0.0
				total_over += over

			#if comp_over == 0.0: comp_over =over
			row+=[convert_hms_format(round(comp_over,2))]
			total_row+=[round(total_over,2)]

			#if emp.overtime_hours :
			#	if emp.type =='compensatory':
			#		total += over

			#	if emp.type !='compensatory':	
			#		total_over += over
			#	else: total_over += 0.0
	
					
				#total_over += emp.overtime_hours
			


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
				#if diff >0:
				#	total_disc += diff
				#else:
				#	total_disc += 0.0
					#total_over = abs(diff)


			total_row+=[round(total_disc,2)]

		if  filters.get("penalty"):
			penalty= 0.0
			emp_penalty = get_penalty_discount( getdate(emp.get("attendance_date")), emp.name )
			if emp_penalty:
				penalty = float(emp_penalty[0].discount_day)
			#for empp in emp_penalty:
			#if getdate(emp.get("attendance_date")) == getdate(emp_penalty[0].warning_date):
					#day = calendar.day_name[getdate(emp.get("attendance_date")).weekday()];
					#emp_wshift = frappe.db.get_value("Employee Employment Detail", emp.name , "work_shift")
					#employee_start_time = frappe.db.get_value("Work Shift Details", {"parent":emp_wshift,"day":day}, "start_work")
					#employee_end_time = frappe.db.get_value("Work Shift Details", {"parent":emp_wshift,"day":day}, "end_work")
					#shift_diff = time_diff_in_hours(employee_end_time, employee_start_time)

					#penalty = float(empp.discount_day) * float(shift_diff)

			total -= penalty
			
			row+=[convert_hms_format(round(penalty,2))]
			total_penalty +=penalty
			total_row+=[round(total_penalty,2)]

		
		#if getdate(emp.attendance_date).day > 16 and total > 7: 
		#	total = total - (total-7)

		#if emp.total_hours:
		#	total= emp.total_hours  - total_ext - penalty +comp_over
		if  total > total_work_hrs and not comp_over: #and not is_holiday:
			total= total - (total -total_work_hrs)

		if total < 0: 
			total=0.0

		row+=[convert_hms_format(round(total,2))]
		total_all+=total 

			
		data.append(row)

	total_row+=[round(total_all,2)]	
	data.append(total_row)
	return columns, data

def get_columns(filters):
	columns = [
		 {"label":_("Type") ,"width":80,"fieldtype": "Data","hidden":1},
		 {"label":_("Attendance Date") ,"width":80,"fieldtype": "Date"},
		 {"label":_("Day") ,"width":70,"fieldtype": "Data"},
		 {"label":_("Attendance Time") ,"width":90,"fieldtype": "Time"},
		 {"label":_("Departure Time") ,"width":90,"fieldtype": "Time"},
		 {"label":_("Total Hours") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Total Work Hours") ,"width":110,"fieldtype": "Data"},
		 #{"label":_("Work Shift") ,"width":80,"fieldtype": "Link","options":"Work Shift"},
		 #{"label":_("Start Work Shift") ,"width":90,"fieldtype": "Time"},
		 #{"label":_("Holiday List") ,"width":90,"fieldtype": "Data"},
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

	#columns += [_("Total Present") + ":Float:80", _("Total Leaves") + ":Float:80",  _("Total Absent") + ":Float:80"]
	return columns

def get_attendance_list(conditions, filters):
	attendance_list = frappe.db.sql("""select employee, attendance_date,day(attendance_date) as day_of_month,attendance_time,departure_time,
		status from tabAttendance where docstatus = 1 %s order by employee, attendance_date""" %
		conditions, filters, as_dict=1)

	att_map = {}
	for d in attendance_list:
		att_map.setdefault(d.employee, frappe._dict()).setdefault(d.day_of_month, "")
		att_map[d.employee][d.day_of_month] = d.status


	return att_map

def get_conditions(filters):
	#if not (filters.get("month") and filters.get("year")):
	#	msgprint(_("Please select month and year"), raise_exception=1)
	if not (filters.get("employee")):
		msgprint(_("Please select employee"), raise_exception=1)

	#filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
		#"Dec"].index(filters.month) + 1

	#filters["total_days_in_month"] = monthrange(cint(filters.year), filters.month)[1]

	conditions = ""#" and month(attendance_date) = %(month)s and year(attendance_date) = %(year)s"
	if filters.get("employee"): conditions += " emp.employee = %(employee)s"
	#if filters.get("company"): conditions += " and att.company = %(company)s"
	if filters.get("from_date"): conditions += " and att.attendance_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and att.attendance_date <= %(to_date)s"

	return conditions, filters

def get_employee_details(conditions, filters): 
	emp_map  = frappe.db.sql("""select  emp.name,emp.employee , att.attendance_date,dept.departure_date, DAYNAME(att.attendance_date) as day,att.attendance_time, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as total_hours ,emp.total_work_hrs,ifnull(overtime_hours,0) as overtime_hours,ifnull(tsh.holiday_overtime_hours,0) as holiday_overtime_hours,compensatory,tsh.type, tsh.from_time ,att.status,start_work, ifnull(ext.early_diff,0) as early_departure,ifnull(ext.ext_diff,0) as ext_diff, work_shift, emp.holiday_list,ifnull(round(TIMESTAMPDIFF(MINUTE,start_work,att.attendance_time)/60,2),0) as late_hrs from `tabEmployee Employment Detail` as emp   
join  tabAttendance as att on att.employee=emp.employee  and att.docstatus = 1
left join  tabDeparture as dept on dept.employee=emp.employee and att.attendance_date=dept.departure_date and dept.docstatus = 1
left join (select t.docstatus,employee,from_time,ifnull(sum(CASE WHEN type='compensatory' THEN hours END),0) as compensatory, ifnull(sum(CASE WHEN type='Normal' THEN hours END),0) as overtime_hours, ifnull(sum(CASE WHEN type='With Leave' THEN hours END),0) as holiday_overtime_hours,type from tabTimesheet as t join `tabTimesheet Detail` as td on t.name=td.parent group by date(from_time),employee) as tsh on emp.employee=tsh.employee and att.attendance_date=date(tsh.from_time) and tsh.docstatus = 1 
left join (select employee,docstatus, permission_date,sum(early_diff)/60 as early_diff, sum(diff) as ext_diff from (
select employee,docstatus, permission_date,early_diff, 0 as diff from `tabExit permission` where permission_type='Early Departure'
union all 
select employee,docstatus, permission_date,0 as early_diff ,diff_exit as diff from `tabExit permission` where type='Return' and permission_type='Exit with return') as d group by permission_date,employee) as ext 
on emp.employee=ext.employee and att.attendance_date=ext.permission_date and ext.docstatus < 2 
where  %s order by emp.employee, attendance_date"""% conditions, filters, as_dict=1)

	return emp_map

def get_holiday(holiday_list, month):
	holiday_map = frappe._dict()
	for d in holiday_list:
		if d:
			holiday_map.setdefault(d, frappe.db.sql_list('''select holiday_date from `tabHoliday`
				where parent=%s and month(holiday_date)=%s''', (d, month)))

	return holiday_map

@frappe.whitelist()
def get_attendance_years():
	year_list = frappe.db.sql_list("""select distinct YEAR(attendance_date) from tabAttendance ORDER BY YEAR(attendance_date) DESC""")
	if not year_list:
		year_list = [getdate().year]

	return "\n".join(str(year) for year in year_list)



@frappe.whitelist()
def get_penalty_discount(warning_date,employee):
	return frappe.db.sql("""select sum(pen.discount_day) as discount_day,warning_date,employee from `tabWarning Information` as wan join tabPenalty as pen on pen.name = wan.penalty and wan.docstatus = 1 group by employee,warning_date having employee=%s and warning_date = %s""", (employee,warning_date) , as_dict=1)

@frappe.whitelist()
def convert_hms_format(number=0):
	num ="0:00:00"
	if number:
		#hours_num = int(number)
		#hours_dec = number-hours_num
		#mins  = hours_dec * 60
		#mins_num = int(mins)
		#mins_dec = mins-mins_num
		#secs = mins_dec * 60
		#print(secs)
		#secs_num = int(secs)
		#num=  str(hours_num) +":"+ str(mins_num)+":"+str(secs_num)
		#n = frappe.utils.datetime.datetime.strptime(num, "%H:%M:%S.%f")
		num = str(datetime.timedelta(seconds=number*3600))
	return num
	




#.slick-row.odd .slick-cell {
 #   background-color: #fafbfc;}


