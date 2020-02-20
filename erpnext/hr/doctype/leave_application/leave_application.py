# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, cstr, date_diff, flt, formatdate, getdate, get_link_to_form, \
	comma_or, get_fullname, add_days,add_years
from erpnext.hr.utils import set_employee_name
from erpnext.hr.doctype.leave_block_list.leave_block_list import get_applicable_block_dates
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.hr.doctype.employee_leave_approver.employee_leave_approver import get_approver_list
import datetime, calendar, time
from calendar import monthrange

class LeaveDayBlockedError(frappe.ValidationError): pass
class OverlapError(frappe.ValidationError): pass
class InvalidLeaveApproverError(frappe.ValidationError): pass
class LeaveApproverIdentityError(frappe.ValidationError): pass
class AttendanceAlreadyMarkedError(frappe.ValidationError): pass

from frappe.model.document import Document
class LeaveApplication(Document):
	def get_feed(self):
		return _("{0}: From {0} of type {1}").format(self.status, self.employee_name, self.leave_type)

	def validate(self):
		if not getattr(self, "__islocal", None) and frappe.db.exists(self.doctype, self.name):
			self.previous_doc = frappe.get_value(self.doctype, self.name, "leave_approver", as_dict=True)
		else:
			self.previous_doc = None

		set_employee_name(self)

		self.validate_dates()
		self.validate_balance_leaves()
		self.validate_leave_overlap()
		self.validate_max_days()
		self.show_block_day_warning()
		self.validate_block_days()
		self.validate_salary_processed_days()
		self.validate_leave_approver()
		self.validate_attendance()

	def on_update(self):
		if self.workflow_state  and ( "reject" in self.workflow_state or "Rejection" in self.workflow_state) :
			frappe.db.sql("update `tabLeave Application` set docstatus=2 where name=%s",self.name)

		#if (not self.previous_doc and self.leave_approver) or (self.previous_doc and \
		#		self.status == "Open" and self.previous_doc.leave_approver != self.leave_approver):
			# notify leave approver about creation
		#	self.notify_leave_approver()

	def on_submit(self):
		if self.workflow_state  and("reject" in self.workflow_state or "Rejection" in self.workflow_state) :
			frappe.db.sql("""update `tabLeave Application` set docstatus=2 ,status = 'Rejected' where name=%s""",self.name)

		else: 
			self.status == "Approved"
			attendance_day = calendar.day_name[getdate(self.from_date).weekday()];
			employee_work_shift = frappe.db.get_value("Employee Employment Detail", self.employee, "work_shift")
			if employee_work_shift:
				employee_start_time = frappe.db.get_value("Work Shift Details", {"parent":employee_work_shift,"day":attendance_day}, "start_work")
				employee_end_time = frappe.db.get_value("Work Shift Details", {"parent":employee_work_shift,"day":attendance_day}, "end_work")

				holiday_list = get_holiday_list_for_employee(self.employee)
				holiday_filter = [["holiday_date", ">=", self.from_date], ["holiday_date", "<=", self.to_date]]
				holiday_filter.append(["parent", "=", holiday_list])
				holidays = frappe.get_all("Holiday", fields=["holiday_date"], filters=holiday_filter)
				holidays = [str(datetime.datetime.strptime(str(h.holiday_date),'%Y-%m-%d')) for h in holidays]

				if self.total_leave_days: tot_leavs= self.total_leave_days
				else: tot_leavs= date_diff(self.to_date, self.from_date) + 1

				for leave in range(int(tot_leavs)):
					leave_date = datetime.datetime.combine(datetime.datetime.strptime(str(add_days( self.from_date , days=leave)),'%Y-%m-%d')
	, datetime.datetime.min.time())

					if str(leave_date) not in holidays:
						self.update_att(leave_date, employee_start_time,employee_end_time,self.discount_salary_from_leaves)
			

		#########################################

		self.validate_back_dated_application()

		# notify leave applier about approval
		self.notify_employee(self.status)
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
			message = """ قام {0} برفض طلب الاجازة""".format(sender)
		else:
			message = """ قام {0} بالموافقة على طلب الاجازة""".format(sender)
		

		frappe.get_doc({"Doctype":"Notification",
				"tilte" : "{0} طلب الاجازة".format(_(self.workflow_state)),
				"message" : message,
				"reciver" : reciver_name,
				"seen" : 0,
				"doctype":"Notification",
				"doctype_type" : "Leave Application",
				"doctype_name" : self.name
				}).insert(ignore_permissions=True)

		#self.notify_leave_approver(self.status)

	def after_insert(self):
		sender = frappe.get_all("User",['name'],filters={"employee":self.employee})
		recivers = frappe.db.sql("SELECT DISTINCT u.name  FROM tabUser u join`tabHas Role` hr on u.name=hr.parent  WHERE role in (%s,%s)", ("HR User","HR Manager"))
		
		for rec in recivers:
			frappe.get_doc({"Doctype":"Notification",
					"tilte" : "طلب إجازة جديد",
					"message" : "قام الموظف {0} بإنشاء طلب إجازة ".format(self.employee),
					"reciver" : rec[0],
					"seen" : 0,
					"doctype":"Notification",
					"doctype_type" : "Leave Application",
					"doctype_name" : self.name
					}).insert(ignore_permissions=True)

	def update_att(self,leave_date, employee_start_time, employee_end_time,discount_salary_from_leaves=0):
		attendance = frappe.db.get_value("Attendance", {"employee":self.employee,"attendance_date":getdate(leave_date),"docstatus":("<", 2),"status":("!=", "On Leave"),"discount_salary_from_leaves":0}, "name")
		departure = frappe.db.get_value("Departure", {"employee":self.employee,"departure_date":getdate(leave_date),"docstatus":("<", 2),"status":("!=", "On Leave")}, "name")
			
		if attendance and discount_salary_from_leaves==0:
			frappe.db.sql("update `tabAttendance` set docstatus=2 where name=%s",attendance)
		if departure and discount_salary_from_leaves==0:
			frappe.db.sql("update  tabDeparture set docstatus=2 where name=%s",departure)

		att = frappe.new_doc('Attendance')
		att.update({
			'employee':self.employee,
			'employee_name':self.employee_name,
			'attendance_time':employee_start_time,
			'attendance_date':leave_date,
			'status':'On Leave',
			'docstatus':1,
			'discount_salary_from_leaves':discount_salary_from_leaves
				})
		if discount_salary_from_leaves: att.flags.ignore_validate = True
		att.flags.ignore_validate = True
		att.insert(ignore_permissions=True)
		dep = frappe.new_doc('Departure')
		dep.update({
			'employee':self.employee,
			'employee_name':self.employee_name,
			'departure_time':employee_end_time,
			'departure_date':leave_date,
			'status':'On Leave',
			'docstatus':1
				})
		if discount_salary_from_leaves: dep.flags.ignore_validate = True
		dep.flags.ignore_validate = True
		dep.insert(ignore_permissions=True)

	def on_cancel(self):
		# notify leave applier about cancellation
		self.notify_employee("cancelled")

	def validate_dates(self):
		if self.from_date and self.to_date and (getdate(self.to_date) < getdate(self.from_date)):
			frappe.throw(_("To date cannot be before from date"))

		if self.half_day and self.half_day_date \
			and (getdate(self.half_day_date) < getdate(self.from_date)
			or getdate(self.half_day_date) > getdate(self.to_date)):

				frappe.throw(_("Half Day Date should be between From Date and To Date"))

		if not is_lwp(self.leave_type):
			self.validate_dates_acorss_allocation()
			self.validate_back_dated_application()

	def validate_dates_acorss_allocation(self):
		def _get_leave_alloction_record(date):
			allocation = frappe.db.sql("""select name from `tabLeave Allocation`
				where employee=%s and leave_type=%s and docstatus=1
				and %s between from_date and to_date""", (self.employee, self.leave_type, date))

			return allocation and allocation[0][0]

		allocation_based_on_from_date = _get_leave_alloction_record(self.from_date)
		allocation_based_on_to_date = _get_leave_alloction_record(self.to_date)

		if not (allocation_based_on_from_date or allocation_based_on_to_date):
			#frappe.throw(_("Application period cannot be outside leave allocation period"))
			frappe.throw(_("Does not have Leaves! Application period cannot be outside leave allocation period"))

		elif allocation_based_on_from_date != allocation_based_on_to_date:
			frappe.throw(_("Application period cannot be across two alocation records"))

	def validate_back_dated_application(self):
		future_allocation = frappe.db.sql("""select name, from_date from `tabLeave Allocation`
			where employee=%s and leave_type=%s and docstatus=1 and from_date > %s
			and carry_forward=1""", (self.employee, self.leave_type, self.to_date), as_dict=1)

		if future_allocation:
			frappe.throw(_("Leave cannot be applied/cancelled before {0}, as leave balance has already been carry-forwarded in the future leave allocation record {1}")
				.format(formatdate(future_allocation[0].from_date), future_allocation[0].name))

	def validate_salary_processed_days(self):
		if not frappe.db.get_value("Leave Type", self.leave_type, "is_lwp"):
			return

		last_processed_pay_slip = frappe.db.sql("""
			select start_date, end_date from `tabSalary Slip`
			where docstatus = 1 and employee = %s
			and ((%s between start_date and end_date) or (%s between start_date and end_date))
			order by modified desc limit 1
		""",(self.employee, self.to_date, self.from_date))

		if last_processed_pay_slip:
			frappe.throw(_("Salary already processed for period between {0} and {1}, Leave application period cannot be between this date range.").format(formatdate(last_processed_pay_slip[0][0]),
				formatdate(last_processed_pay_slip[0][1])))


	def show_block_day_warning(self):
		block_dates = get_applicable_block_dates(self.from_date, self.to_date,
			self.employee, self.company, all_lists=True)

		if block_dates:
			frappe.msgprint(_("Warning: Leave application contains following block dates") + ":")
			for d in block_dates:
				frappe.msgprint(formatdate(d.block_date) + ": " + d.reason)

	def validate_block_days(self):
		block_dates = get_applicable_block_dates(self.from_date, self.to_date,
			self.employee, self.company)

		if block_dates and self.docstatus == 1:
			frappe.throw(_("You are not authorized to approve leaves on Block Dates"), LeaveDayBlockedError)

	def validate_balance_leaves(self):
		if self.from_date and self.to_date:
			self.total_leave_days = get_number_of_leave_days(self.employee, self.leave_type,
				self.from_date, self.to_date, self.half_day, self.half_day_date)

			if self.total_leave_days == 0:
				frappe.throw(_("The day(s) on which you are applying for leave are holidays. You need not apply for leave."))

			if not is_lwp(self.leave_type):
				self.leave_balance,self.balance_hrs = get_leave_balance_on(self.employee, self.leave_type, self.from_date,
					consider_all_leaves_in_the_allocation_period=True)
				if self.status != "Rejected" and self.leave_balance < self.total_leave_days:
					if frappe.db.get_value("Leave Type", self.leave_type, "allow_negative"):
						frappe.msgprint(_("Note: There is not enough leave balance for Leave Type {0}")
							.format(self.leave_type))
					else:
						frappe.throw(_("There is not enough leave balance for Leave Type {0}")
							.format(self.leave_type))


	def validate_leave_overlap(self):
		if not self.name:
			# hack! if name is null, it could cause problems with !=
			self.name = "New Leave Application"

		for d in frappe.db.sql("""
			select
				name, leave_type, posting_date, from_date, to_date, total_leave_days, half_day_date
			from `tabLeave Application`
			where employee = %(employee)s and docstatus < 2 
			and to_date >= %(from_date)s and from_date <= %(to_date)s
			and name != %(name)s""", {
				"employee": self.employee,
				"from_date": self.from_date,
				"to_date": self.to_date,
				"name": self.name
			}, as_dict = 1):

			if cint(self.half_day)==1 and getdate(self.half_day_date) == getdate(d.half_day_date) and (
				flt(self.total_leave_days)==0.5
				or getdate(self.from_date) == getdate(d.to_date)
				or getdate(self.to_date) == getdate(d.from_date)):

				total_leaves_on_half_day = self.get_total_leaves_on_half_day()
				if total_leaves_on_half_day >= 1:
					self.throw_overlap_error(d)
			else:
				self.throw_overlap_error(d)

	def throw_overlap_error(self, d):
		msg = _("Employee {0} has already applied for {1} between {2} and {3}").format(self.employee,
			d['leave_type'], formatdate(d['from_date']), formatdate(d['to_date'])) \
			+ """ <br><b><a href="#Form/Leave Application/{0}">{0}</a></b>""".format(d["name"])
		frappe.throw(msg, OverlapError)

	def get_total_leaves_on_half_day(self):
		leave_count_on_half_day_date = frappe.db.sql("""select count(name) from `tabLeave Application`
			where employee = %(employee)s
			and docstatus < 2
			and half_day = 1
			and half_day_date = %(half_day_date)s
			and name != %(name)s""", {
				"employee": self.employee,
				"half_day_date": self.half_day_date,
				"name": self.name
			})[0][0]

		return leave_count_on_half_day_date * 0.5


	def validate_max_days(self):
		max_days = frappe.db.get_value("Leave Type", self.leave_type, "max_days_allowed")
		if max_days and self.total_leave_days > cint(max_days):
			frappe.throw(_("Leave of type {0} cannot be longer than {1}").format(self.leave_type, max_days))

	def validate_leave_approver(self):
		employee = frappe.get_doc("Employee", self.employee)
		leave_approvers = [l.leave_approver for l in employee.get("leave_approvers")]

		if len(leave_approvers) and self.leave_approver not in leave_approvers:
			frappe.throw(_("Leave approver must be one of {0}")
				.format(comma_or(leave_approvers)), InvalidLeaveApproverError)

		elif self.leave_approver and not frappe.db.sql("""select name from `tabHas Role`
			where parent=%s and role='Leave Approver'""", self.leave_approver):
			frappe.throw(_("{0} ({1}) must have role 'Leave Approver'")\
				.format(get_fullname(self.leave_approver), self.leave_approver), InvalidLeaveApproverError)

		elif self.docstatus==1 and len(leave_approvers) and self.leave_approver != frappe.session.user:
			frappe.throw(_("Only the selected Leave Approver can submit this Leave Application"),
				LeaveApproverIdentityError)

	def validate_attendance(self):
		attendance = frappe.db.sql("""select name from `tabAttendance` where employee = %s and (attendance_date between %s and %s)
					and status = "Present" and docstatus = 1""",
			(self.employee, self.from_date, self.to_date))
		if attendance:
			frappe.throw(_("Attendance for employee {0} is already marked for this day").format(self.employee),
				AttendanceAlreadyMarkedError)

	def notify_employee(self, status):
		employee = frappe.get_doc("Employee", self.employee)
		if not employee.user_id:
			return

		def _get_message(url=False):
			if url:
				name = get_link_to_form(self.doctype, self.name)
			else:
				name = self.name

			message = "Leave Application: {name}".format(name=name)+"<br>"
			message += "Leave Type: {leave_type}".format(leave_type=self.leave_type)+"<br>"
			message += "From Date: {from_date}".format(from_date=self.from_date)+"<br>"
			message += "To Date: {to_date}".format(to_date=self.to_date)+"<br>"
			message += "Status: {status}".format(status=_(status))
			return message

		self.notify({
			# for post in messages
			"message": _get_message(url=True),
			"message_to": employee.user_id,
			"subject": (_("Leave Application") + ": %s - %s") % (self.name, _(status))
		})

	def notify_leave_approver(self,status):
		employee = frappe.get_doc("Employee", self.employee)

		def _get_message(url=False):
			name = self.name
			employee_name = cstr(employee.employee_name)
			if url:
				name = get_link_to_form(self.doctype, self.name)
				employee_name = get_link_to_form("Employee", self.employee, label=employee_name)
			message = (_("Leave Application") + ": %s") % (name)+"<br>"
			message += (_("Employee") + ": %s") % (employee_name)+"<br>"
			message += (_("Leave Type") + ": %s") % (self.leave_type)+"<br>"
			message += (_("From Date") + ": %s") % (self.from_date)+"<br>"
			message += (_("To Date") + ": %s") % (self.to_date)
			message +=  (_("Status") + ": %s") %(_(status))
			return message
		users = frappe.get_all("User", fields=["name","email"],filters={'enabled':1})
		for usr in users:
			user = frappe.get_doc("User", usr.name)
			if "HR Manager" in [u.role for u in user.get("roles")] or "HR User" in [u.role for u in user.get("roles")]:
				if usr.user_id:
					self.notify({
						# for post in messages
						"message": _get_message(url=True),
						"message_to": usr.email,
						"subject": (_("Leave Application") + ": %s - %s") % (self.name, _(status))
					})



		

	def notify(self, args):
		args = frappe._dict(args)
		from frappe.desk.page.chat.chat import post
		post(**{"txt": args.message, "contact": args.message_to, "subject": args.subject,
			"notify": cint(self.follow_via_email)})


