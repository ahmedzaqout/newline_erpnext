# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, re

from frappe.utils import getdate, validate_email_add, today, add_years, nowdate, cstr
from frappe.model.naming import make_autoname, getseries
from frappe import throw, _, scrub
#import frappe.permissions
from frappe.permissions import add_user_permission, remove_user_permission, \
	set_user_permission_if_allowed, has_permission
from frappe.model.document import Document
from erpnext.utilities.transaction_base import delete_events
from frappe.utils.nestedset import NestedSet
import datetime, calendar, time
from frappe.utils.password import update_password as _update_password


STANDARD_USERS = ("Guest", "Administrator")

class EmployeeUserDisabledError(frappe.ValidationError):
	pass

class Employee(NestedSet):
	nsm_parent_field = 'reports_to'
	__new_password = None

	def autoname(self):
		naming_method = frappe.db.get_value("HR Settings", None, "emp_created_by")
		if frappe.db.get_value("HR Settings", None, "auto_generate_employee_no") == '1':
			self.name = self.employee_number
		elif not naming_method:
			naming_method == 'Employee Number'
			#throw(_("Please setup Employee Naming System in Human Resource > HR Settings"))
		else:
			if naming_method == 'Naming Series':
				self.name = self.employee_number 
				#set_name_by_naming_series(self)
			elif naming_method == 'Employee Number':
				self.name = self.employee_number
			elif naming_method == 'Full Name':
				#self.set_employee_name()
				self.name = self.employee_name

		self.employee_number = self.name

	def validate(self):
		from erpnext.controllers.status_updater import validate_status
		validate_status(self.status, ["Active", "Left"])
		self.validate_date()
		self.validate_email()
		self.validate_status()
		#self.validate_employee_leave_approver()
		#self.validate_reports_to()
		#self.validate_prefered_email()
                #self.validate_phone_cell()
		self.clearance_leave_balances()
		#self.validate_duplicate_personal_email()
		#self.validate_duplicate_cell_number()

		if self.email and self.is_new():
			#pass
			#self.validate_for_enabled_user_id()
			self.validate_duplicate_user_id()
			self.create_user()
		else:
			existing_user_id = frappe.db.get_value("Employee", self.name, "email")
			if existing_user_id:
				frappe.permissions.remove_user_permission(
					"Employee", self.name, existing_user_id)


		try:
			if self.supervisor:
				self.add_manager_staff()

			self.deactivate_employee()
			self.update_emp_work_shift()
			self.update_emp_work_history()
		except:
			pass	

		if self.basic_salary and  not self.validate_salary_structure():
			frappe.msgprint(_("Press Make Salary Structure Button"))

		if self.employee_dependent: 
			child_num =0
			for d in self.get("employee_dependent"): #('Employee Dependent')
				if d.relation =='Son' or d.relation =='Daughter':
					child_num += 1
			add_depenents_bonus(self.employee, 'Bonus Children', child_num)

		if not self.name:
			frappe.msgprint(__("Data Required!"))
		if self.type and not self.relieving_date:
			frappe.throw(_("Please enter relieving date."))
		elif self.type and self.relieving_date:
			self.service_years = self.get_service_years()
			self.amount = flt(self.calculate_end_service_amount())
			#self.update_emp_status('Left')

		# clear new password
		self.__new_password = self.new_password
		self.new_password = ""
