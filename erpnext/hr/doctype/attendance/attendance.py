# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import getdate, nowdate,get_time, time_diff,time_diff_in_seconds,get_datetime,cint, time_diff_in_hours,date_diff, now, global_date_format, format_time,format_datetime, now_datetime,add_months
from frappe import _, msgprint
from frappe.model.document import Document
from erpnext.hr.utils import set_employee_name
import datetime, calendar, time
from calendar import monthrange
from time import mktime
from datetime import datetime
from erpnext.hr import is_overtime_exceeded
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
import jwt




class Attendance(Document):
	def validate_duplicate_record(self):
		res = frappe.db.sql("""select name from `tabAttendance` where employee = %s and attendance_date = %s
			and name != %s and docstatus = 1""",
			(self.employee, self.attendance_date, self.name))
		if res:
			frappe.throw(_("Attendance for employee {0} is already marked").format(self.employee))

		set_employee_name(self)

	def check_leave_record(self):
		leave_record = frappe.db.sql("""select leave_type, half_day from `tabLeave Application`
			where employee = %s and %s between from_date and to_date and status = 'Approved'
			and docstatus = 1""", (self.employee, self.attendance_date), as_dict=True)
		if leave_record:
			if leave_record[0].half_day:
				self.status = 'Half Day'
				frappe.msgprint(_("Employee {0} on Half day on {1}").format(self.employee, self.attendance_date))
			else:
				self.status = 'On Leave'
				self.leave_type = leave_record[0].leave_type
				frappe.msgprint(_("Employee {0} on Leave on {1}").format(self.employee, self.attendance_date))
		if self.status == "On Leave" and not leave_record:
			frappe.throw(_("No leave record found for employee {0} for {1}").format(self.employee, self.attendance_date))

	def validate_attendance_date(self):

		date_of_joining = frappe.db.get_value("Employee", self.employee, "date_of_joining")

		if getdate(self.attendance_date) > getdate(nowdate()):
			frappe.throw(_("Attendance can not be marked for future dates"))
		elif date_of_joining and getdate(self.attendance_date) < getdate(date_of_joining):
			frappe.throw(_("Attendance date can not be less than employee's joining date"))

		#if self.departure_time != '00:00:0':
		#	if get_time(self.attendance_time) >= get_time(self.departure_time):
		#		frappe.throw(_("Attendance Time can not be more than Departure time"))

		#if self.departure_time:
		#	exit_per = frappe.db.get_value("Exit permission", {'employee':self.employee,'permission_type':'Exit with return','permission_date':self.attendance_date}, "to_date")
		#	if not exit_per:
		#		frappe.throw(_("Not Allowed! Exit with return permission date does not exist"));

		#if self.departure_time != '0':			
		#	if self.attendance_time == self.departure_time:
		#		frappe.throw(_("Attendance Time can not be equal Departure time"))

		attendance_day = calendar.day_name[getdate(self.attendance_date).weekday()]
		emp_details = frappe.db.get_value("Employee Employment Detail", self.employee,["work_shift","morning_delay_in_minutes"], as_dict=1)
		morning_delay_minutes= emp_details.morning_delay_in_minutes
		if not emp_details.work_shift:
			frappe.throw(_("Work shift does not Exist"))

		employee_end_time = frappe.db.get_value("Work Shift Details", {"parent":emp_details.work_shift,"day":attendance_day}, "end_work")
		next_day = frappe.db.get_value("Work Shift Details", {"parent":emp_details.work_shift,"day":attendance_day}, "next_day")
		employee_end_time = self.attendance_time
		#if not employee_end_time:
		#	frappe.throw(_("Work shift does not Exist"))
		#if next_day == 1:
		#	employee_end_time = self.attendance_time
		#if get_time(self.attendance_time) > get_time(employee_end_time):
		#	frappe.throw(_("Attendance time can not be more than employee's end time shift"))
		
		employee_start_time = frappe.db.get_value("Work Shift Details", {"parent":emp_details.work_shift,"day":attendance_day}, "start_work")
		#####New07022019
		
		diff_time = frappe.db.sql("select format(((TIME_TO_SEC('%s')-TIME_TO_SEC('%s'))/60),0) as diff" %( str(self.attendance_time), str(get_time(employee_start_time) ) ))
		if float(diff_time[0][0]) < 0:
			self.attendance_time = employee_start_time

		if not emp_details.morning_delay_in_minutes:
			morning_delay_minutes = frappe.db.get_value("HR Settings", None, "morning_delay")
			if not morning_delay_minutes:
				frappe.throw(_("Add a value for Morning Delay Minutes in HR Settings"))

		if self.is_new() and employee_start_time and self.attendance_time and self.docstatus<2:
			try:
				diff_time = frappe.db.sql("select format(((TIME_TO_SEC('%s')-TIME_TO_SEC('%s'))/60),0) as diff" %( str(self.attendance_time), str(get_time(employee_start_time) ) ))

				if float(diff_time[0][0]) > 0:
					import datetime
					diff_late = datetime.timedelta(seconds=round( float(diff_time[0][0] or 0.0),1) *60 )
					if float(diff_time[0][0]) > float(morning_delay_minutes):
						doc = frappe.new_doc('Exit permission')
						doc.update({
							'employee':self.employee,
							'permission_date': getdate(self.attendance_date),
							'from_date': get_time(employee_start_time),
							'to_date': get_time(self.attendance_time),
							'reason': _("Late System Auto Entry"),
							'permission_type': "Morning Late",
							'late_diff':diff_late ,
							'docstatus': 0,
							'workflow_state':'Pending Request'
						})
						doc.save(ignore_permissions=True)


					if float(diff_time[0][0]) <= float(morning_delay_minutes) :
						doc = frappe.new_doc('Exit permission')
						doc.update({
							'employee':self.employee,
							'permission_date': getdate(self.attendance_date),
							'from_date': get_time(employee_start_time),
							'to_date': get_time(self.attendance_time),
							'reason': _("Late System Auto Entry"),
							'permission_type': "Morning Late",
							'late_diff': diff_late ,
							'docstatus': 1,
							'workflow_state':'Final Approval'
						})	
						doc.save(ignore_permissions=True)

			except: 
				frappe.throw(_("Attendance Time can not be less than employee's start time shift"))
	
		elif not employee_start_time: 
			frappe.throw(_("Start Time Work Shift does not exist for that day"))
		
		
		



	def add_overtime(self,attendance_day,employee_work_shift,employee_end_time):
		#if is_overtime_exceeded(self.employee, self.attendance_date):		
		#	frappe.throw(_("Overtime is exceeded!"))

		holiday_list = frappe.db.get_value("Employee", self.employee, "holiday_list")
		if holiday_list:
			#holidays = frappe.get_list("Holiday",fields=["holiday_date"], filters={'parent':holiday_list}, as_list=1)
			holidays = frappe.get_all("Holiday", fields=["holiday_date"],filters={'parent':holiday_list})
			from_time= frappe.db.sql('select TIMESTAMP(%s , %s)',(self.attendance_date, self.attendance_time))[0][0]
			to_time= frappe.db.sql('select TIMESTAMP(%s , %s)',(self.attendance_date, employee_end_time))[0][0]
			#hours = frappe.db.sql("select format(((TIME_TO_SEC('%s')-TIME_TO_SEC('%s'))/60),0)" %(str(to_time), str(from_time)))[0][0]
			for holiday in holidays:
				if holiday.holiday_date == getdate(self.attendance_date):
					if att_over:
						doc= frappe.db.sql('update `tabTimesheet Detail` set to_time=%s where parent=%s and from_time=%s and hours=%s',(to_time,att_over,from_time,str(time_diff_in_hours(to_time,from_time))))
					else:
						overtime = frappe.new_doc('Timesheet')
						overtime.update({
							'name':self.employee_name,
							'employee':self.employee,
							'start_date': getdate(nowdate()),
							'to_date': getdate(nowdate()),
							'time_logs': [{
								'activity_type':_('Auto Entry: Attendance in holiday date'),
								'from_time':from_time,
								'to_time': to_time,
								'hours': time_diff_in_hours(to_time,from_time)
									}],
							'type':'Normal',
							'docstatus': 0,
							'workflow_state':'Pending Request'
						})
						overtime.insert(ignore_permissions=True)

	def validate_employee(self):
		emp = frappe.db.sql("select name from `tabEmployee` where name = %s and status = 'Active'",
		 	self.employee)
		if not emp:
			frappe.throw(_("Employee {0} is not active or does not exist").format(self.employee))

	def validate(self):
		self.docstatus = 1
		footprint_clock_closing = frappe.db.get_value("HR Settings", None, "footprint_clock_closing")

		#if footprint_clock_closing and get_time(self.attendance_time) >= get_time(footprint_clock_closing):
		#	frappe.throw(_("Not Allowed! Footprint Clock is closed"))
		#frappe.throw( frappe.get_request_header("X-Frappe-CSRF-Token"))
		#if self.attendance_type == 'Attendance':
		#	self.departure_time = '0'
		#	self.attendance_time = time.strftime("%X")
	
		#elif self.attendance_type =='Departure':
		#	self.attendance_time = get_time(self.attendance_time)
		#	self.departure_time = time.strftime("%X")
		#	att = frappe.db.sql("select name from `tabAttendance` where employee = %s and attendance_date=%s and docstatus !=2 order by name desc LIMIT 1",(self.employee,self.attendance_date))
		#	if att:
		#		frappe.db.sql("update `tabAttendance` set departure_time=%s,departure_date=%s where employee = %s and attendance_date=%s and docstatus !=2",(time.strftime("%X"),getdate(nowdate()),self.employee,self.attendance_date))
				
			
		from erpnext.controllers.status_updater import validate_status
		validate_status(self.status, ["Present", "Absent", "On Leave", "Half Day"])
		self.validate_duplicate_record()
		self.validate_attendance_date()
		#self.check_leave_record()


	def api_post(self,data):
		message=""
		mylist= ""
		try:
			mylist = frappe.get_doc(data).insert().as_dict()
		except Exception as e:
			message = str(e)

		if message: 
			code = 403
		else: code = 200

		return {"status":{"success":"sucess","code":code,"message":message},"list":mylist}