@frappe.whitelist()
def get_approvers(doctype, txt, searchfield, start, page_len, filters):
	if not filters.get("employee"):
		frappe.throw(_("Please select Employee Record first."))

	employee_user = frappe.get_value("Employee", filters.get("employee"), "user_id")

	approvers_list = frappe.db.sql("""select user.name, user.first_name, user.last_name from
		tabUser user, `tabEmployee Leave Approver` approver where
		approver.parent = %s
		and user.name like %s
		and approver.leave_approver=user.name""", (filters.get("employee"), "%" + txt + "%"))

	if not approvers_list:
		approvers_list = get_approver_list(employee_user)
	return approvers_list

@frappe.whitelist()
def get_number_of_leave_days(employee, leave_type, from_date, to_date, half_day = None, half_day_date = None):
	number_of_days = 0
	if half_day == 1:
		if from_date == to_date:
			number_of_days = 0.5
		else:
			number_of_days = date_diff(to_date, from_date) + .5
	else:
		number_of_days = date_diff(to_date, from_date) + 1

	if not frappe.db.get_value("Leave Type", leave_type, "include_holiday"):
		number_of_days = flt(number_of_days) - flt(get_holidays(employee, from_date, to_date))
	return number_of_days

@frappe.whitelist()
def get_leave_balance_on(employee, leave_type, date, allocation_records=None,
		consider_all_leaves_in_the_allocation_period=False,docname=None,company=None):
	if allocation_records == None:
		allocation_records = get_leave_allocation_records(date, employee).get(employee, frappe._dict())
	com = frappe.defaults.get_user_default("Company")
	remain,leave_hrs_balance = 0, 0.0
	if com == "Nawa" or frappe.session.user == "Administrator" :
		date2 = datetime.datetime.strptime(str(date), "%Y-%m-%d")
		if date2:
			pre_year_date = date2.replace(year=date2.year-1)
			allocation_records_last_year = get_leave_allocation_records(pre_year_date, employee).get(employee, frappe._dict())
			allocation_prev = allocation_records_last_year.get(leave_type, frappe._dict())
			leaves_taken_prev = get_approved_leaves_for_period(employee, leave_type, allocation_prev.from_date,  allocation_prev.to_date)
			remain = flt(allocation_prev.total_leaves_allocated) - flt(leaves_taken_prev) 
			if ( flt(allocation_prev.total_leaves_allocated) - flt(leaves_taken_prev)  >  0.5*(flt(allocation_prev.total_leaves_allocated))):
				remain = 0.5*(flt(allocation_prev.total_leaves_allocated))


	allocation = allocation_records.get(leave_type, frappe._dict())


	

	from erpnext.hr.doctype.salary_slip.salary_slip import get_working_total_hours
	from erpnext.hr import get_emp_work_shift
	total_hrs , disc_hours ,total_real_hrs, compensatory_total_hours, permission_total_hours = get_working_total_hours(employee,allocation.from_date, datetime.datetime.strptime(str(date), "%Y-%m-%d").date())

	if consider_all_leaves_in_the_allocation_period:
		date = allocation.to_date
	leaves_taken = get_approved_leaves_for_period(employee, leave_type, allocation.from_date, date)
		
	shift_hrs = get_emp_work_shift(employee,calendar.day_name[getdate(allocation.from_date).weekday()] )
	leave_days_balance = (flt(allocation.total_leaves_allocated) - flt(leaves_taken))+remain
	leaves_dayss=leave_days_balance
	leaves_hourss=0
	annual_ex_total_hours= 0.0
	sick_ex_total_hours= 0.0

	if com == "Nawa":
		disc_hours =disc_hours - permission_total_hours
		

		perm = frappe.db.sql("select employee,docstatus ,permission_date ,ifnull(diff_exit,0) as diff from `tabExit permission` where type='Return' and permission_type='Exit with return' and employee = %(employee)s and date(permission_date) BETWEEN %(start_date)s AND DATE_ADD(%(end_date)s,INTERVAL 1 day) and docstatus = 1 and exit_type = 'Special' ", {'employee': employee, 'start_date': allocation.from_date, 'end_date': date}, as_dict=1)
		if perm:
			for p in perm:
				exit_hrs = frappe.db.sql("select format(((TIME_TO_SEC('%s'))/3600),0)" %p.diff)[0][0]
				annual_ex_total_hours += float(exit_hrs)

		sickk = frappe.db.sql("select employee,docstatus ,permission_date ,ifnull(diff_exit,0) as diff from `tabExit permission` where type='Return' and permission_type='Exit with return' and employee = %(employee)s and date(permission_date) BETWEEN %(start_date)s AND DATE_ADD(%(end_date)s,INTERVAL 1 day) and docstatus = 1 and exit_type = 'Sick' ", {'employee': employee, 'start_date':allocation.from_date, 'end_date': date}, as_dict=1)
		if sickk:
			for p in sickk:
				exit_hrs = frappe.db.sql("select format(((TIME_TO_SEC('%s'))/3600),0)" %p.diff)[0][0]
				sick_ex_total_hours += float(exit_hrs)

		if leave_type == _('Annual Leave'):
			disc_hours =disc_hours + annual_ex_total_hours

		if leave_type == _('Sick Leave'):
			sick_ex_total_hours  = sick_ex_total_hours

	if shift_hrs: 
		leave_hrs_balance=  (leave_days_balance * shift_hrs) 
		if leave_type == _('Annual Leave'):
			leave_hrs_balance = (leave_days_balance * shift_hrs) - disc_hours
		if leave_type == _('Sick Leave'):
			leave_hrs_balance = (leave_days_balance * shift_hrs) - sick_ex_total_hours
		else:
			leave_hrs_balance = (leave_days_balance * shift_hrs) 

		leaves_dayss = int(leave_hrs_balance/shift_hrs)
		leaves_hourss = leave_hrs_balance % shift_hrs

	return leaves_dayss ,flt(leaves_hourss,2)