######################################################### Edited By Maysaa ###########################################

	def validate_phone_cell(self):
		import re
		rule = re.compile(r'(^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,7}$)')
		ext_rule = re.compile(r'(^[0-9]{1,4}$)')
		if self.phone_number:
			if not rule.search(self.phone_number):
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
	def create_user(self):
		user = frappe.new_doc("User")
		user.update({
			"name": self.employee_name,
			"email": self.email,
			"enabled": 1,
			"first_name": self.first_name,
			"last_name": self.last_name ,
			"language": self.language 

		})
		user.insert()
		if user.name:
			self.user_id= self.email
		return user.name

	def update_nsm_model(self):
		frappe.utils.nestedset.update_nsm(self)

	def on_update(self):
		self.validate_duplicate_emp_name()
		#self.update_nsm_model()
		self.send_password_notification(self.__new_password)
		#from frappe.core.doctype.user.user import update_password
		#update_password(new_password=self.new_password,old_password=self.__new_password)
		#frappe.clear_cache(user=self.email)
		if self.email:
			self.update_user()
			self.update_user_permissions()

	def email_new_password(self, new_password=None):
		if new_password:
			_update_password(user=self.email, pwd=new_password, logout_all_sessions=self.logout_all_sessions)

	def send_password_notification(self, new_password):
		try:
			if self.flags.in_insert:
				if self.email not in STANDARD_USERS:
					if new_password:
						# new password given, no email required
						_update_password(user=self.email, pwd=new_password,
							logout_all_sessions=self.logout_all_sessions)

					# if not self.flags.no_welcome_mail and self.send_welcome_email:
					# 	self.send_welcome_mail_to_user()
					# 	self.flags.email_sent = 1
					# 	if frappe.session.user != 'Guest':
					# 		msgprint(_("Welcome email sent"))
					# 	return
			else:
				self.email_new_password(new_password)

		except frappe.OutgoingEmailError:
			print(frappe.get_traceback())
			pass # email server not set, don't send email

	def update_user_permissions(self):
		if not self.create_user_permission: return
		#if not has_permission('User Permission', ptype='write', raise_exception=False): return

		employee_user_permission_exists = frappe.db.exists('User Permission', {
			'allow': 'Employee',
			'for_value': self.name,
			'user': self.email
		})

		if employee_user_permission_exists: return

		employee_user_permission_exists = frappe.db.exists('User Permission', {
			'allow': 'Employee',
			'for_value': self.name,
			'user': self.email
		})

		if employee_user_permission_exists: return

		add_user_permission("Employee", self.name, self.email)
		set_user_permission_if_allowed("Company", self.company, self.email)

		#frappe.permissions.add_user_permission("Employee", self.name, self.user_id)
		#frappe.permissions.set_user_permission_if_allowed("Company", self.company, self.user_id)

	def update_user(self):
		# add employee role if missing
		user = frappe.get_doc("User", self.email)
		user.flags.ignore_permissions = True

		if "Employee" not in user.get("roles"):
			user.append_roles("Employee")

		# copy details like Fullname, DOB and Image to User
		if self.employee_name and not (user.first_name and user.last_name):
			employee_name = self.employee_name.split(" ")
			if len(employee_name) >= 3:
				user.last_name = " ".join(employee_name[2:])
				user.middle_name = employee_name[1]
			elif len(employee_name) == 2:
				user.last_name = employee_name[1]

			user.first_name = employee_name[0]

		#if self.date_of_birth:
		#	user.birth_date = self.date_of_birth

		#if self.gender:
		#	user.gender = self.gender

		if self.language:
			user.language = self.language

		if self.image:
			if not user.user_image:
				user.user_image = self.image
				try:
					frappe.get_doc({
						"doctype": "File",
						"file_name": self.image,
						"attached_to_doctype": "User",
						"attached_to_name": self.email
					}).insert()
				except frappe.DuplicateEntryError:
					# already exists
					pass

		user.save()

	def update_user_old_method(self):
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
		if self.email:
			validate_email_add(self.email, True)

	def validate_status(self):
		if self.status == 'Left' and not self.relieving_date:
			throw(_("Please enter relieving date."))

	def validate_for_enabled_user_id(self):
		if not self.status == 'Active':
			return
		enabled = frappe.db.get_value("User", self.email, "enabled")
		if enabled is None:
			frappe.throw(_("User {0} does not exist").format(self.email))
		if enabled == 0:
			frappe.throw(_("User {0} is disabled").format(self.email), EmployeeUserDisabledError)

	def validate_duplicate_user_id(self):
		employee = frappe.db.sql_list("""select name from `tabEmployee` where
			user_id=%s and status='Active' and name!=%s""", (self.email, self.name))
		if employee:
			throw(_("User {0} is already assigned to Employee {1}").format(
				self.email, employee[0]), frappe.DuplicateEntryError)

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


	def validate_prefered_email(self):
		if self.prefered_contact_email and not self.get(scrub(self.prefered_contact_email)):
			frappe.msgprint(_("Please enter " + self.prefered_contact_email))