#### function
@frappe.whitelist(allow_guest=True)
def update_holiday(employee=None, holiday_list=None, shift_change_date=None):
	print "update_holiday"
	#send_aler_email("update_holiday Script Running")
	def call_holiday(emp,employee_name, holiday_list,shift_change_date=None):
		today = datetime.today()
		#if not shift_change_date:
		#	shift_change_date= today
		cur_month = today.month
		if not holiday_list:
			holiday_list = get_holiday_list_for_employee(emp)
		if holiday_list:
			#holidays = frappe.db.sql_list('''select holiday_date from `tabHoliday` where parent=%s''', (holiday_list))
			holiday_filter = [["parent", "=", holiday_list], ["holiday_date", "<=", today]]
			holidays = frappe.get_all("Holiday", fields=["holiday_date"], filters=holiday_filter)
			for holiday in holidays:
				day = calendar.day_name[getdate(holiday.holiday_date).weekday()]
				if shift_change_date:
					if getdate(holiday.holiday_date) <= getdate(shift_change_date):
						print str(getdate(holiday.holiday_date))+"  dd  "+str(getdate(shift_change_date))
						update_att_holiday(emp, employee_name, day,holiday.holiday_date)
				else :						
					update_att_holiday(emp, employee_name, day,holiday.holiday_date)
	if employee:
		employee_name = frappe.db.get_value("Employee",{'status':'Active'},"employee_name")
		call_holiday(employee,employee_name, holiday_list,shift_change_date)
	else:
		employees = frappe.get_all("Employee", fields=["name","employee_name"],filters={'status':'Active'})
		for emp in employees:
			call_holiday(emp.name,emp.employee_name, holiday_list)
		

