# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate,time_diff_in_hours
from frappe import msgprint, _
from calendar import monthrange
from datetime import date, timedelta
from datetime import datetime
import  calendar, time



def execute(filters=None):
	if not filters: filters = {}

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	delta = datetime.strptime(filters.get("to_date") , '%Y-%m-%d')- datetime.strptime(filters.get("from_date"), '%Y-%m-%d')
 
	
	sdate= datetime.strptime(filters.get("from_date"), '%Y-%m-%d')
	data=[]
	total_p = total_d = total_l = 0.0
	total_all=0.0
	total_earl=0.0
	total_ext=0.0
	total_lat=0.0
	total_over=0.0
	ovr_rate = frappe.db.get_value("HR Settings", None, "overtime_hour_price")
	if not ovr_rate:
		frappe.throw(_("Add a value for Overtime Hour Rate in HR Settings"))

	overtime_hour_price_in_holidays = frappe.db.get_value("HR Settings", None, "overtime_hour_price_in_holidays")
	if not overtime_hour_price_in_holidays:
		frappe.throw(_("Add a value for Holiday and Leaves Overtime Hour Rate in HR Settings"))

	emp=filters.get("employee")
	for i in range(delta.days + 1):
    		day = sdate + timedelta(days=i)
		total_work_hrs, start_work, end_work,next_day,next_total_work_hrs = get_wsh_history(filters.get("employee"), getdate(day))
		if next_day and next_day==1:
			emp_map  = frappe.db.sql("""select  att.attendance_date, dept.departure_date,att.attendance_time, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as total_hours ,GREATEST(24-round((TIMESTAMPDIFF(MINUTE,dept.departure_time,att.attendance_time))/60,3),0) as next_total_hrs ,att.status 
from tabAttendance as att left join  tabDeparture as dept on att.employee=dept.employee and date_add(att.attendance_date,interval 1 day)  =dept.departure_date and dept.docstatus = 1 and att.docstatus=1  where att.docstatus=1  and dept.docstatus = 1 and att.employee= '{0}' and att.attendance_date = '{1}' """.format(filters.get("employee"),getdate(day)), as_dict=1)
		else:
			emp_map  = frappe.db.sql("""select  att.attendance_date, dept.departure_date,att.attendance_time, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as total_hours ,GREATEST(24-round((TIMESTAMPDIFF(MINUTE,dept.departure_time,att.attendance_time))/60,3),0) as next_total_hrs ,att.status 
	from tabAttendance as att join  tabDeparture as dept on att.employee=dept.employee and att.attendance_date=dept.departure_date and dept.docstatus = 1 and att.docstatus=1  where att.docstatus=1  and dept.docstatus = 1  and att.employee= '{0}' and att.attendance_date = '{1}' """.format(filters.get("employee"),getdate(day)), as_dict=1)
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
		if emp_map:
			attend=emp_map[0].attendance_time
			dep=emp_map[0].departure_time
			total_ho=emp_map[0].total_hours
			next_total_hrs=emp_map[0].next_total_hrs
			status=emp_map[0].status
			emp=emp_map[0]
		if not start_work:
			row =[day.strftime("%m-%d-%Y"), _(day.strftime("%A")),"","",0,0,_("On Holiday")]
			total= 0.0
			
		else:
		
			if next_day and next_day==1:
				row = [day.strftime("%m-%d-%Y"), _(day.strftime("%A")),attend,dep,next_total_hrs, next_total_work_hrs,status]
				total= next_total_hrs
				total_work_hrs=next_total_work_hrs
			else:
				row = [day.strftime("%m-%d-%Y"), _(day.strftime("%A")),attend,dep,total_ho,total_work_hrs,status]
				total= total_ho
				total_work_hrs=total_work_hrs

		total_l+=total_work_hrs
		total_row= ['','','','','',round(total_l,2),'']
		
		if  filters.get("morning_late") :
			diff_klk  = frappe.db.sql("""select  ifnull(ex.late_diff,0) as late_diff from `tabExit permission` as ex where ex.employee ='{0}' and ex.permission_date = '{1}' and docstatus= 1 and permission_type = 'Morning Late' """.format(filters.get("employee"),getdate(day)), as_dict=1)
			late_hrs="0:00:00"

			if diff_klk:
				latt= datetime.strptime(diff_klk[0].late_diff, "%H:%M:%S")
				late_hrs=str(diff_klk[0].late_diff)
				total_lat += (latt.hour)+ (latt.minute*60) + latt.second
			row+=[str(late_hrs)]

			total_row+=[convert_hms_format(round(total_lat,2))]

		
		if  filters.get("overtime"):
			over_tt  = frappe.db.sql("""select t.docstatus,employee,from_time,ifnull(sum(CASE WHEN type='compensatory' THEN hours END),0) as compensatory, ifnull(sum(CASE WHEN type='Normal' THEN hours END),0) as overtime_hours, ifnull(sum(CASE WHEN type='With Leave' THEN hours END),0) as holiday_overtime_hours,type from tabTimesheet as t join `tabTimesheet Detail` as td on t.name=td.parent and t.docstatus=1 where employee = '{0}' and date(from_time) ='{1}' group by date(from_time),employee  """.format(filters.get("employee"),getdate(day)), as_dict=1)

			comp_over, over, sh_over = 0.0, 0.0, 0.0
			if over_tt:
				over_tt=over_tt[0]
			
				
				if over_tt.compensatory and over_tt.compensatory != 0.0:
					if total >  total_work_hrs:
						total= total - (total - (total_work_hrs or 0.0) ) 


					comp_over = float(over_tt.compensatory) 
					total += comp_over
					#total_comp_over += comp_over
					#frappe.msgprint(str(comp_over))

				if over_tt.overtime_hours:
					over = over_tt.overtime_hours * float(ovr_rate)
					#total += 0.0
					total_over += over

				if over_tt.holiday_overtime_hours:
					over = over_tt.holiday_overtime_hours * float(overtime_hour_price_in_holidays)
					#total += 0.0
					total_over += over

			sh_over =comp_over
			if not  comp_over or comp_over == 0.0: sh_over =over
			row+=[convert_hms_format(round(sh_over*3600,2))]
			total_row+=[convert_hms_format(round(total_over*3600,2))]

			


		if  filters.get("early_dep"):
			if next_day and next_day==1:
				earl  = frappe.db.sql("""select  ifnull(ex.early_diff,0) as early_diff from `tabExit permission` as ex where ex.employee ='{0}' and DATE_SUB(ex.permission_date,interval 1 day)= '{1}' and docstatus= 1 and  permission_type = 'Early Departure' """.format(filters.get("employee"),getdate(day)), as_dict=1)
			else:
				earl  = frappe.db.sql("""select  ifnull(ex.early_diff,0) as early_diff from `tabExit permission` as ex where ex.employee ='{0}' and ex.permission_date = '{1}' and docstatus= 1 and permission_type = 'Early Departure' """.format(filters.get("employee"),getdate(day)), as_dict=1)
			early_departure="0:00:00"
			if earl and earl[0].early_diff:
				early_departure=convert_hms_format(round(float(earl[0].early_diff),2))
				total_earl += float(earl[0].early_diff)

			row+=[str(early_departure)]
			

			total_row+=[str(convert_hms_format(round(total_earl,2)))]

		if  filters.get("ex_per"):
			ex  = frappe.db.sql("""select  ifnull(ex.early_diff,0) as early_diff from `tabExit permission` as ex where ex.employee ='{0}' and ex.permission_date = '{1}' and docstatus= 1 and permission_type = 'Exit with return' """.format(filters.get("employee"),getdate(day)), as_dict=1)
			ext_diff=0.0
			if ex:
				ext_diff = float(ex[0].early_diff)

			row+=[convert_hms_format(round(ext_diff*60,2))]
			discount_permissions_from_attendance_hours = frappe.db.get_value("HR Settings", None, "discount_permissions_from_attendance_hours")
			
			#if  total > total_work_hrs and not comp_over:
			#	total= total - (total -total_work_hrs)

			if ext_diff and discount_permissions_from_attendance_hours: 
				total -= ext_diff
			total_ext +=ext_diff
			total_row+=[str(convert_hms_format(round(total_ext,2)))]







		if  total > total_work_hrs:
			total= total_work_hrs
		

		disc =0
		if  total < total_work_hrs:
			disc = total_work_hrs*3600 - total *3600
		total_d +=disc

		if total <= 0: 
			total=0.0
		if  filters.get("disc_hrs"):
			row+=[convert_hms_format(round(disc,2))]
			total_row+=[str(convert_hms_format(round(total_d,2)))]
		row+=[convert_hms_format(round(total*3600,2))]
		total_all+=total 
		total_row+=[str(convert_hms_format(round(total_all*3600,2)))]
		
		
		data.append(row)

	data.append(total_row)
	return columns, data


