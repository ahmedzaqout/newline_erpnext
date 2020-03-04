# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, re

from frappe.utils import getdate, validate_email_add, today, add_years,nowdate
from frappe.model.naming import make_autoname, getseries
from frappe import throw, _, scrub
import frappe.permissions
from frappe.model.document import Document
from erpnext.utilities.transaction_base import delete_events
from frappe.utils.nestedset import NestedSet
import datetime, calendar, time

class EmployeeUserDisabledError(frappe.ValidationError):
	pass

class Employee(NestedSet):
	nsm_parent_field = 'reports_to'

	def autoname(self):
		naming_method = frappe.db.get_value("HR Settings", None, "emp_created_by")
		if frappe.db.get_value("HR Settings", None, "auto_generate_employee_no") == '1':
			self.name = self.employee_number
			#self.employee_number = self.name
			#self.employee = self.name

		elif not naming_method:
			naming_method == 'Employee Number'
		
		else:
			if naming_method == 'Naming Series':
				self.name = self.employee_number 
			elif naming_method == 'Employee Number':
				self.name = self.employee_number
			elif naming_method == 'Full Name':
				self.name = self.employee_name
		
			self.employee = self.name




	def validate(self):
		from erpnext.controllers.status_updater import validate_status
		validate_status(self.status, ["Active", "Left"])

		self.employee = self.name
		self.validate_date()
		self.validate_email()
		self.validate_status()
		self.validate_employee_leave_approver()
		self.validate_reports_to()
		self.validate_prefered_email()
                self.validate_phone_cell()
		self.clearance_leave_balances()
		self.validate_duplicate_personal_email()
		self.validate_duplicate_cell_number()

		if self.user_id:
			pass
			#self.validate_for_enabled_user_id()
			self.validate_duplicate_user_id()
		else:
			existing_user_id = frappe.db.get_value("Employee", self.name, "user_id")
			if existing_user_id:
				frappe.permissions.remove_user_permission(
					"Employee", self.name, existing_user_id)

	
######################################################### Edited By Maysaa ###########################################

	def validate_phone_cell(self):
		import re
		rule = re.compile(r'(^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,7}$)')
		ext_rule = re.compile(r'(^[0-9]{1,4}$)')
		if self.cell_number:
			if not rule.search(self.cell_number):
				throw(_("Invalid Cell Number"))
		if self.emergency_phone_number:
			if not rule.search(self.emergency_phone_number):
				throw(_("Invalid Emergency Phone Number"))
				
	
	def clearance_leave_balances(self):
		if self.employment_type ==_('In hours'):
			emp = frappe.get_doc("Leave Allocation", {"employee":self.name})
			if emp:
	    			employee = frappe.db.sql("""update `tabLeave Allocation` set total_leaves_allocated=0 where employee= '{employee}'""".format	(employee=self.name),  as_dict=1)


	def validate_duplicate_personal_email(self):
		employee = frappe.db.sql_list("""select name from `tabEmployee` where
			personal_email=%s and status='Active' and name!=%s""", (self.personal_email, self.name))
		if employee:
			throw(_("Personal Email {0} is already assigned to Employee {1}").format(
				self.personal_email, employee[0]), frappe.DuplicateEntryError)

	def validate_duplicate_cell_number(self):
		employee = frappe.db.sql_list("""select name from `tabEmployee` where
			cell_number=%s and status='Active' and name!=%s""", (self.cell_number, self.name))
		if employee:
			throw(_("Cell Number {0} is already assigned to Employee {1}").format(
				self.personal_email, employee[0]), frappe.DuplicateEntryError)