#### Hook event
def onholiday(doc, method):
	print "onholiday"
	#send_aler_email("onholiday Script Running")
	today = datetime.today()
	cur_month = today.month
	employees = frappe.get_all("Employee", fields=["name","employee_name"],filters={'status':'Active'})
	for emp in employees:
		#holiday_list = frappe.db.get_value("Employee Employment Detail", emp.name, "holiday_list")
		holiday_list = get_holiday_list_for_employee(emp)
		if holiday_list:
			#holidays = frappe.db.sql_list('''select holiday_date from `tabHoliday` where parent=%s''', (holiday_list))
			holiday_filter = [["parent", "=", holiday_list], ["holiday_date", "<=", today]]
			holidays = frappe.get_all("Holiday", fields=["holiday_date"], filters=holiday_filter)
			for holiday in holidays:
				day = calendar.day_name[getdate(holiday.holiday_date).weekday()]
				#print str(day)+"  dd  "+str(today)
				#if day <= today:
				update_att_holiday(emp.name,emp.employee_name,day,holiday.holiday_date)


def update_att_holiday(emp,employee_name,day,holiday):
	print str(day)
	att_time, att_status, dep_time, dep_status= None, None, None, None
	employee_work_shift = frappe.db.get_value("Employee Employment Detail", emp, "work_shift")
	employee_start_time = frappe.db.get_value("Work Shift Details", {"parent":employee_work_shift,"day":day}, "start_work")
	if not employee_start_time:
		frappe.db.get_value("Work Shift Details", {"parent":employee_work_shift,"day":"Saturday"}, "start_work")

	employee_end_time = frappe.db.get_value("Work Shift Details", {"parent":employee_work_shift,"day":day}, "end_work")
	if not employee_end_time:
		frappe.db.get_value("Work Shift Details", {"parent":employee_work_shift,"day":"Saturday"}, "end_work")

	att_doc = frappe.db.get_value("Attendance",{ "docstatus":("<",2),"employee": emp, "attendance_date":holiday}, ["name","status"], as_dict=1) or None
	print str(employee_start_time)
	if att_doc: att_time, att_status= att_doc.name, att_doc.status

	dep_doc = frappe.db.get_value("Departure", {"employee":emp,"departure_date":holiday ,"docstatus":("<", 2)}, ["name","status"], as_dict=1) or None
	if dep_doc: dep_time, dep_status= dep_doc.name, dep_doc.status

	if not employee_start_time:
		print(_("Start Time Work Shift does not exist for that day"))
		return
	#frappe.msgprint(str(holiday) +" "+ emp.name)
	if att_status !='On Holiday':
		if att_doc:
			print emp+' '+ att_status
			if att_status =='Absent':
				att = frappe.get_doc('Attendance',att_time)
				att.status='On Holiday'
				att.attendance_time=employee_start_time
				att.flags.ignore_validate = True
				att.flags.ignore_validate_update_after_submit = True 
				att.save(ignore_permissions=True)
				print "updated"
				#frappe.msgprint("updated")

		elif not att_doc or att_doc==None:
			#frappe.msgprint("not")
			att = frappe.new_doc('Attendance')
			att.update({
				'employee':emp,
				'employee_name':employee_name,
				'attendance_time':employee_start_time,
				'attendance_date':holiday,
				'docstatus':1,
				'status':'On Holiday'
					})
			att.flags.ignore_validate = True
			att.insert(ignore_permissions=True)
			print "added"
			#frappe.msgprint("added")

		if dep_doc:
			if dep_status =='Absent':
				dep = frappe.get_doc('Departure',dep_time)
				dep.status='On Holiday'
				dep.departure_time=employee_end_time
				dep.flags.ignore_validate = True
				dep.flags.ignore_validate_update_after_submit = True 
				dep.save(ignore_permissions=True)
				print "updated"


		elif not dep_doc:
			dep = frappe.new_doc('Departure')
			dep.update({
				'employee':emp,
				'employee_name':employee_name,
				'departure_time':employee_end_time,
				'departure_date':holiday,
				'docstatus':1,
				'status':'On Holiday'
					})
			dep.flags.ignore_validate = True
			dep.insert(ignore_permissions=True)
			print "added"
			#frappe.msgprint("depadded")

	