def get_columns(filters):
	columns = [
		 {"label":_("Attendance Date") ,"width":80,"fieldtype": "Date"},
		 {"label":_("Day") ,"width":70,"fieldtype": "Data"},
		 {"label":_("Attendance Time") ,"width":90,"fieldtype": "Time"},
		 {"label":_("Departure Time") ,"width":90,"fieldtype": "Time"},
		 {"label":_("Total Hours") ,"width":100,"fieldtype": "Data"},
		 #{"label":_("Start Work") ,"width":110,"fieldtype": "Time"},
		 #{"label":_("End Work") ,"width":110,"fieldtype": "Time"},
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



	columns += [ {"label":_("Total") ,"width":70,"fieldtype": "Data"}]
	return columns

def get_attendance_list(conditions, filters):
	attendance_list = frappe.db.sql("""select employee,day(attendance_date) as day_of_month,
		tabAttendance.status from tabAttendance  where docstatus = 1 %s order by employee, attendance_date""" %
		conditions, filters, as_dict=1)

	att_map = {}
	for d in attendance_list:
		att_map.setdefault(d.employee, frappe._dict()).setdefault(d.day_of_month, "")
		att_map[d.employee][d.day_of_month] = d.status

	return att_map
def get_conditions(filters):
	if not (filters.get("employee")):
		msgprint(_("Please select employee"), raise_exception=1)

	conditions = ""
	if filters.get("employee"): conditions += " and att.employee = %(employee)s"
	if filters.get("from_date"): conditions += "and att.attendance_date = %(from_date)s"
	if filters.get("to_date"): conditions += "and att.attendance_date = %(to_date)s"
	return conditions, filters

def get_employee_details():
	emp_map = frappe._dict()
	for d in frappe.db.sql("""select tabEmployee.employee_name, tabEmployee.name,ed.designation, ed.branch,ed.management , ed.holiday_list from tabEmployee left join `tabEmployee Employment Detail` as ed on tabEmployee.employee=ed.employee """, as_dict=1):
		emp_map.setdefault(d.name, d)

	return emp_map

def get_holiday(holiday_list, month):
	holiday_map = frappe._dict()
	for d in holiday_list:
		if d:
			holiday_map.setdefault(d, frappe.db.sql_list('''select day(holiday_date) from `tabHoliday`
				where parent=%s and month(holiday_date)=%s''', (d, month)))

	return holiday_map

@frappe.whitelist()
def get_penalty_discount(warning_date,employee):
	return frappe.db.sql("""select ifnull(sum(pen.discount_day),0) as discount_day,warning_date,employee from `tabWarning Information` as wan join tabPenalty as pen on pen.name = wan.penalty and wan.docstatus = 1 group by employee,warning_date having employee=%s and warning_date = %s""", (employee,warning_date) , as_dict=1)


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

@frappe.whitelist()
def convert_hms_format(number=0):
	num ="0:00:00"
	if number:
		hours, remainder = divmod(number, 3600)
		minutes, seconds = divmod(remainder, 60)
		num= '{0}:{1}:{2}'.format(int(hours), int(minutes), int(seconds))
	return num
@frappe.whitelist()
def get_attendance_years():
	year_list = frappe.db.sql_list("""select distinct YEAR(attendance_date) from tabAttendance ORDER BY YEAR(attendance_date) DESC""")
	if not year_list:
		year_list = [getdate().year]

	return "\n".join(str(year) for year in year_list)
