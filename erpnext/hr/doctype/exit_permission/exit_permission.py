# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate,nowdate,now,get_time,time_diff_in_hours, flt, getdate, rounded, date_diff,add_days, cint, cstr
import datetime, calendar, time
from dateutil.parser import parse as parse_date



class Exitpermission(Document):
	def validate(self):

		if self.permission_type == 'Morning Late':
			self.sms_for_morning_delay()

		if getdate(self.permission_date) > getdate(nowdate()):
			frappe.throw(_("Exit permission can not be marked for future dates"))

		attendance_day = calendar.day_name[getdate(self.permission_date).weekday()];
		employee_work_shift = frappe.db.get_value("Employee Employment Detail", self.employee, "work_shift")
		employee_start_time = frappe.db.get_value("Work Shift Details", {"parent":employee_work_shift,"day":attendance_day}, "start_work")
		employee_end_time = frappe.db.get_value("Work Shift Details", {"parent":employee_work_shift,"day":attendance_day}, "end_work")
		if not employee_end_time:
			frappe.throw(_("Work shift does not Exist"))
		if not employee_start_time:
			frappe.throw(_("Work shift does not Exist"))

		############
		#if self.is_new() and not self.workflow_state:
		#	self.workflow_state = 'Pending Request'

		if self.permission_type == 'Exit with return':		
			if (self.type== 'Exit' and get_time(self.from_date) < get_time(employee_start_time)):
				frappe.throw(_("Exit permission can not be less than employee's start time shift"))

			if self.type== 'Return' and get_time(self.to_date) < get_time(employee_start_time):
				frappe.throw(_("Return time can not be less than employee's start time shift"))

			#holiday_list = frappe.db.get_value("Employee", self.employee, "holiday_list")
			#if holiday_list:
				#holidays = frappe.get_all("Holiday", fields=["holiday_date"],filters={'parent':holiday_list})
				#for holiday in holidays:
					#if holiday.holiday_date == getdate(self.permission_date):
						#frappe.throw(_("Exit permission can not be marked in holiday"))
			
			#if self.type== 'Exit': 
				#self.to_date = '0'
				#self.from_date = time.strftime("%X")
			#elif self.type== 'Return':
				#self.from_date = '0'
				#self.to_date = time.strftime("%X")

			per_type = frappe.db.sql("select type, from_date,name from `tabExit permission` where employee = %s and permission_date = %s and name != %s and permission_type='Exit with return' and docstatus<2 order by name desc limit 1",(self.employee, self.permission_date, self.name))

			if  per_type :

				if  per_type[0][0] !='Exit' and self.type == 'Return':
					frappe.throw(_("Not allowed! Can not return with no exit order"))
				if  per_type[0][0] !='Return' and self.type == 'Exit':
					frappe.throw(_("Not Allowed! You have an Exit permission"))

				diff_time = frappe.db.sql("select format(((TIME_TO_SEC('%s')-TIME_TO_SEC('%s'))/60),0)" %(str(self.to_date), str(per_type[0][1])))[0][0]
				if   diff_time <= '0' and self.type == 'Return':
					frappe.throw(_("Return time can not be before Exit time"))

				if per_type[0][0] =='Exit' and self.type == 'Return':
					fromdate = per_type[0][1]
					number= round(float(diff_time)/60,1)
					self.diff_exit= str(datetime.timedelta(seconds=number*3600))
					self.exit_order_name =per_type[0][2]
					self.from_date =per_type[0][1]

			else: 	
				if self.type == 'Return':
					frappe.throw(_("Not allowed! Can not return with no exit order"))

			### validate Attendance
			attendance = frappe.db.get_value("Attendance", {'employee':self.employee,'attendance_date':self.permission_date,'docstatus':("<", 2)}, "name")
			if self.is_new() and not attendance:
				frappe.throw(_("Not allowed! You have not an attendance for today"))

			### Exit after Departure
			is_manager=False
			for role in frappe.get_roles():
				if role == 'HR Manager':is_manager=True

			departure = frappe.db.get_value("Departure", {'employee':self.employee,'departure_date':self.permission_date,'docstatus':("<", 2)}, "name")
			if self.is_new() and departure and not is_manager:
				frappe.throw(_("Not allowed! Can not Exit after Departure"))
			
			### validate duplication
			if self.is_new() and self.permission_date and self.type == 'Exit':
				exit_per = frappe.db.get_value("Exit permission", {'employee':self.employee,'permission_type':'Exit with return','permission_date':self.permission_date,'type':'Exit','docstatus':("<", 2)}, "name")
				ret_per = frappe.db.get_value("Exit permission", {'employee':self.employee,'permission_type':'Exit with return','permission_date':self.permission_date,'type':'Return','docstatus':("<", 2)}, "name")
				#exit_per = frappe.db.sql("select type from `tabExit permission` where employee = %s and permission_date=%s and docstatus !=2 order by name desc LIMIT 1",(self.employee,self.permission_date))
				#ret_per = frappe.db.sql("select type from `tabExit permission` where employee = %s and permission_date=%s and docstatus !=2 order by name desc LIMIT 1",(self.employee,self.permission_date))
				if exit_per and not ret_per:
					frappe.throw(_("Not Allowed! You have an Exit permission"));
			
			#if self.type== 'Return' and (get_time(self.to_date) <= get_time(self.from_date)):
			#	frappe.throw(_("Exit permission return time can not be equal or less than exit time")

		self.docstatus= 1
		self.workflow_state='Final Approval'




		
			
	def sms_for_morning_delay(self):
		from frappe.core.doctype.sms_settings.sms_settings import send_sms
		sending_sms_for_morning_delay = frappe.db.get_value("HR Settings", None, "sending_sms_for_morning_delay")
		if sending_sms_for_morning_delay and sending_sms_for_morning_delay =='1':
            		mobile = frappe.db.get_value("HR Settings", None, "manager_phone_number")
			if mobile and mobile != '0':
				if len(mobile) <14: 
					frappe.msgprint(_("Mobile number is not valid"))
				else:
            				context = {"doc": self, "alert": self, "comments": None}
            			#if self.get("_comments"):
                		#	context["comments"] = json.loads(self.get("_comments"))

					messages = self.employee_name + _(" has a late attendance today. His attendance is at {0}, and the delay for about {1}").format(self.from_date,self.late_diff)
            				messages = frappe.render_template(messages, context)
            				number = [mobile]
            				send_sms(number,messages)
        		else:
            			frappe.msgprint(_("No mobile number to send SMS, PLZ check it from HR Settings"))
				



				

		
		
			