@frappe.whitelist()
def attendance_hrs():
	user= frappe.local.session.user
	employee = frappe.db.get_value("Employee Personal Detail", {'user_id':user}, "name")
	return frappe.db.sql("select round(TIMESTAMPDIFF(MINUTE,attendance_time,CURRENT_TIME())/60,2) as total_hours from `tabAttendance` where attendance_date =CURDATE() and docstatus!=2 and employee=%s",user)

#Test Email
@frappe.whitelist()
def send_aler_email(msg):
	from frappe.utils import get_url
	print "email"
	try:
		frappe.sendmail(
			recipients= "maysaaelsafadi@gmail.com",
			sender = "mesa_safd@hotmail.com",
			subject = msg+(" from {} Today").format(get_url()),
			message = msg
		)
		return _("Email sent")
	except frappe.OutgoingEmailError:
		pass

@frappe.whitelist(allow_guest=True)
def check_attendance_monthly(mydate=None):
	#date, hour
	#now = now_datetime()
	 #get_datetime(date)
	#month = frappe.db.get_value("HR Settings", None, "month")
	
	if not mydate:
		mydate = now_datetime()
	#hour = frappe.db.get_value("HR Settings", None, "hour")
	#if not hour: hour =18
	#month_range= monthrange(cint(getdate(mydate).year), int(getdate(mydate).month))[1]
	month_range = abs(date_diff ( add_months(datetime.today(), -1), mydate))
	for d in range(month_range):
		try:
			day = str(getdate(mydate).year)+'-'+str(getdate(mydate).month)+'-'+str(d+1) #frappe.utils.add_days(datetime.today(), -d) 
			hour = get_time(mydate).hour
			#print day
			if getdate(day) < getdate(now_datetime()):
				check_attendance(day, hour,True)
		except ValueError:
        		continue

	frappe.msgprint(_("Absent Records Added"))

