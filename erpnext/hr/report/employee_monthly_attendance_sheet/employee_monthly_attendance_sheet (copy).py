# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _
from calendar import monthrange

def execute(filters=None):
	if not filters: filters = {}

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	emp_map = get_employee_details(conditions, filters)


	data ,total_row= [],[]
	total=0.0
	over = 0.0

	total_all,total_over, total_lat, total_earl,total_ext =0.0,0.0,0.0,0.0,0.0

	ovr_rate = frappe.db.get_value("HR Settings", None, "overtime_hour_price")
	if not ovr_rate:
		frappe.throw(_("Add a value for Overtime Hour Rate in HR Settings"))

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

					
		row =[emp.type,emp.get("attendance_date"),_(emp.day),emp.attendance_time,emp.departure_time,emp.total_hours,emp.total_work_hrs,emp.work_shift,emp.start_work,
emp.holiday_list,_(emp.status)]

		total_row= ['','','','','','','','','','','']

		if emp.total_hours:total= emp.total_hours
		else: total= 0.0
		if is_holiday:
			total= 0.0

		if  emp.total_hours > emp.total_work_hrs and not is_holiday:
			total= emp.total_hours - (emp.total_hours -emp.total_work_hrs)

		###############
		if getdate(emp.attendance_date).day > 16 and total > 7: 
			total = total - (total-7)


		if  filters.get("morning_late") and emp.late_hrs>=0:
			row+=[emp.late_hrs]
			if emp.late_hrs: 
				#total -= emp.late_hrs
				total_lat += emp.late_hrs
			total_row+=[total_lat]


		if  filters.get("overtime"):
			if emp.type== "Normal":
				emp.overtime_hours = emp.overtime_hours * float(ovr_rate)

			row+=[emp.overtime_hours]

			if emp.overtime_hours :
				if emp.type =='compensatory':
					total += emp.overtime_hours

				if emp.type !='compensatory':	
					total_over += emp.overtime_hours
				else: total_over += 0.0
	
					
				#total_over += emp.overtime_hours
			
			total_row+=[total_over]

		if  filters.get("early_dep"):
			row+=[emp.early_departure]
			if emp.early_departure: 
				#total -= emp.early_departure
				total_earl +=emp.early_departure
			total_row+=[total_earl]

		if  filters.get("ex_per"):
			row+=[emp.ext_diff]
			if emp.ext_diff: 
				total -= emp.ext_diff
				total_ext +=emp.ext_diff
			total_row+=[total_ext]
					

		if total < 0: 
			total=0.0
		
		#if getdate(emp.attendance_date).day > 16 and total > 7: 
		#	total = total - (total-7)

		row+=[total]
		total_all+=total 

			
		data.append(row)

	total_row+=[total_all,0.0]	
	data.append(total_row)
	return columns, data

def get_columns(filters):
	columns = [
		 {"label":_("Type") ,"width":80,"fieldtype": "Data","hidden":1},
		 {"label":_("Attendance Date") ,"width":80,"fieldtype": "Date"},
		 {"label":_("Day") ,"width":70,"fieldtype": "Data"},
		 {"label":_("Attendance Time") ,"width":90,"fieldtype": "Time"},
		 {"label":_("Departure Time") ,"width":90,"fieldtype": "Time"},
		 {"label":_("Total Hours") ,"width":90,"fieldtype": "Float"},
		 {"label":_("Total Work Hours") ,"width":100,"fieldtype": "Time"},
		 {"label":_("Work Shift") ,"width":80,"fieldtype": "Link","options":"Work Shift"},
		 {"label":_("Start Work Shift") ,"width":90,"fieldtype": "Time"},
		 {"label":_("Holiday List") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Status") ,"width":70,"fieldtype": "Data"}
	]
	if  filters.get("morning_late"):
		columns += [{"label":_("Late Hours") ,"width":70,"fieldtype": "Time"}]
	if  filters.get("overtime"):
		columns += [{"label":_("Overtime Hours") ,"width":70,"fieldtype": "Float"},]
	if  filters.get("early_dep"):
		columns += [{"label":_("Early Departure") ,"width":70,"fieldtype": "Float"},]
	if  filters.get("ex_per"):
		columns += [{"label":_("Exit Permissions") ,"width":70,"fieldtype": "Float"},]

	columns += [ {"label":_("Total") ,"width":70,"fieldtype": "Float"}]

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
	emp_map  = frappe.db.sql("""select  emp.name,emp.employee , att.attendance_date,dept.departure_date, DAYNAME(att.attendance_date) as day,att.attendance_time, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as total_hours ,emp.total_work_hrs,overtime_hours,tsh.type, tsh.start_date ,att.status,start_work, ext.early_diff as early_departure,ext.ext_diff as ext_diff, work_shift, emp.holiday_list,ifnull(round(TIMESTAMPDIFF(MINUTE,start_work,att.attendance_time)/60,2),0.0) as late_hrs from `tabEmployee Employment Detail` as emp   
join  tabAttendance as att on att.employee=emp.employee  and att.docstatus = 1
left join  tabDeparture as dept on dept.employee=emp.employee and att.attendance_date=dept.departure_date and dept.docstatus = 1
left join ( select docstatus,type, employee,start_date,ifnull(round(sum(total_hours),2),0) as overtime_hours from tabTimesheet group by start_date,employee,type) as tsh on emp.employee=tsh.employee and att.attendance_date=tsh.start_date and tsh.docstatus = 1 
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



#.slick-row.odd .slick-cell {
 #   background-color: #fafbfc;}