########################################

	def update_nsm_model(self):
		frappe.utils.nestedset.update_nsm(self)

	def on_update(self):
		self.validate_duplicate_emp_name()
		self.update_nsm_model()
		if self.user_id:
			pass
			#self.update_user()
			#self.update_user_permissions()

	def update_user_permissions(self):
		frappe.permissions.add_user_permission("Employee", self.name, self.user_id)
		frappe.permissions.set_user_permission_if_allowed("Company", self.company, self.user_id)

	def update_user(self):
		# add employee role if missing
		user = frappe.get_doc("User", self.user_id)
		user.flags.ignore_permissions = True

		if "Employee" not in user.get("roles"):
			user.add_roles("Employee")

		# copy details like Fullname, DOB and Image to User
		if self.employee_name and not (user.first_name and user.last_name):
			employee_name = self.employee_name.split(" ")
			if len(employee_name) >= 3:
				user.last_name = " ".join(employee_name[2:])
				user.middle_name = employee_name[1]
			elif len(employee_name) == 2:
				user.last_name = employee_name[1]

			user.first_name = employee_name[0]

		if self.date_of_birth:
			user.birth_date = self.date_of_birth

		if self.gender:
			user.gender = self.gender

		if self.image:
			if not user.user_image:
				user.user_image = self.image
				try:
					frappe.get_doc({
						"doctype": "File",
						"file_name": self.image,
						"attached_to_doctype": "User",
						"attached_to_name": self.user_id
					}).insert()
				except frappe.DuplicateEntryError:
					# already exists
					pass

		user.save()

	def validate_date(self):
		if self.date_of_birth and getdate(self.date_of_birth) > getdate(today()):
			throw(_("Date of Birth cannot be greater than today."))

		if self.date_of_birth and self.date_of_joining and getdate(self.date_of_birth) >= getdate(self.date_of_joining):
			throw(_("Date of Joining must be greater than Date of Birth"))

		elif self.date_of_retirement and self.date_of_joining and (getdate(self.date_of_retirement) <= getdate(self.date_of_joining)):
			throw(_("Date Of Retirement must be greater than Date of Joining"))

		elif self.relieving_date and self.date_of_joining and (getdate(self.relieving_date) <= getdate(self.date_of_joining)):
			throw(_("Relieving Date must be greater than Date of Joining"))

		elif self.contract_end_date and self.date_of_joining and (getdate(self.contract_end_date) <= getdate(self.date_of_joining)):
			throw(_("Contract End Date must be greater than Date of Joining"))

	def validate_email(self):
		if self.company_email:
			validate_email_add(self.company_email, True)
		if self.personal_email:
			validate_email_add(self.personal_email, True)

	def validate_status(self):
		if self.status == 'Left' and not self.relieving_date:
			throw(_("Please enter relieving date."))

	def validate_for_enabled_user_id(self):
		if not self.status == 'Active':
			return
		enabled = frappe.db.get_value("User", self.user_id, "enabled")
		if enabled is None:
			frappe.throw(_("User {0} does not exist").format(self.user_id))
		if enabled == 0:
			frappe.throw(_("User {0} is disabled").format(self.user_id), EmployeeUserDisabledError)

	def validate_duplicate_user_id(self):
		employee = frappe.db.sql_list("""select name from `tabEmployee` where
			user_id=%s and status='Active' and name!=%s""", (self.user_id, self.name))
		if employee:
			throw(_("User {0} is already assigned to Employee {1}").format(
				self.user_id, employee[0]), frappe.DuplicateEntryError)

	def validate_duplicate_emp_name(self):
		employee = frappe.db.sql_list("""select name from `tabEmployee` where
			employee_name=%s and status='Active' and name!=%s""", (self.employee_name, self.name))
		if employee:
			throw(_("User {0} is already assigned to Employee {1}").format(
				self.employee_name, employee[0]), frappe.DuplicateEntryError)

	def validate_employee_leave_approver(self):
		for l in self.get("leave_approvers")[:]:
			if "Leave Approver" not in frappe.get_roles(l.leave_approver):
				frappe.get_doc("User", l.leave_approver).add_roles("Leave Approver")

	def validate_reports_to(self):
		if self.reports_to == self.name:
			throw(_("Employee cannot report to himself."))

	def on_trash(self):
		self.update_nsm_model()
		delete_events(self.doctype, self.name)
		delete_events('Employee Personal Detail', self.name)
		delete_events('User', self.name)
		delete_events('Employee Employment Detail', self.name)
		delete_events('Employee Salary Detail', self.name)
		delete_events('Employee Data', self.name)
		delete_events('Employee Ending Service  Details', self.name)


	def validate_prefered_email(self):
		if self.prefered_contact_email and not self.get(scrub(self.prefered_contact_email)):
			frappe.msgprint(_("Please enter " + self.prefered_contact_email))

	def auto_generate_emp(self, employee=None):
		def generate_hash_num(num):
			hash_mask= '.'
			count = 0
			while(num>0):
				num= num/10
				count+=1
	
			max_num = (10**count) -1
			for i in range(count):
				hash_mask+='#'	
			return hash_mask, max_num		
		

		if frappe.db.get_value("HR Settings", None, "number_of_company_members"):
			memebers_num = frappe.db.get_value("HR Settings", None, "number_of_company_members")
			company_memebers, max_num = generate_hash_num(int(memebers_num))
		else: company_memebers = '.####'

		#if frappe.db.get_value("HR Settings", None, "auto_generate_employee_no") == '0'and employee:
		#	return make_autoname(employee)
		mask= 'EMP-'
		if frappe.db.get_value("HR Settings", None, "auto_generate_employee_no") == '1':
			mask = frappe.db.get_value("HR Settings", None, "employee_mask") 
			start_value = frappe.db.get_value("HR Settings", None, "employee_number_mask") 
			if mask and start_value:
				emp_number= mask+ company_memebers
				current = frappe.db.sql("select `current`,name from `tabSeries` where name=%s ", (mask ) ,as_dict=1)
				from erpnext.hr import employee_numbers
				employee_numbers = employee_numbers()
				if current and current[0].name >0:
					if (int(current[0].current) > int(max_num)):# or (int(current[0].current) > int(employee_numbers)):
						frappe.throw(_("Employees cannot exceed company members! PLZ got to setting ")+ """ <br><b><a href="#Form/HR Settings/">HR Settings</a></b>""")

				#part = getseries(mask, number_mask, 'Employee')
				#for emp_num in frappe.get_all("Employee", fields=["employee_number"],order_by='employee_number desc',limit=1):
				#	if mask  in emp_num.employee_number:
				#		empnum= emp_num.employee_number.split(str(mask ))
				#		last_empnum= int(''.join(empnum))
				#		#if current != last_empnum:
				#		frappe.db.sql("update tabSeries set current = %s where name=%s", (last_empnum, (mask + start_value) ))

				return make_autoname(emp_number,start_value=start_value)
		else:
			return make_autoname(mask + '.#####')