def get_leaves_for_period(employee, leave_type, from_date, to_date, status, docname=None):
	leave_applications = frappe.db.sql("""
		select name, employee, leave_type, from_date, to_date, total_leave_days
		from `tabLeave Application`
		where employee=%(employee)s and leave_type=%(leave_type)s
			and docstatus =1
			and (from_date between %(from_date)s and %(to_date)s
				or to_date between %(from_date)s and %(to_date)s
				or (from_date < %(from_date)s and to_date > %(to_date)s))
	""", {
		"from_date": from_date,
		"to_date": to_date,
		"employee": employee,
		#"status": status,
		"leave_type": leave_type
	}, as_dict=1)
	leave_days = 0
	for leave_app in leave_applications:
		if docname and leave_app.name == docname:
			continue
		if leave_app.from_date >= getdate(from_date) and leave_app.to_date <= getdate(to_date):
			leave_days += leave_app.total_leave_days
		else:
			if leave_app.from_date < getdate(from_date):
				leave_app.from_date = from_date
			if leave_app.to_date > getdate(to_date):
				leave_app.to_date = to_date

			leave_days += get_number_of_leave_days(employee, leave_type,
				leave_app.from_date, leave_app.to_date)

	return leave_days


def get_approved_leaves_for_period(employee, leave_type, from_date, to_date):
	leave_applications = frappe.db.sql("""
		select employee, leave_type, from_date, to_date, total_leave_days
		from `tabLeave Application`
		where employee=%(employee)s and leave_type=%(leave_type)s
			 and docstatus=1
			and (from_date between %(from_date)s and %(to_date)s
				or to_date between %(from_date)s and %(to_date)s
				or (from_date < %(from_date)s and to_date > %(to_date)s))
	""", {
		"from_date": from_date,
		"to_date": to_date,
		"employee": employee,
		"leave_type": leave_type
	}, as_dict=1)

	leave_days = 0
	for leave_app in leave_applications:
		if leave_app.from_date >= getdate(from_date) and leave_app.to_date <= getdate(to_date):
			leave_days += leave_app.total_leave_days
		else:
			if leave_app.from_date < getdate(from_date):
				leave_app.from_date = from_date
			if leave_app.to_date > getdate(to_date):
				leave_app.to_date = to_date

			leave_days += get_number_of_leave_days(employee, leave_type,
				leave_app.from_date, leave_app.to_date)

	return leave_days

