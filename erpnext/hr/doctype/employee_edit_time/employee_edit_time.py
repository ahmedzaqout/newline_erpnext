# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.model.document import Document
from frappe.utils import getdate, nowdate,get_time, time_diff,time_diff_in_seconds,get_datetime,cint,time_diff_in_hours
import datetime, calendar
from calendar import monthrange
import datetime as dt
from erpnext.hr import is_overtime_exceeded

class EmployeeEditTime(Document):
	def validate(self):
		self.morning_late= " "
		self.validate_duplicate_record()
		self.validat_morninig_late()

		if getdate(self.attendance_date) > getdate(nowdate()):
			frappe.throw(_("Edit Time can not be marked for future dates"))

		if get_time(self.attendance_time) >= get_time(self.departure_time):
			frappe.throw(_("Attendance Time can not be more than Departure time"))


		#morning_late = frappe.db.get_value("Exit permission", {'employee':self.employee,'permission_type':'Morning Late','permission_date':self.attendance_date,'docstatus':("<",2)}, ["late_diff","from_date","to_date"])
		#if morning_late and morning_late[0]:
		#	late_msg= _("You have a Morning Late for about {0} hour, from {1} to {2}").format(morning_late[0],str(morning_late[1]),str(morning_late[1])) 
		#	self.morning_late= late_msg
		#	frappe.msgprint( late_msg )
		
		self.validate_permissions()

	def validate_permissions(self):
		exit_perm_msg=" "
		total_ext_diff=0.0
		exit_perm = frappe.db.sql("select e.employee,e.docstatus, e.permission_date, r.diff_exit as ext_diff,e.from_date,r.to_date from `tabExit permission` as e join `tabExit permission` as r on e.name = r.exit_order_name where e.employee=%s and e.permission_date=%s",(self.employee,self.attendance_date),as_dict=1)
		for e_per in exit_perm:
			if e_per: 
				exit_perm_msg+= " "+_("from {0} to {1},").format(e_per.from_date, e_per.to_date)
				total= get_datetime(e_per.ext_diff)
				total= total.hour*60+total.minute+total.second/60
				total_ext_diff+= total or 0.0

		if exit_perm_msg != " ": self.exit_per = _("You have an exit permission for about {0} hour(s)").format(str(datetime.timedelta(seconds=round(total_ext_diff,1)*60))) +" "+ exit_perm_msg
		return total_ext_diff


	def validate_duplicate_record(self):
		res = frappe.db.sql("""select name from `tabEmployee Edit Time` where employee = %s and attendance_date = %s
			and name != %s and docstatus = 1""",
			(self.employee, self.attendance_date, self.name))
		if res:
			frappe.throw(_("Edit Time for employee {0} is already marked").format(self.employee))

	def validat_morninig_late(self):
		attendance_day = calendar.day_name[getdate(self.attendance_date).weekday()];
		employee_work_shift = frappe.db.get_value("Employee Employment Detail", self.employee, "work_shift")

		employee_end_time = frappe.db.get_value("Work Shift Details", {"parent":employee_work_shift,"day":attendance_day}, "end_work")
		if not employee_end_time:
			frappe.throw(_("Work shift does not Exist"))

		#if get_time(self.departure_time) > get_time(employee_end_time):
		#	frappe.throw(_("Attendance Departure can not be more than employee's end time shift"))
		if get_time(self.attendance_time) > get_time(employee_end_time):
			frappe.throw(_("Attendance time can not be more than employee's end time shift"))
			
		employee_start_time = frappe.db.get_value("Work Shift Details", {"parent":employee_work_shift,"day":attendance_day}, "start_work")
		morning_delay_minutes = frappe.db.get_value("HR Settings", None, "morning_delay")


		morning_late = frappe.db.get_value("Exit permission", {'employee':self.employee,'permission_type':'Morning Late','permission_date':self.attendance_date,'docstatus':("<",2)}, "name")


		diff_time = frappe.db.sql("select format(((TIME_TO_SEC('%s')-TIME_TO_SEC('%s'))/60),0)" %(str(self.attendance_time), str(employee_start_time)))
		diff_late = datetime.timedelta(seconds=round( float(diff_time[0][0] or 0.0),1) *60 )
		late_msg= _("You have a Morning Late for about {diff_late} hour, from {fromtime} to {totime}").format(diff_late=diff_late,fromtime=get_time(employee_start_time),totime=get_time(self.attendance_time)) 


		if employee_start_time:
			if get_time(self.attendance_time) > get_time(employee_start_time):
				if float(diff_time[0][0]) > float(morning_delay_minutes) and self.docstatus==1:
					if not morning_late:	
						self.add_morninig_late( diff_late, get_time(employee_start_time), 0, 'Pending Request' )
						self.morning_late= late_msg
						frappe.msgprint( late_msg )
					else:
						self.update_morninig_late(diff_late, morning_late, get_time(employee_start_time) )
						self.morning_late= late_msg
						frappe.msgprint( late_msg )

				if float(diff_time[0][0]) <=1 and self.docstatus==1:
					if not morning_late:	
						self.add_morninig_late(diff_late, get_time(employee_start_time), 1, 'Final Approval' )
					else:
						self.update_morninig_late(diff_late, morning_late, get_time(employee_start_time) )

			else: 
				frappe.throw(_("Attendance Time can not be less than employee's start time shift"))
	
		else: frappe.throw(_("Start Time Work Shift does not exist for that day"))



	def add_morninig_late(self,diff_late,from_date,docstatus,workflow_state):
		doc = frappe.new_doc('Exit permission')
		doc.update({
			'employee':self.employee,
			'permission_date': self.attendance_date,
			'from_date': from_date,
			'to_date': get_time(self.attendance_time),
			'late_diff': diff_late,
			'reason': _("Late System Auto Entry"),
			'permission_type': "Morning Late",
			'docstatus': docstatus,
			'workflow_state':workflow_state
			})
		doc.save(ignore_permissions=True)


	def update_morninig_late(self,diff_late,morning_late,from_date):
		doc = frappe.get_doc('Exit permission',morning_late)
		doc.update({
			'permission_date': self.attendance_date,
			'from_date': from_date,
			'to_date': get_time(self.attendance_time),
			'late_diff': diff_late
			})
		doc.flags.ignore_validate = True
		doc.flags.ignore_validate_update_after_submit = True
		doc.save(ignore_permissions=True)
	
	def after_insert(self):
		sender = frappe.get_all("User",['name'],filters={"employee":self.employee})
		recivers = frappe.db.sql("SELECT DISTINCT u.name  FROM tabUser u join`tabHas Role` hr on u.name=hr.parent  WHERE role in (%s,%s)", ("HR User","HR Manager"))
		
		for rec in recivers:
			frappe.get_doc({"Doctype":"Notification",
					"tilte" : "طلب تعديل دوام جديد",
					"message" : "قام الموظف {0} بإنشاء طلب تعديل دوام".format(self.employee),
					"reciver" : rec[0],
					"seen" : 0,
					"doctype":"Notification",
					"doctype_type" : "Employee Edit Time",
					"doctype_name" : self.name
					}).insert(ignore_permissions=True)	

	def on_submit(self):
		diff_time = frappe.db.sql("select format(((TIME_TO_SEC('%s')-TIME_TO_SEC('%s'))/60),0)" %(str(self.attendance_time), str(self.departure_time)))[0][0]

		if diff_time <0: frappe.throw(_("Departure Time Should be more than Attendance Time"))


		#att_time = frappe.db.get_value("Attendance",{ "docstatus":("<",2),"employee": self.employee, "attendance_date":self.attendance_date}, ["name","attendance_time"])
		att_time = frappe.db.get_value("Attendance",{ "docstatus":("<",2),"employee": self.employee, "attendance_date":self.attendance_date}, "name")
		dep_time = frappe.db.get_value("Departure",{ "docstatus":("<",2),"employee": self.employee, "departure_date":self.attendance_date}, "name")

		if not att_time and diff_time >0:
			att = frappe.new_doc('Attendance')
			att.update({
				'employee':self.employee,
				'employee_name':self.employee_name,
				'attendance_time':self.attendance_time,
				'attendance_date':self.attendance_date,
				'docstatus':1
					})
			#att.flags.ignore_validate = True
			att.insert(ignore_permissions=True)

		if not dep_time and diff_time >0:
			dep = frappe.new_doc('Departure')
			dep.update({
				'employee':self.employee,
				'employee_name':self.employee_name,
				'departure_time':self.departure_time,
				'departure_date':self.attendance_date,
				'docstatus':1
					})
			#dep.flags.ignore_validate = True
			dep.insert(ignore_permissions=True)
			#frappe.db.sql("""insert into `tabAttendance`  (name,employee,attendance_time,attendance_date) VALUES(%s,%s,%s)""",(self.employee,str(self.attendance_time),str(self.attendance_date)))
			#frappe.db.sql("""insert into `tabDeparture`  (name,employee,departure_time,departure_date) VALUES(%s,%s,%s)""",(self.employee,str(self.departure_time),str(self.attendance_date)))
	

		if att_time and diff_time >0:
			frappe.db.sql("""UPDATE `tabAttendance` SET attendance_time = %s , status='Present' WHERE employee = %s and name=%s""",(str(self.attendance_time), self.employee, att_time))

		if dep_time and diff_time >0:
			frappe.db.sql("""UPDATE `tabDeparture` SET departure_time= %s , status='Present' WHERE employee = %s and name=%s""",(str(self.departure_time), self.employee, dep_time))




		day = calendar.day_name[getdate(self.attendance_date).weekday()];
		employee_work_shift = frappe.db.get_value("Employee Employment Detail", self.employee, "work_shift")
		employee_start_time = frappe.db.get_value("Work Shift Details", {"parent":employee_work_shift,"day":day}, "start_work")
		employee_end_time = frappe.db.get_value("Work Shift Details", {"parent":employee_work_shift,"day":day}, "end_work")

		att_from_time= frappe.db.sql('select TIMESTAMP(%s , %s)',(self.attendance_date, employee_end_time))[0][0]
		to_time= frappe.db.sql('select TIMESTAMP(%s , %s)',(self.attendance_date, self.departure_time))[0][0]
		#att_time = frappe.db.get_value("Attendance",{ "docstatus":("<",2),"employee": self.employee, "attendance_date":self.attendance_date}, "attendance_time")
		att_over = frappe.db.get_value("Timesheet",{ "employee":self.employee, "start_date":self.attendance_date,"docstatus":("<",2)}, "name")


		self.add_overtime(att_over,to_time,att_from_time,employee_start_time,employee_end_time)
		
		sender = frappe.session.user
		reciver_name=""
		recivers = frappe.get_list("User",['name','full_name'],filters={"employee":self.employee})
		if not recivers:
			recivers = frappe.get_list("Employee",['user_id'],filters={"name":self.employee})
			if recivers:
				reciver_name=recivers[0].user_id
		else:
			reciver_name=recivers[0].name

			
		message=""		
		if self.workflow_state  and("reject" in self.workflow_state or "Rejection" in self.workflow_state) :
			message = """ قام {0} برفض طلب تعديل الدوام""".format(sender)
		else:
			message = """ قام {0} بالموافقة على طلب تعديل الدوام""".format(sender)
		

		frappe.get_doc({"Doctype":"Notification",
				"tilte" : "{0} طلب تعديل الدوام".format(_(self.workflow_state)),
				"message" : message,
				"reciver" : reciver_name,
				"seen" : 0,
				"doctype":"Notification",
				"doctype_type" : "Employee Edit Time",
				"doctype_name" : self.name
				}).insert(ignore_permissions=True)

	

	def add_overtime(self,att_over,to_time,att_from_time,employee_start_time,employee_end_time):
		#if is_overtime_exceeded(self.employee, self.attendance_date):		
		#	frappe.throw(_("Overtime is exceeded!"))

		overtime_max_minutes = frappe.db.get_value("HR Settings", None, "overtime_max_minutes")	
		if not overtime_max_minutes:
			frappe.throw(_("Enter the value of max overtime in HR settings"))

		total_att = time_diff(str(self.departure_time),str(self.attendance_time) )
		shift_att = time_diff(str(employee_end_time),str(employee_start_time) )
		diff = time_diff_in_hours(str(total_att),str(shift_att))

		
		att_time = frappe.db.get_value("Attendance",{ "docstatus":("<",2),"employee": self.employee, "attendance_date":self.attendance_date}, "attendance_time")
		if not att_time: att_time= self.attendance_time

		dep_time= att_time + shift_att	
		dep_timedate= dt.datetime.combine(getdate(self.attendance_date), dt.datetime.strptime(str(dep_time), '%H:%M:%S').time())	

		total_exit= self.validate_permissions()
		#frappe.msgprint(str(total_exit))
		discount_permissions_from_attendance_hours = frappe.db.get_value("HR Settings", None, "discount_permissions_from_attendance_hours")
		if discount_permissions_from_attendance_hours and total_exit!=0.0:
			if diff > total_exit:
				diff = diff- total_exit
			else:
				diff = total_exit- diff
		

		if self.attendance_time:
			if total_att > shift_att and diff*60 > float(overtime_max_minutes):

				if att_over:
					over_det = frappe.get_doc('Timesheet',att_over)
					if frappe.db.exists('Timesheet Detail',{'parent':over_det.name,'activity_type':_('Auto Entry: Overtime Attendance')}):
						time_det = frappe.get_doc('Timesheet Detail',{'parent':over_det.name,'activity_type':_('Auto Entry: Overtime Attendance')})
						time_det.update({
							'from_time':dep_timedate,
							'to_time':to_time,
							'hours':diff
						})
						#time_det.from_time = dep_timedate
						#time_det.to_time = to_time
						time_det.flags.ignore_validate = True
						time_det.flags.ignore_validate_update_after_submit = True 
						time_det.save(ignore_permissions=True)
						update_overtime_total_hrs(over_det)
					else:
						over_det.update({
							'time_logs': [{
							'activity_type':_('Auto Entry: Overtime Attendance'),
							'from_time':dep_timedate,
							'to_time': to_time,
							'hours': diff
								}]
						})
						over_det.flags.ignore_validate = True
						over_det.flags.ignore_validate_update_after_submit = True 
						over_det.save(ignore_permissions=True)
						update_overtime_total_hrs(over_det)
					
				else:
					overtime = frappe.new_doc('Timesheet')
					overtime.update({
						'name':self.employee,
						'employee':self.employee,
						'start_date': getdate(self.attendance_date),
						'to_date': getdate(self.attendance_date),
						'time_logs': [{
							'activity_type':_('Auto Entry: Overtime Attendance'),
							'from_time':dep_timedate,
							'to_time': to_time,
							'hours': diff
								}],
						'type':'compensatory',
						'docstatus': 0,
						'workflow_state':'Pending Request'
						})
					overtime.insert(ignore_permissions=True)
		return "done"


def update_overtime_total_hrs(over_order):
	total = 0.0
	doc = frappe.db.get_list("Timesheet Detail",{ "parent":over_order.name},"hours")
	if doc:
		for d in doc:
			total += d.hours or 0.0

	over_order.update({
		'total_hours':total
		})
	#over_order.total_hours = total
	over_order.flags.ignore_validate_update_after_submit = True 
	over_order.save(ignore_permissions=True)