@frappe.whitelist()
def make_employee_docs(employee_number):
	emp_per= frappe.new_doc("Employee Personal Detail")
	emp_per.employee = employee_number
	emp_per.employee_number = employee_number
	emp_per.flags.ignore_validate = True
	emp_per.flags.ignore_mandatory = True
	emp_per.save(ignore_permissions=True)

	emp_user= frappe.new_doc("User")
	emp_user.employee = employee_number
	#emp_user.email = "emp"+str(self.employee_number)+"@test.ps"
	emp_user.flags.ignore_validate = True
	emp_user.flags.ignore_links = True
	emp_user.flags.ignore_mandatory = True
	emp_user.save(ignore_permissions=True)

	emp_det= frappe.new_doc("Employee Employment Detail")
	emp_det.employee = employee_number
	if frappe.db.get_value('Employment Type', _('Trial'),'name') and  frappe.db.get_default("company") == 'Nawa':
		emp_det.employment_type = _('Trial')
		emp_type = frappe.get_doc('Employment Type')
		emp_type.duration = 3
		emp_type.save(ignore_permissions=True)
	emp_det.flags.ignore_validate = True
	emp_det.flags.ignore_mandatory = True
	emp_det.save(ignore_permissions=True)

	emp_sal= frappe.new_doc("Employee Salary Detail")
	emp_sal.employee = employee_number
	emp_sal.flags.ignore_validate = True
	emp_sal.flags.ignore_mandatory = True
	emp_sal.save(ignore_permissions=True)

	emp_data= frappe.new_doc("Employee Data")
	emp_data.employee = employee_number
	emp_data.flags.ignore_validate = True
	emp_data.flags.ignore_mandatory = True
	emp_data.save(ignore_permissions=True)

	emp_end= frappe.new_doc("Employee Ending Service  Details")
	emp_end.employee = employee_number
	emp_end.flags.ignore_validate = True
	emp_end.flags.ignore_mandatory = True
	emp_end.save(ignore_permissions=True)