def get_leave_allocation_records(date, employee=None):
	conditions = (" and employee='%s'" % employee) if employee else ""

	leave_allocation_records = frappe.db.sql("""
		select employee, leave_type, total_leaves_allocated, from_date, to_date
		from `tabLeave Allocation`
		where %s between from_date and to_date and docstatus=1 {0}""".format(conditions), (date), as_dict=1)


	allocated_leaves = frappe._dict()
	for d in leave_allocation_records:
		allocated_leaves.setdefault(d.employee, frappe._dict()).setdefault(d.leave_type, frappe._dict({
			"from_date": d.from_date,
			"to_date": d.to_date,
			"total_leaves_allocated": d.total_leaves_allocated
		}))

	return allocated_leaves


def get_holidays(employee, from_date, to_date):
	'''get holidays between two dates for the given employee'''
	holiday_list = get_holiday_list_for_employee(employee)

	holidays = frappe.db.sql("""select count(distinct holiday_date) from `tabHoliday` h1, `tabHoliday List` h2
		where h1.parent = h2.name and h1.holiday_date between %s and %s
		and h2.name = %s""", (from_date, to_date, holiday_list))[0][0]

	return holidays

def is_lwp(leave_type):
	lwp = frappe.db.sql("select is_lwp from `tabLeave Type` where name = %s", leave_type)
	return lwp and cint(lwp[0][0]) or 0