def check_attendance(ddate=nowdate(),hour=20, nowF=False):
	#print str(ddate)
	#ddate = '2019-01-09'
	#send_aler_email("Absent Script Running")
	#frappe.msgprint(str(nowF)+str(now_datetime()))
	#frappe.msgprint ("dd "+str(ddate))
	employees = frappe.get_all("Employee Employment Detail", fields=["name","work_shift","employee_name","scheduled_confirmation_date","date_of_joining"],filters={'status':'Active'})
	today = calendar.day_name[getdate(ddate).weekday()];
	#today= day #getdate(nowdate()) #'2018-08-13' 
	cur_time = get_time(now_datetime())
	#print cur_time.hour
	for emp in employees:
		holiday_list = get_holiday_list_for_employee(emp)
		if holiday_list:
			holiday_filter = [["parent", "=", holiday_list], ["holiday_date", "<=", ddate]]
			holidays = frappe.get_all("Holiday", fields=["holiday_date"], filters=holiday_filter)
			for holiday in holidays:
				if str(ddate) == str(holiday):
					print "False"
					return False

			
		attendance = frappe.db.get_value("Attendance", {"employee":emp.name,"attendance_date":getdate(ddate),"docstatus":("!=", 2)}, "name")
		departure = frappe.db.get_value("Departure", {"employee":emp.name,"departure_date":getdate(ddate),"docstatus":("!=", 2)}, "name")

		#emp_work_shift = frappe.db.get_value("Employee Employment Detail", emp.name, "work_shift")
		#end_time = frappe.db.get_value("Work Shift Details", {"parent":emp_work_shift,"day":today}, "end_work")
		#print cur_time.hour
		if  emp.date_of_joining :
			date_of_joining =  emp.date_of_joining
		if emp.scheduled_confirmation_date:
			date_of_joining =  emp.scheduled_confirmation_date

		if nowF:
			condition = (not attendance and not departure ) or (not attendance or not departure) or (not attendance and departure)
		else: 
			condition = ((not attendance and not departure ) or (not attendance or not departure) or (not attendance and departure)) and cur_time.hour>= hour 
		if frappe.db.get_value("Employee",{'status':'Active','employee_number': emp.name}, "name") and condition and getdate(ddate) >= date_of_joining :

			if not attendance and departure:
				dep = frappe.get_doc('Departure',departure)
				dep.docstatus=2
				dep.flags.ignore_validate = True
				dep.flags.ignore_validate_update_after_submit = True 
				dep.save(ignore_permissions=True)


			atten = frappe.new_doc('Attendance')
			atten.update({'name':emp.employee_name,'employee_name':emp.employee_name,'employee':emp.name,'status':'Absent',"docstatus":1,"attendance_date":getdate(ddate),"attendance_time":'00:00:00'})
			atten.flags.ignore_validate=True
			atten.save(ignore_permissions=True)

			dept = frappe.new_doc('Departure')
			dept.update({'name':emp.employee_name,'employee_name':emp.employee_name,'employee':emp.name,'status':'Absent',"docstatus":1,"departure_time":'00:00:00',"departure_date":getdate(ddate)})
			dept.flags.ignore_validate=True
			dept.insert(ignore_permissions=True)
			print 'added |' +str(emp.name)
	#frappe.msgprint(_("Added"))

		#if not departure:
			#return frappe.db.sql("insert into tabDeparture (employee_name,employee,departure_time,departure_date)\
 #VALUES ( %s, %s, %s, %s)",(emp.employee_name,emp.name,end_time,today))
		#	dept = frappe.new_doc('Departure')
		#	dept.update({'name':emp.employee_name,'employee_name':emp.employee_name,'employee':emp.name,"departure_time":end_time,"departure_date":today})
		#	dept.flags.ignore_validate=True
		#	dept.insert(ignore_permissions=True)

		