def get_timeline_data(doctype, name):
	'''Return timeline for attendance'''
	return dict(frappe.db.sql('''select unix_timestamp(attendance_date), count(*)
		from `tabAttendance` where employee=%s
			and attendance_date > date_sub(curdate(), interval 1 year)
			and status in ('Present', 'Half Day')
			group by attendance_date''', name))

@frappe.whitelist()
def get_retirement_date(date_of_birth=None):
	ret = {}
	if date_of_birth:
		try:
			retirement_age = int(frappe.db.get_single_value("HR Settings", "retirement_age") or 60)
			dt = add_years(getdate(date_of_birth),retirement_age)
			ret = {'date_of_retirement': dt.strftime('%Y-%m-%d')}
		except ValueError:
			# invalid date
			ret = {}

	return ret

def validate_employee_role(doc, method):
	# called via User hook
	if "Employee" in [d.role for d in doc.get("roles")]:
		if not frappe.db.get_value("Employee Personal Detail", {"user_id": doc.name}):
			pass #frappe.msgprint(_("Please set User ID field in an Employee record to set Employee Role"))
			#doc.get("roles").remove(doc.get("roles", {"role": "Employee"})[0])

def update_user_permissions(doc, method):
	# called via User hook
	if "Employee" in [d.role for d in doc.get("roles")]:
		if frappe.db.get_value("Employee Personal Detail", {"user_id": doc.email}):
			employee = frappe.get_doc("Employee Personal Detail", {"user_id": doc.email})
			employee.update_user_permissions()

def send_birthday_reminders():
	"""Send Employee birthday reminders if no 'Stop Birthday Reminders' is not set."""
	if int(frappe.db.get_single_value("HR Settings", "stop_birthday_reminders") or 0):
		return

	from frappe.utils.user import get_enabled_system_users
	users = None

	birthdays = get_employees_who_are_born_today()

	if birthdays:
		if not users:
			users = [u.email_id or u.name for u in get_enabled_system_users()]

		for e in birthdays:
			frappe.sendmail(recipients=filter(lambda u: u not in (e.company_email, e.personal_email, e.user_id), users),
				subject=_("Birthday Reminder for {0}").format(e.employee_name),
				message=_("""Today is {0}'s birthday!""").format(e.employee_name),
				reply_to=e.company_email or e.personal_email or e.user_id)

def get_employees_who_are_born_today():
	"""Get Employee properties whose birthday is today."""
	return frappe.db.sql("""select name, personal_email, company_email, user_id, employee_name
		from tabEmployee where day(date_of_birth) = day(%(date)s)
		and month(date_of_birth) = month(%(date)s)
		and status = 'Active'""", {"date": today()}, as_dict=True)

def get_holiday_list_for_employee(employee, raise_exception=True):
	if employee and frappe.db.get_value("Employee Employment Detail", employee, ["holiday_list", "company"]):
		holiday_list, company = frappe.db.get_value("Employee Employment Detail", employee, ["holiday_list", "company"])
	else:
		holiday_list=''
		company=frappe.db.get_value("Global Defaults", None, "default_company")

	#if not holiday_list:
	#	holiday_list = frappe.db.get_value("Company", company, "default_holiday_list")

	#if not holiday_list and raise_exception:
	#	frappe.throw(_('Please set a default Holiday List for Employee {0} or Company {1}').format(employee, company))

	return holiday_list

def is_holiday(employee, date=None):
	'''Returns True if given Employee has an holiday on the given date
	:param employee: Employee `name`
	:param date: Date to check. Will check for today if None'''

	holiday_list = get_holiday_list_for_employee(employee)
	if not date:
		date = today()

	if holiday_list:
		return frappe.get_all('Holiday List', dict(name=holiday_list, holiday_date=date)) and True or False

