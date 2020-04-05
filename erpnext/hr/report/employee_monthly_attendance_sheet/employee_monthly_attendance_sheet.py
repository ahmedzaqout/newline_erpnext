# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate, time_diff_in_hours, get_time
from frappe import msgprint, _
import datetime, calendar, time
from calendar import monthrange
import math
import time
from erpnext.hr.doctype.leave_application.leave_application \
	import get_leave_allocation_records, get_leave_balance_on, get_approved_leaves_for_period


def execute(filters=None):
	if not filters: filters = {}

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	emp_map = get_employee_details(conditions, filters)


	data ,total_row= [],[]
	total=0.0;
	over = 0.0
	leaves_num=0
	total_all,total_over, total_lat, total_earl,total_ext,total_disc,total_work_hrs_row,total_penalty,total_comp_over =0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
	comp_over, over ,penalty = 0.0, 0.0, 0.0

	ovr_rate = frappe.db.get_value("HR Settings", None, "overtime_hour_price")
	if not ovr_rate:
		frappe.throw(_("Add a value for Overtime Hour Rate in HR Settings"))

	overtime_hour_price_in_holidays = frappe.db.get_value("HR Settings", None, "overtime_hour_price_in_holidays")
	if not overtime_hour_price_in_holidays:
		frappe.throw(_("Add a value for Holiday and Leaves Overtime Hour Rate in HR Settings"))
	holidays_state=0


	for emp in sorted(emp_map):
		#frappe.msgprint(getdate(emp.attendance_date).day)
		is_holiday = False
		ho_state = frappe.db.sql("""select name from `tabState Holiday`
				where  %s between from_date and to_date""", (emp.get("attendance_date")))
		if ho_state:
			holidays_state +=1

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
		total_work_hrs, start_work, end_work = get_wsh_history(filters.get("employee"), getdate(emp.get("attendance_date")), emp.total_work_hrs) 
		if not total_work_hrs : total_work_hrs = emp.total_work_hrs

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
		late_hrs = emp.late_hrs
		if start_work:
			late_hrs = time_diff_in_hours(emp.attendance_time, start_work)
		if  filters.get("morning_late") and late_hrs>=0:
			row+=[convert_hms_format(round(late_hrs,2))]
			if late_hrs: 
				#total -= emp.late_hrs
				total_lat += late_hrs
			else:
				total_lat += 0.0
			total_row+=[round(total_lat,2)]

		comp_over, over, sh_over = 0.0, 0.0, 0.0
		if  filters.get("overtime"):
			#if emp.type== "Normal":
			#	emp.overtime_hours = emp.overtime_hours * float(ovr_rate)

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
			
			#if  total > total_work_hrs and not comp_over:
			#	total= total - (total -total_work_hrs)

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

			
			total_row+=[max(0,round(total_disc,2))]

		if  filters.get("penalty"):
			penalty= 0.0
			emp_penalty = get_penalty_discount( getdate(emp.get("attendance_date")), emp.name )
			if emp_penalty:
				penalty = float(emp_penalty[0].discount_day)
				if penalty >= total_work_hrs:
					update_att_status(emp.attname, emp.deptname,emp.name, emp.get("attendance_date"), emp.employee_name)
			#for empp in emp_penalty:
			#if getdate(emp.get("attendance_date")) == getdate(emp_penalty[0].warning_date):
					#day = calendar.day_name[getdate(emp.get("attendance_date")).weekday()];
				#emp_wshift = frappe.db.get_value("Employee Employment Detail", emp.name , "work_shift")
				#employee_start_time = frappe.db.get_value("Work Shift Details", {"parent":emp_wshift,"day":day}, "start_work")
				#employee_end_time = frappe.db.get_value("Work Shift Details", {"parent":emp_wshift,"day":day}, "end_work")
				#shift_hrs = time_diff_in_hours(employee_end_time, employee_start_time)
				#penalty = float(empp.discount_day) * float(shift_diff)

				if  total > total_work_hrs and not comp_over:
					total= total - (total -total_work_hrs)
				#if comp_over: 
				#	diff = abs(penalty - comp_over)
				#	total -= diff
				#	total -= penalty
				#	total_penalty += diff
				#else:
				total_penalty += penalty
				total -= penalty

			row+=[convert_hms_format(round(penalty,2))]
			total_row+=[round(total_penalty,2)]
		
		#if getdate(emp.attendance_date).day > 16 and total > 7: 
		#	total = total - (total-7)

		#if emp.total_hours:
		#	total= emp.total_hours  - total_ext - penalty +comp_over
		if  total > total_work_hrs and not comp_over: #and not is_holiday:
			total= total - (total -total_work_hrs)

		if total <= 0: 
			total=0.0

		row+=[convert_hms_format(round(total,2))]
		total_all+=total 
		#if total_all> total_work_hrs_row: total_all = total_work_hrs_row
		total_row+=[round(total_all,2)]	


		#To Nawa By Maysaa 	
		company = frappe.defaults.get_user_default("Company")
		if company == "Nawa" or frappe.session.user == "Administrator" :
			if emp.status =='On Leave':
				leavetype= frappe.db.sql('select leave_type from `tabLeave Application` where employee=%s and %s between from_date and to_date ',(filters.get("employee"), emp.get("attendance_date")),  as_dict=1)
				leave_types = get_leavs(company)
				
				for leave_type in leave_types:
					if leave_type == leavetype[0].leave_type:
						row+=[1]
						leaves_num += 1
					else: row+=[0]
			total_row+=[leaves_num]	


		data.append(row)

	

	
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

	company = frappe.defaults.get_user_default("Company")
	if company == "Nawa" or frappe.session.user == "Administrator" :
		leave_types = get_leavs(company)
		for leave_type in leave_types:
			columns += [{"label":_(leave_type) ,"width":80,"fieldtype": "Data","default":"0"}]


	#columns += [_("Total Present") + ":Float:80", _("Total Leaves") + ":Float:80",  _("Total Absent") + ":Float:80"]
	return columns