###################################################### For C.P ##################################################################
#Edited By Maysaa
@frappe.whitelist(allow_guest=True)
def get_total_hrs(employee,date):
	#date= nowdate()
	total_hrs= 0
	total_hours  = frappe.db.sql("select round(TIMESTAMPDIFF(MINUTE,attendance_time,departure_time)/60,2) as total_hours from tabAttendance where docstatus = 1 and employee=%s and month(attendance_date)=month(%s) and year(attendance_date)= year(%s) order by employee, attendance_date" , (employee,date,date), as_dict=1)

	for i in range(len(total_hours)):
		total_hrs = total_hrs + int(total_hours[i].total_hours)
	return total_hrs


@frappe.whitelist(allow_guest=True)
def get_overtime_hrs(employee,date):
	date= nowdate()
	total_hrs= 0
	overtime_hours  = frappe.db.sql("select round(total_hours,2) as overtime_hours from tabTimesheet where docstatus = 1 and employee=%s and month(start_date)=month(%s) and year(start_date)= year(%s) order by employee, start_date" , (employee,date,date), as_dict=1)

	for i in range(len(overtime_hours)):
		total_hrs = total_hrs + int(overtime_hours[i].overtime_hours)
	return total_hrs


@frappe.whitelist(allow_guest=True)
def all_emp_total_hrs():
	date= nowdate()
	total_hrs= 0
	total_hours  = frappe.db.sql("select round(TIMESTAMPDIFF(MINUTE,attendance_time,departure_time)/60,2) as total_hours from tabAttendance where docstatus = 1  and attendance_date <= %s order by employee, attendance_date" , date, as_dict=1)

	for i in range(len(total_hours)):
		total_hrs = total_hrs + int(total_hours[i].total_hours)
	return total_hrs


@frappe.whitelist(allow_guest=True)
def emp_orders(employee):
	date= nowdate()
	last_orders  = frappe.db.sql("SELECT * FROM (select name,docstatus,employee, 'Timesheet' as type, creation as ddate from `tabTimesheet` union all select name,docstatus,employee, 'Leave Application' as type, creation as ddate from `tabLeave Application` union all select name,docstatus,employee, 'Exit permission' as type, creation as ddate from `tabExit permission` union all select name,docstatus,employee, 'Employee Edit Time' as type, creation as ddate from `tabEmployee Edit Time` union all select name,docstatus,employee, 'Employee Loan Application' as type, creation as ddate from `tabEmployee Loan Application`) as u where employee=%s and month(ddate)=month(now()) ORDER BY docstatus desc LIMIT 10" , employee, as_dict=1)
	return last_orders