##########
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



	def update_emp_work_shift(self):
		if getdate(self.shift_change_date) :
			from erpnext.hr import clear_employee_holidays
			from erpnext.hr.doctype.attendance.attendance import update_holiday
			clear_employee_holidays(self.name, self.shift_change_date)
			update_holiday(self.name, self.holiday_list, self.shift_change_date)
			wsh_history = frappe.new_doc('Work Shift History')
			wsh_history.employee= self.name
			wsh_history.work_shift= self.work_shift
			wsh_history.shift_change_date= self.shift_change_date
			wsh_history.flags.ignore_validate = True
			wsh_history.insert(ignore_permissions=True)
			
			
	def validate_duplicate_supervisor(self):
		supervisor = frappe.get_all("Responsible Of Staff",{ "parent":self.supervisor_num,"employee": self.name}, "employee")
		for s in supervisor:
			frappe.msgprint(s.employee)
			if self.name == s.employee:
				isExisted= True
			else:
				isExisted= False
		return isExisted


	def add_manager_staff(self):
		self.validate_duplicate_supervisor()
		if self.supervisor :#and not self.validate_duplicate_supervisor():
			emp_doc = frappe.get_doc('Employee',self.supervisor_num)
			emp_doc.append('responsible_of_staff',{
				'employee':self.name,
				'employee_name':self.employee_name
				})
			emp_doc.flags.ignore_links = True
			emp_doc.flags.ignore_mandatory = True
			emp_doc.flags.ignore_validate =True
			emp_doc.save(ignore_permissions=True)


	def deactivate_employee(self):
		today = datetime.today()
		if self.status != "Active":
			self.relieving_date= today
			self.enabled= 0
		else:
			self.relieving_date=  None
			self.enabled= 1



	def update_end_serv(self):
		self.relieving_date=self.contract_end_date
			
	def update_emp_work_history(self):
		if self.work_place_change_date:
			from_date=self.work_place_change_date
			to_date =self.work_place_change_date
	
			wh_history = frappe.new_doc('Employee Internal Work History')
			wh_history.employee= self.name
			wh_history.branch= self.branch
			wh_history.circle= self.circle
			wh_history.management= self.management
			wh_history.department= self.department
			wh_history.designation= self.designation
			wh_history.from_date= from_date
			wh_history.to_date= to_date
			wh_history.parentfield= "employee_internal_work_history"
			wh_history.parent= self.name
			wh_history.parenttype= "Employee"
			wh_history.flags.ignore_validate = True
			wh_history.flags.ignore_mandatory = True
			wh_history.insert(ignore_permissions=True)
			

	def validate_salary_structure(self):
		employee_name = self.employee_name
		if not self.employee_name:
			employee_name = self.name

		if frappe.db.get_value('Salary Structure', _('Salary Structure')+'_'+ employee_name ):
			return True
		else:
			return False

	def make_salary_structure(self, arg=None):
		if self.validate_salary_structure():
			employee_name = self.employee_name
			if not self.employee_name:
				employee_name = self.name
			sal_struct = frappe.get_doc('Salary Structure', _('Salary Structure')+'_'+ employee_name )
			if sal_struct:
				self.update_earnings(sal_struct)
				self.update_deductions(sal_struct)
		else:
			self.new_salary_structure()
		

	def new_salary_structure(self):
		employee_name = self.employee_name
		if not self.employee_name:
			employee_name = self.name

		if self.date_of_joining:
			joining_date = self.date_of_joining
		else: joining_date = getdate(nowdate())
		
		from erpnext.hr.doctype.payroll_entry.payroll_entry import get_end_date
		if self.payroll_frequency:
			end_date = get_end_date(cstr(joining_date), self.payroll_frequency)['end_date']

		doc = frappe.new_doc('Salary Structure')
		doc.update({
			'name':_('Salary Structure')+'_'+ employee_name,
			'employee_name':employee_name,
			'salary_period':self.payroll_frequency,
			'employees': [{
				'employee': self.name,
				'base':self.basic_salary,
				'from_date':joining_date,
				'to_date':end_date,
				'day_salary':self.day_salary,
				'hour_cost':self.hour_cost,
				'overtime_hour_cost': self.over_hrs
				}]
			
			})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

		doc.append('earnings',{
			'salary_component':'Basic',
			'abbr': 'B',
			'formula':'',
			'amount': self.basic_salary,
			'type': _('Earning')
				})
		doc.save(ignore_permissions=True)

		for e in self.earnings:
			doc.append('earnings',{
				'salary_component':e.salary_component,
				'abbr': e.abbr,
				'formula': e.formula,
				'amount': e.amount,
				'type': e.type
					})
			doc.save(ignore_permissions=True)

		for d in self.deductions:
			doc.append('deductions',{
				'salary_component':d.salary_component,
				'abbr': d.abbr,
				'formula': d.formula,
				'amount': d.amount,
				'type': d.type
					})
			doc.save(ignore_permissions=True)


	def update_earnings(self, sal_struct):
		sal_struct_name = sal_struct.name
		earning_arr, earning_amount= [], []
		for e in sal_struct.get("earnings"):
			earning_arr.append(e.salary_component)

		for earning in self.earnings:
			if earning.salary_component not in earning_arr:
				sal_struct.append(
					'earnings',{
						'salary_component':earning.salary_component,
						'amount': earning.amount
					})
				sal_struct.save(ignore_permissions=True)
			else:
				if frappe.db.get_value('Salary Detail',{'parent':sal_struct_name,'type':'Earning'}):					
					pass

	def update_deductions(self, sal_struct):
		deduction_arr= []
		for d in sal_struct.get("deductions"):
			deduction_arr.append(d.salary_component)

		for deduction in self.deductions:
			if deduction.salary_component not in deduction_arr:
				sal_struct.append(
					'deductions',{
						'salary_component':deduction.salary_component,
						'amount': deduction.amount
					}					
				)
				sal_struct.save(ignore_permissions=True)
			else:
				if frappe.db.get_value('Salary Detail',{'parent':sal_struct.name,'type':'Deduction'}):					
					sal_struct_det = frappe.get_doc('Salary Detail',{'parent':sal_struct.name,'type':'Deduction'})
					sal_struct_det.amount = deduction.amount
					sal_struct_det.save(ignore_permissions=True)
			


	def get_salary_remaining(self):
		return frappe.get_all("Salary Slip", fields=["month","start_date","name","salary_ratio","remaining_salary","basic_salary"],filters={'employee':self.name,'salary_ratio':("!=", 0)})

	def get_emp_warnings(self):
		return frappe.get_all("Warning Information", fields=["warning_date","penalty","penalty_type","warning_type","discount_hour","discount_period_type","employee_violation"],filters={'employee':self.name})
			
	def update_salary_history(self,last_salary,new_salary):
		doc = frappe.new_doc('Salary Change History')
		doc.update({
			'employee':self.name,
			'last_salary':last_salary,
			'new_salary':new_salary,
			'change_date':getdate(nowdate()),
			'user': frappe.session.user
			})
		doc.save(ignore_permissions=True)


	def update_emp_status(self, status):
		self.status= status
		self.contract_end_date=self.relieving_date
		self.enabled = 0


	def get_leaves_taken(self):
		leaves_taken = get_approved_leaves_for_period(self.name, _('Annual Leave'), self.scheduled_confirmation_date, self.relieving_date )
		leave_balance ,leaves_hours = get_leave_balance_on(self.name, _('Annual Leave'), self.relieving_date ,consider_all_leaves_in_the_allocation_period=True)
		
		return leave_balance

	def calculate_end_service_amount(self):
		service_years = self.get_service_years()
		amount = 0.0
		if self.type =='Resignation':
			taken_leaves = self.get_leaves_taken()
			amount = service_years * self.basic_salary +(taken_leaves* self.day_salary)

			if service_years <=5:
				amount= 0.3333 * flt(amount)
			elif service_years <=9:
				amount= 0.6667 * flt(amount)
			elif service_years >=10:
				amount= amount
		elif self.type =='End of the decade':
			amount = service_years * self.basic_salary 

		return amount


	def get_service_years(self):
		service_years = date_diff(self.relieving_date, self.scheduled_confirmation_date)/365
		return service_years