@frappe.whitelist()
def get_events(start, end, filters=None):
	events = []

	employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, ["name", "company"],
		as_dict=True)
	if employee:
		employee, company = employee.name, employee.company
	else:
		employee=''
		company=frappe.db.get_value("Global Defaults", None, "default_company")

	from frappe.desk.reportview import get_filters_cond
	conditions = get_filters_cond("Leave Application", filters, [])

	# show department leaves for employee
	if "Employee" in frappe.get_roles():
		add_department_leaves(events, start, end, employee, company)

	add_leaves(events, start, end, conditions)

	add_block_dates(events, start, end, employee, company)
	add_holidays(events, start, end, employee, company)

	return events

def add_department_leaves(events, start, end, employee, company):
	department = frappe.db.get_value("Employee", employee, "department")

	if not department:
		return

	# department leaves
	department_employees = frappe.db.sql_list("""select name from tabEmployee where department=%s
		and company=%s""", (department, company))

	match_conditions = "and employee in (\"%s\")" % '", "'.join(department_employees)
	add_leaves(events, start, end, match_conditions=match_conditions)

def add_leaves(events, start, end, match_conditions=None):
	query = """select name, from_date, to_date, employee_name, half_day,
		status, employee, docstatus
		from `tabLeave Application` where
		from_date <= %(end)s and to_date >= %(start)s <= to_date
		and docstatus < 2
		 """
	if match_conditions:
		query += match_conditions

	for d in frappe.db.sql(query, {"start":start, "end": end}, as_dict=True):
		e = {
			"name": d.name,
			"doctype": "Leave Application",
			"from_date": d.from_date,
			"to_date": d.to_date,
			"status": d.status,
			"title": cstr(d.employee_name) + \
				(d.half_day and _(" (Half Day)") or ""),
			"docstatus": d.docstatus
		}
		if e not in events:
			events.append(e)

def add_block_dates(events, start, end, employee, company):
	# block days
	from erpnext.hr.doctype.leave_block_list.leave_block_list import get_applicable_block_dates

	cnt = 0
	block_dates = get_applicable_block_dates(start, end, employee, company, all_lists=True)

	for block_date in block_dates:
		events.append({
			"doctype": "Leave Block List Date",
			"from_date": block_date.block_date,
			"to_date": block_date.block_date,
			"title": _("Leave Blocked") + ": " + block_date.reason,
			"name": "_" + str(cnt),
		})
		cnt+=1

def add_holidays(events, start, end, employee, company):
	applicable_holiday_list = get_holiday_list_for_employee(employee, company)
	if not applicable_holiday_list:
		return

	for holiday in frappe.db.sql("""select name, holiday_date, description
		from `tabHoliday` where parent=%s and holiday_date between %s and %s""",
		(applicable_holiday_list, start, end), as_dict=True):
			events.append({
				"doctype": "Holiday",
				"from_date": holiday.holiday_date,
				"to_date":  holiday.holiday_date,
				"title": _("Holiday") + ": " + cstr(holiday.description),
				"name": holiday.name
			})