@frappe.whitelist(allow_guest=True)
def all_emp_orders():
	date= nowdate()
	last_orders  = frappe.db.sql("SELECT u.name,u.docstatus,u.employee, u.type,e.employee_name, date(u.ddate) as ddate FROM (select name,docstatus,employee, 'Timesheet' as type, creation as ddate from `tabTimesheet` union all select name,docstatus,employee, 'Leave Application' as type, creation as ddate from `tabLeave Application` union all select name,docstatus,employee, 'Exit permission' as type, creation as ddate from `tabExit permission` union all select name,docstatus,employee, 'Employee Edit Time' as type, creation as ddate from `tabEmployee Edit Time` union all select name,docstatus,employee, 'Employee Loan Application' as type, creation as ddate from `tabEmployee Loan Application`) as u join tabEmployee as e on u.employee=e.name where month(ddate)=month(now()) ORDER BY ddate desc " , as_dict=1)
	return last_orders


@frappe.whitelist(allow_guest=True)
def employment_type_percentage():
	arr=[]
	employment_type = frappe.db.sql("select name from `tabEmployment Type`",as_dict=1)
	for i in range(len(employment_type)):
		percentage = frappe.db.sql("""select round((count(*)*100),2) as percentage from `tabEmployee Employment Detail` where employment_type=%s""" ,employment_type[i].name, as_dict=1)
		arr.append([employment_type[i].name, percentage[0].percentage])
	return arr


@frappe.whitelist(allow_guest=True)
def leave_type_percentage(user):
	arr=[]
	leave_type = frappe.db.sql("select name from `tabLeave Type`",as_dict=1)
	for i in range(len(leave_type)):
		percentage = frappe.db.sql("""select round((count(*)/100),2) as percentage from `tabLeave Application` as t1 join `tabEmployee` as t2 on t1.employee= t2.name where t2.user_id=%s and t1.leave_type=%s""" ,(user,leave_type[i].name), as_dict=1)
		arr.append([leave_type[i].name, percentage[0].percentage])
	return arr


@frappe.whitelist(allow_guest=True)
def all_leave_type_percentage():
	arr=[]
	leave_type = frappe.db.sql("select name from `tabLeave Type`",as_dict=1)
	for i in range(len(leave_type)):
		percentage = frappe.db.sql("""select round((count(*)/10),2) as percentage from `tabLeave Application` where leave_type=%s""" ,leave_type[i].name, as_dict=1)
		arr.append([leave_type[i].name, percentage[0].percentage])
	return arr


@frappe.whitelist(allow_guest=True)
def employee_total():
	arr=[]
	today = datetime.today()
	cur_year = today.year

	#active_employees = frappe.get_all("Employee Employment Detail", filters = { "status": "Active", "company":get_default_company() }, fields = ["date_of_joining"])
	#for employee in active_employees:
	#	if cur_year > employee.date_of_joining:
	#		cur_year

	years = [cur_year, cur_year+1, cur_year+2, cur_year+3, cur_year+4, cur_year+5, cur_year+6]
	for i in range(len(years)):
		total = frappe.db.sql("""select count(*) as total  from `tabEmployee Employment Detail` where year(date_of_joining)=%s""" ,years[i], as_dict=1)
		arr.append(total[0].total)
	return arr
		

@frappe.whitelist(allow_guest=True)
def monthly_emp_total_hrs():
	#month=  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,12]
	now = now_datetime()
	month_range= monthrange(cint(now.year), now.month)[1]
	arr=[None] * month_range

	total_hours  = frappe.db.sql("select ifnull(sum(round(TIMESTAMPDIFF(MINUTE,attendance_time,dept.departure_time)/60,2)),0) as total_hours,ifnull(day(attendance_date),0) as day from tabAttendance as att left join  tabDeparture as dept on att.attendance_date=dept.departure_date and dept.docstatus = 1 where att.docstatus = 1  and month(attendance_date) = month(now()) and year(attendance_date) = year(now()) group by day" , as_dict=1)
	return total_hours

	for j in range(month_range):
		if j <len(total_hours):
			#arr[total_hours[j].day:total_hours[j].day] =total_hours[j].total_hours
			arr[total_hours[j].day]= total_hours[j].total_hours
		else: 
			arr[j]=0
	return arr
	



@frappe.whitelist(allow_guest=True)
def mytest():
	return frappe.db.sql("SELECT CONVERT( %s ,datetime(6))",str(format_datetime('15:49:46.000000')) )#frappe.get_doc("DocType", "User")
			