@frappe.whitelist(allow_guest=True)
def employee_child(employee):
	return frappe.db.sql("""select count(name) as count from `tabEmployee Dependent` where relation in ('Son','Daughter') and parent=%s""", employee, as_dict=1)


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
		if not frappe.db.get_value("Employee", {"user_id": doc.name}):
			frappe.msgprint(_("Please set User ID field in an Employee record to set Employee Role"))
			doc.get("roles").remove(doc.get("roles", {"role": "Employee"})[0])

def update_user_permissions(doc, method):
	# called via User hook
	 if "Employee" in [d.role for d in doc.get("roles")]:
	 	if frappe.db.get_value("Employee", {"user_id": doc.email}):
	 		employee = frappe.get_doc("Employee", {"user_id": doc.email})
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
	if employee and frappe.db.get_value("Employee", employee, ["holiday_list", "company"]):
		holiday_list, company = frappe.db.get_value("Employee", employee, ["holiday_list", "company"])
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
def create_user(employee, email):
	emp = frappe.get_doc("Employee", employee)

	employee_name = emp.employee_name.split(" ")
	middle_name = last_name = ""

	if len(employee_name) >= 3:
		last_name = " ".join(employee_name[2:])
		middle_name = employee_name[1]
	elif len(employee_name) == 2:
		last_name = employee_name[1]

	first_name = employee_name[0]

	if email:
		emp.prefered_email = email

	user = frappe.new_doc("User")
	user.update({
		"name": emp.employee_name,
		"email": emp.prefered_email,
		"enabled": 1,
		"first_name": first_name,
		#"middle_name": middle_name,
		"last_name": last_name #,
		#"gender": emp.gender,
		#"birth_date": emp.date_of_birth,
		#"phone": emp.phone_number#,
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
		work_shift = frappe.db.get_value("Employee", emp_name, "work_shift")
		pr_work_shift = frappe.db.get_value("Employee", emp_name, "private_work_shift")
		if pr_work_shift:
			start_time, end_work = frappe.db.get_value("Private Work Shift Details", {"parent":pr_work_shift,"day":day}, ["start_work","end_work"])
		elif work_shift:
			start_time, end_work = frappe.db.get_value("Work Shift Details", {"parent":work_shift,"day":day}, ["start_work","end_work"])
		
		total_hrs= get_downtime(start_time,end_work)
 		frappe.db.sql("""update `tabEmployee` set start_work=%s,end_work=%s, total_work_hrs=%s where employee= '{employee}'""".format(employee=emp_name),(start_time, end_work, total_hrs),as_dict=1)



# add_depenents_bonus to employee salary details and *update employee strucre
@frappe.whitelist()
def add_depenents_bonus(employee, sal_comp, child_num=0):
	if sal_comp== 'Bonus Wife': amount = frappe.db.get_value("HR Settings", None, "bonus_wife_ratio") 
	elif sal_comp== 'Bonus Children':
		bonus_children_ratio = frappe.db.get_value("HR Settings", None, "bonus_children_ratio")
		amount = bonus_children_ratio * child_num

	if frappe.db.get_value('Salary Component',sal_comp) and frappe.db.get_value('Employee',employee):
		emp_sal = frappe.get_doc('Employee',{'employee': employee})
		if frappe.get_value('Salary Detail',{'salary_component':sal_comp,'parent':emp_sal.name,'parenttype':'Employee','type':'Earning'}):
			sal_det = frappe.get_doc('Salary Detail',{'parent':emp_sal.name,'parenttype':'Employee','type':'Earning'})
			sal_det.update({'salary_component':sal_comp,'amount':amount, 'type': _('Earning')})
			sal_det.save(ignore_permissions=True)
		else:
			emp_sal.append('earnings',{'salary_component':sal_comp,'amount':amount, 'type': _('Earning')})
			emp_sal.save(ignore_permissions=True)
		