@frappe.whitelist()
def deactivate_sales_person(status = None, employee = None):
	if status == "Left":
		sales_person = frappe.db.get_value("Sales Person", {"Employee": employee})
		if sales_person:
			frappe.db.set_value("Sales Person", sales_person, "enabled", 0)

@frappe.whitelist()
def create_user(employee, user):
	first_name = last_name = ''
	if frappe.db.get_value('Employee Personal Detail', {'name':employee}, 'name'):
		emp = frappe.get_doc("Employee Personal Detail", employee)

		employee_name = emp.employee_name.split(" ")
		middle_name = last_name = ""

		if len(employee_name) >= 3:
			last_name = " ".join(employee_name[2:])
			middle_name = employee_name[1]
		elif len(employee_name) == 2:
			last_name = employee_name[1]

		first_name = employee_name[0]

	user = frappe.new_doc("User")
	user.update({
		"name": user,
		"email": user,
		"enabled": 1,
		"first_name": first_name,
		#"middle_name": middle_name,
		"last_name": last_name
		#"gender": emp.gender,
		#"birth_date": emp.date_of_birth,
		#"phone": emp.cell_number,
		#"bio": emp.bio
	})
	user.insert()
	return user.name

def get_employee_emails(employee_list):
	'''Returns list of employee emails either based on user_id or company_email'''
	employee_emails = []
	for employee in employee_list:
		if not employee:
			continue
		user, email = frappe.db.get_value('Employee', employee, ['user_id', 'company_email'])
		if user or email:
			employee_emails.append(user or email)

	return employee_emails

@frappe.whitelist()
def get_children(doctype, parent=None, company=None, is_root=False, is_tree=False):
	condition = ''

	if is_root:
		parent = ""
	if parent and company and parent!=company:
		condition = ' and reports_to = "{0}"'.format(frappe.db.escape(parent))
	else:
		condition = ' and ifnull(reports_to, "")=""'

	employee = frappe.db.sql("""
		select
			name as value, employee_name as title,
			exists(select name from `tabEmployee` where reports_to=emp.name) as expandable
		from
			`tabEmployee` emp
		where company='{company}' {condition} order by name"""
		.format(company=company, condition=condition),  as_dict=1)

	# return employee
	return employee


##############
@frappe.whitelist()
def validate_only_arabic(ar_field):
	rule = re.compile(ur'(^[ء-ي  -]+$)')
	myFields = {ar_field}
	for fi in myFields:
		if fi:
			if not rule.search(fi):
				throw(_("Bad Entry in Arabic name <br> {0}").format(fi))

@frappe.whitelist()
def validate_only_english(en_field):
	rule = re.compile(ur'(^[A-Za-z \- -dat]+$)')
	myFields = {"en_field" : en_field}
	for key,value in myFields.items():
		if value:
			if not rule.search(value):
				throw(_("Bad Entry in English name<br> {0}").format(value))





				
	

@frappe.whitelist(allow_guest=True)
def update_shifts():
	from erpnext.assets.doctype.asset_repair.asset_repair import get_downtime
	employees = frappe.get_all("Employee", fields=["name","work_shift","employee_name"],filters={'status':'Active'})
	day = calendar.day_name[getdate(nowdate()).weekday()];
	for emp_name in employees:		
		work_shift = frappe.db.get_value("Employee Employment Detail", emp_name, "work_shift")
		pr_work_shift = frappe.db.get_value("Employee Employment Detail", emp_name, "private_work_shift")
		if pr_work_shift:
			start_time, end_work = frappe.db.get_value("Private Work Shift Details", {"parent":pr_work_shift,"day":day}, ["start_work","end_work"])
		elif work_shift:
			start_time, end_work = frappe.db.get_value("Work Shift Details", {"parent":work_shift,"day":day}, ["start_work","end_work"])
		
		total_hrs= get_downtime(start_time,end_work)
 		frappe.db.sql("""update `tabEmployee` set start_work=%s,end_work=%s, total_work_hrs=%s where employee= '{employee}'""".format(employee=emp_name),(start_time, end_work, total_hrs),as_dict=1)


	