def get_leavs(company):
	return frappe.db.sql_list("select name from `tabLeave Type` where company=%s order by name asc",company)


@frappe.whitelist()
def get_wsh_history(employee,ddate, total_work_hrs):
	total_work_hrs = total_work_hrs
	start_work, end_work ='', ''
	day = calendar.day_name[getdate(ddate).weekday()];
	#conditions = " employee = %s and %s <= shift_change_date",(filters.get("employee"), ddate)
	emp_wshift = frappe.db.get_value("Employee",employee , "private_work_shift")

	if emp_wshift:
		doc = frappe.db.sql("select GREATEST(round((TIMESTAMPDIFF(MINUTE,start_work,end_work))/60,3),0) as total_work_hrs, start_work,end_work from `tabPrivate Work Shift Details`  where parent =  '{0}' and day = '{1}' and '{2}' between from_date and to_date ".format(emp_wshift, day,getdate(ddate)),as_dict=1)
		if doc:
			return doc[0].total_work_hrs ,doc[0].start_work,doc[0].end_work


	#conditions = " employee = %s and %s <= shift_change_date",(filters.get("employee"), ddate)
	work_shift = frappe.db.sql("""select work_shift from `tabWork Shift History` where  employee = %s and  %s >= shift_change_date  order by work_shift asc limit 1""",(employee, ddate), as_dict=1)
	if work_shift:
		day = calendar.day_name[getdate(ddate).weekday()];
		doc = frappe.db.sql("select GREATEST(round((TIMESTAMPDIFF(MINUTE,start_work,end_work))/60,3),0) as total_work_hrs, start_work,end_work from `tabWork Shift Details`  where parent =  '{0}' and day = '{1}'".format(work_shift[0].work_shift, day),as_dict=1)
		if doc:
			total_work_hrs= doc[0].total_work_hrs 
			# doc[0].start_work, doc[0].end_work
	return total_work_hrs, start_work, end_work


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

	conditions = ""
	if filters.get("employee"): conditions += " emp.name = %(employee)s"
	#if filters.get("company"): conditions += " and emp.company = %(company)s"
	if filters.get("from_date"): conditions += " and att.attendance_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and att.attendance_date <= %(to_date)s"

	return conditions, filters

