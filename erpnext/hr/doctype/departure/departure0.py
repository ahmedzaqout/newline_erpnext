# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe import _, msgprint
from frappe.model.document import Document
from erpnext.hr.utils import set_employee_name
from frappe.utils import getdate, nowdate,get_time, time_diff,time_diff_in_seconds,cint,time_diff_in_hours,to_timedelta,get_datetime
import datetime, calendar, time
import datetime as dt
from erpnext.hr import is_overtime_exceeded

class Departure(Document):
	def validate(self):
		self.docstatus = 1

		departure_clock_closing = frappe.db.get_value("HR Settings", None, "departure_clock_closing")
		if departure_clock_closing and get_time(self.departure_time) >= get_time(departure_clock_closing):
			frappe.throw(_("Not Allowed! Footprint Clock is closed, your departure should be before {0}".format(departure_clock_closing) ))

		self.validate_duplicate_record()
		self.validate_attendance_date()

			


	def validate_employee(self):
		emp = frappe.db.sql("select name from `tabEmployee` where name = %s and status = 'Active'",
		 	self.employee)
		if not emp:
			frappe.throw(_("Departure for employee {0} is already marked").format(self.employee))

	def validate_duplicate_record(self):
		res = frappe.db.sql("""select name from `tabDeparture` where employee = %s and departure_date = %s
			and name != %s and docstatus = 1""",
			(self.employee, self.departure_date, self.name))
		if res:
			frappe.throw(_("Departure is already marked"))

		set_employee_name(self)

	def validate_permissions(self):
		exit_perm_msg=" "
		total_ext_diff=0.0
		exit_perm = frappe.db.sql("select e.employee,e.docstatus, e.permission_date, r.diff_exit as ext_diff,e.from_date,r.to_date from `tabExit permission` as e join `tabExit permission` as r on e.name = r.exit_order_name where e.employee=%s and e.permission_date=%s",(self.employee,self.departure_date),as_dict=1)
		if exit_perm:
			for e_per in exit_perm:
				exit_perm_msg+= " "+_("from {0} to {1},").format(e_per.from_date, e_per.to_date)
				total= get_datetime(e_per.ext_diff)

				#result = int(h) * 3600 + int(m) * 60 + int(s)
				total= total.hour+ total.minute/60 + total.second/3600
				total_ext_diff+= total or 0.0

		if exit_perm_msg != " ": self.exit_per = _("You have an exit permission for about {0} hour(s)").format(str(datetime.timedelta(seconds=round(total_ext_diff,1)*60))) +" "+ exit_perm_msg
		return total_ext_diff


	def validate_attendance_date(self):
		att_time = frappe.db.get_value("Attendance",{ "docstatus":("<",2),"employee": self.employee, "attendance_date":self.departure_date}, "attendance_time")
		if not att_time:
			frappe.throw(_("Attendance does not exist"))


		attendance_day = calendar.day_name[getdate(self.departure_date).weekday()];
		employee_work_shift = frappe.db.get_value("Employee Employment Detail", self.employee, "work_shift")
		employee_end_time = frappe.db.get_value("Work Shift Details", {"parent":employee_work_shift,"day":attendance_day}, "end_work")
		if not employee_end_time:
			frappe.throw(_("End Time Work Shift does not exist for that day"))
		#if get_time(self.departure_time) > get_time(employee_end_time):
		#	frappe.throw(_("Departure time can not be more than employee's end time shift"))
		
		if self.departure_time:
			exit_per = frappe.db.get_value("Exit permission", {'employee':self.employee,'permission_type':'Exit with return','permission_date':self.departure_date,'type':'Exit','docstatus':("<", 2)}, "name")
			ret_per = frappe.db.get_value("Exit permission", {'employee':self.employee,'permission_type':'Exit with return','permission_date':self.departure_date,'type':'Return','docstatus':("<", 2)}, ["name","to_date"])

			if exit_per and not ret_per:
				frappe.throw(_("Not Allowed! You have an Exit permission with no return"));

			if ret_per:
				if get_time(self.departure_time) <=  get_time(ret_per[1]):
					frappe.throw(_("Departure time can not be less than return time permission"));
				


		day = calendar.day_name[getdate(self.departure_date).weekday()];
		employee_work_shift = frappe.db.get_value("Employee Employment Detail", self.employee, "work_shift")

		employee_start_time = frappe.db.get_value("Work Shift Details", {"parent":employee_work_shift,"day":day}, "start_work")
		employee_end_time = frappe.db.get_value("Work Shift Details", {"parent":employee_work_shift,"day":day}, "end_work")
		#shift_diff = str(time_diff_in_hours(employee_end_time,employee_start_time))
		if not employee_start_time:
			frappe.throw(_("Start Time Work Shift does not exist for that day"))
	

		att_from_time= frappe.db.sql('select TIMESTAMP(%s , %s)',(self.departure_date, employee_end_time))[0][0]
		to_time= frappe.db.sql('select TIMESTAMP(%s , %s)',(self.departure_date, self.departure_time))[0][0]
		from_time= frappe.db.sql('select TIMESTAMP(%s , %s)',(self.departure_date, att_time))[0][0]
		
		#### In Holiday >>overtime ###
		holiday_list = frappe.db.get_value("Employee Employment Detail", self.employee, "holiday_list")
		att_over = frappe.db.get_value("Timesheet",{ "employee":self.employee, "start_date":self.departure_date,"docstatus":("<",2)}, "name")
		over_diff = str(time_diff_in_hours(to_time,from_time))
		is_holiday= False
		if holiday_list:
			holidays = frappe.get_all("Holiday", fields=["holiday_date"],filters={'parent':holiday_list})
			for holiday in holidays:
				if holiday.holiday_date == getdate(self.departure_date):
					is_holiday= True

			overtime_max_minutes = frappe.db.get_value("HR Settings", None, "overtime_max_minutes")	
			if not overtime_max_minutes:
				frappe.throw(_("Enter the value of max overtime in HR settings"))

			#if is_overtime_exceeded(self.employee, self.departure_date):		
			#	frappe.throw(_("Overtime is exceeded!"))
			
			total_att = time_diff(str(self.departure_time),str(att_time) )
			shift_att = time_diff(str(employee_end_time),str(employee_start_time) )
			diff = time_diff_in_hours(str(total_att),str(shift_att))
			
			if is_holiday and total_att > shift_att and diff > float(overtime_max_minutes) :
				dep_time= att_time + shift_att	
				dep_timedate= frappe.db.sql('select TIMESTAMP(%s , %s)',(self.departure_date, dep_time))[0][0]
				#dep_timedate= dt.datetime.combine(getdate(self.departure_date), dt.datetime.strptime(str(dep_time), '%H:%M:%S.%f').time())	


				dep_timedate= frappe.db.sql('select TIMESTAMP(%s , %s)',(self.departure_date, dep_time))[0][0]
				hol_overtime = frappe.new_doc('Timesheet')
				if hol_overtime and att_over:
					over_det = frappe.get_doc('Timesheet',att_over)
					time_det = frappe.get_doc('Timesheet Detail',{'parent':over_det.name,'activity_type':_('Auto Entry: Overtime Attendance')})
					
					time_det.update({
						'from_time':dep_timedate,
						'to_time':to_time,
						'hours':diff
					})
					time_det.flags.ignore_validate = True
					time_det.flags.ignore_validate_update_after_submit = True 
					time_det.save(ignore_permissions=True)
					
					from erpnext.hr.doctype.employee_edit_time.employee_edit_time import update_overtime_total_hrs
					update_overtime_total_hrs(over_det)

					#over_det.append('time_logs',{
					#	'activity_type':_('Auto Entry: Overtime Attendance'),
					#	'from_time':dep_timedate,
					#	'to_time': to_time,
					#	'hours': diff
					#	})
					#over_det.flags.ignore_validate = True
					#over_det.flags.ignore_validate_update_after_submit = True 
					#over_det.save(ignore_permissions=True)

				else:
					hol_overtime = frappe.new_doc('Timesheet')
					hol_overtime.update({
						'name':self.employee,
						'employee':self.employee,
						'start_date': getdate(self.departure_date),
						'to_date': getdate(self.departure_date),
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
					hol_overtime.insert(ignore_permissions=True)

			else:
				#frappe.msgprint(str(to_time))
				self.add_overtime(att_time,att_over,to_time,att_from_time,employee_start_time,employee_end_time)


	    ########Early Departure

		early_departure_in_minutes = frappe.db.get_value("HR Settings", None, "early_departure_in_minutes")
		if not early_departure_in_minutes:
			frappe.throw(_("Add a value for Early Departure In Minutes in HR Settings"))
		
			
		if self.is_new() and employee_end_time and self.departure_time and self.docstatus<2 and not is_holiday:
			#if get_time(self.departure_time) < get_time(employee_end_time):
				#diff_time = frappe.db.sql("select format(((TIME_TO_SEC('%s')-TIME_TO_SEC('%s'))/60),0)" %(str(employee_end_time), str(self.departure_time)))
			total_att = time_diff(str(self.departure_time),str(att_time) )
			shift_att = time_diff(str(employee_end_time),str(employee_start_time) )
			diff = time_diff_in_hours(str(shift_att),str(total_att))*60
			#frappe.msgprint(str(employee_end_time)+" n "+str(employee_start_time))
			#frappe.msgprint(str(total_att)+" c "+str(shift_att)+" x "+str(diff)+" n "+str(early_departure_in_minutes))

			if total_att < shift_att:
				if float(diff) > float(early_departure_in_minutes):
					doc = frappe.new_doc('Exit permission')
					doc.update({
						'employee':self.employee,
						'permission_date': getdate(self.departure_date),
						'from_date': get_time(att_time),
						'to_date': get_time(self.departure_time),
						'reason': _("System Auto Entry: Early Departure"),
						'permission_type': "Early Departure",
						'early_diff':round(diff,2),
						'docstatus': 0,
						'workflow_state':'Pending Request'
					})
					doc.insert(ignore_permissions=True)





	def add_overtime(self,att_time,att_over,to_time,att_from_time,employee_start_time,employee_end_time):

		overtime_max_minutes = frappe.db.get_value("HR Settings", None, "overtime_max_minutes")	
		if not overtime_max_minutes:
			frappe.throw(_("Enter the value of max overtime in HR settings"))

		#if is_overtime_exceeded(self.employee, self.departure_date):		
		#	frappe.throw(_("Overtime is exceeded!"))

		total_att = time_diff(str(self.departure_time),str(att_time) )
		shift_att = time_diff(str(employee_end_time),str(employee_start_time) )
		diff = time_diff_in_hours(str(total_att),str(shift_att))

		dep_time= att_time + shift_att	
		dep_timedate= frappe.db.sql('select TIMESTAMP(%s , %s)',(self.departure_date, dep_time))[0][0]
		#dep_timedate= dt.datetime.combine(getdate(self.departure_date), dt.datetime.strptime(str(dep_time), '%H:%M:%S.%f').time())		
		total_exit= self.validate_permissions()
		#frappe.msgprint("bb "+str(total_exit))
		discount_permissions_from_attendance_hours = frappe.db.get_value("HR Settings", None, "discount_permissions_from_attendance_hours")
		if discount_permissions_from_attendance_hours and total_exit!=0.0:
			if diff > total_exit:
				diff = diff- total_exit
			else:
				diff = total_exit- diff
		#### attendance > shift time ####


		if att_time:
			#diff_time=str(time_diff_in_hours(self.departure_time,att_time))
			#diff_time = frappe.db.sql("select format(((TIME_TO_SEC('%s')-TIME_TO_SEC('%s'))/60),0)" %(str(self.departure_time), str(att_from_time)))[0][0]
			#shift_diff1 = frappe.db.sql("select format(((TIME_TO_SEC('%s')-TIME_TO_SEC('%s'))/60),0)" %(str(employee_end_time), str(employee_start_time)))[0][0]

			#frappe.msgprint(str(rem_dt))
			#frappe.msgprint(str(get_time(self.departure_time)+to_timedelta(diff_dep_shift)))
			#if shift_diff1 and float(diff_time) > 0:
			if total_att > shift_att and diff*60 > float(overtime_max_minutes):
				overtime = frappe.new_doc('Timesheet')
				
				if overtime and att_over:
					over_det = frappe.get_doc('Timesheet',att_over)
					time_det = frappe.get_doc('Timesheet Detail',{'parent':over_det.name,'activity_type':_('Auto Entry: Overtime Attendance')})
					time_det.update({
						'from_time':dep_timedate.replace(microsecond=0),
						'to_time':to_time,
						'hours':diff
					})
					time_det.flags.ignore_validate = True
					time_det.flags.ignore_validate_update_after_submit = True 
					time_det.save(ignore_permissions=True)
					#frappe.msgprint("mm "+str(diff))
					from erpnext.hr.doctype.employee_edit_time.employee_edit_time import update_overtime_total_hrs
					update_overtime_total_hrs(over_det)
		
				else:
					#frappe.msgprint("nn "+str(diff))
					overtime.update({
						'name':self.employee,
						'employee':self.employee,
						'start_date': getdate(self.departure_date),
						'to_date': getdate(self.departure_date),
						'time_logs': [{
							'activity_type':_('Auto Entry: Overtime Attendance'),
							'from_time':dep_timedate.replace(microsecond=0),
							'to_time': to_time,
							'hours': diff
								}],
						'type':'compensatory',
						'docstatus': 0,
						'workflow_state':'Pending Request'
						})
					overtime.insert(ignore_permissions=True)
		return "done"




	

		