def get_employee_details(conditions, filters): 
	emp_map  = frappe.db.sql("""select distinct att.attendance_date, emp.employee_name, att.name as attname,dept.name as deptname, emp.name,emp.name as employee ,dept.departure_date, DAYNAME(att.attendance_date) as day,att.attendance_time, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as total_hours ,GREATEST(round((TIMESTAMPDIFF(MINUTE,shd.start_work,shd.end_work))/60,3),0) as total_work_hrs,ifnull(overtime_hours,0) as overtime_hours,ifnull(tsh.holiday_overtime_hours,0) as holiday_overtime_hours,compensatory,tsh.type, tsh.from_time ,att.status,shd.start_work, ifnull(ext.early_diff,0) as early_departure,ifnull(ext.ext_diff,0) as ext_diff, work_shift, emp.holiday_list,ifnull(GREATEST(round(TIMESTAMPDIFF(MINUTE,shd.start_work,att.attendance_time)/60,2),0),0) as late_hrs from `tabEmployee` as emp   
join  tabAttendance as att on att.employee=emp.name and att.discount_salary_from_leaves=0 and att.docstatus = 1
left join  tabDeparture as dept on dept.employee=emp.name and att.attendance_date=dept.departure_date and dept.docstatus = 1
left join `tabWork Shift Details` as shd on shd.parent =  work_shift and shd.day = DAYNAME(att.attendance_date)
left join (select t.docstatus,employee,from_time,ifnull(sum(CASE WHEN type='compensatory' THEN hours END),0) as compensatory, ifnull(sum(CASE WHEN type='Normal' THEN hours END),0) as overtime_hours, ifnull(sum(CASE WHEN type='With Leave' THEN hours END),0) as holiday_overtime_hours,type from tabTimesheet as t join `tabTimesheet Detail` as td on t.name=td.parent and t.docstatus=1 group by date(from_time),employee) as tsh on emp.name=tsh.employee and att.attendance_date=date(tsh.from_time) and tsh.docstatus = 1 
left join (select employee,depstat,exitstat, permission_date,sum(early_diff)/60 as early_diff, sum(diff) as ext_diff from (
select employee,docstatus as depstat,0 as exitstat, permission_date,early_diff, 0 as diff from `tabExit permission` where permission_type='Early Departure' and docstatus = 1
union all 
select employee,0 as depstat,docstatus as exitstat, permission_date,0 as early_diff ,TIME_TO_SEC(diff_exit)/3600 as diff from `tabExit permission` where type='Return' and permission_type='Exit with return' and docstatus = 1) as d group by permission_date,employee) as ext 
on emp.name=ext.employee and att.attendance_date=ext.permission_date 
where  %s order by emp.name, attendance_date"""% conditions, filters, as_dict=1)
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
	return frappe.db.sql("""select ifnull(sum(pen.discount_day),0) as discount_day,warning_date,employee from `tabWarning Information` as wan join tabPenalty as pen on pen.name = wan.penalty and wan.docstatus = 1 group by employee,warning_date having employee=%s and warning_date = %s""", (employee,warning_date) , as_dict=1)

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
	



def update_att_status(attname, deptname, employee, date, employee_name):
	from erpnext.hr.doctype.leave_application.leave_application import get_number_of_leave_days, get_leave_balance_on
	doc = frappe.get_doc('Attendance', attname)
	if doc.status != 'On Leave':
		#frappe.db.set_value("Attendance", attname, "status", "On Leave")
		doc.update({
			'docstatus':2,
			'status' :'On Leave'})
		doc.flags.ignore_validate = True
		doc.flags.ignore_validate_update_after_submit = True
		doc.save(ignore_permissions=True)
	dep_doc = frappe.get_doc('Departure', deptname)
	if dep_doc.status != 'On Leave':
		dep_doc.update({
			'docstatus':2,
			'status' :'On Leave'})
		dep_doc.flags.ignore_validate = True
		dep_doc.flags.ignore_validate_update_after_submit = True
		dep_doc.save(ignore_permissions=True)
	#add new leave 
	if not frappe.db.get_value('Leave Application',{'employee':employee, 'from_date': date})  and frappe.db.get_value("Leave Type",_('Annual Leave'), "name"):
		leave = frappe.new_doc('Leave Application')
		leave.employee= employee
		leave.employee_name= employee_name
		leave.leave_type= _('Annual Leave')
		leave.from_date = date
		leave.to_date = date
		leave.total_leave_days = get_number_of_leave_days(employee, _('Annual Leave'),date,date)
		leave.status = 'Approved'
		leave.leave_balance = get_leave_balance_on(employee,_('Annual Leave'), date,consider_all_leaves_in_the_allocation_period=True)
		leave.description = _('Auto Entry: Discount form Leaves')
		leave.docstatus= 1
		leave.flags.ignore_validate = True
		leave.insert(ignore_permissions=True)

	send_email(employee ,_('Auto Entry: Discount form Warning'), _('Employee Task Late Warning')) 
	return True


#.slick-row.odd .slick-cell {
 #   background-color: #fafbfc;}



