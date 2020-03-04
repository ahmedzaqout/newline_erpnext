# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext

from frappe.utils import add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words,today,time_diff_in_hours
from frappe.model.naming import make_autoname

from frappe import msgprint, _
from erpnext.hr.doctype.payroll_entry.payroll_entry import get_start_end_dates
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.utilities.transaction_base import TransactionBase
from frappe.utils.background_jobs import enqueue
import datetime, calendar, time
from calendar import monthrange
from erpnext.hr.doctype.job_description.job_description import month_days
from erpnext.hr.doctype.leave_application.leave_application import get_number_of_leave_days, get_leave_balance_on


class SalarySlip(TransactionBase):
	def autoname(self):
		self.name = make_autoname('Sal Slip/' +self.employee + '/.#####')

	def validate(self):
		#if self.start_date:
		#	self.month = calendar.month_name[getdate(self.start_date).month]
		#	self.year  = getdate(self.start_date).year
		self.status = self.get_status()
		self.validate_dates()
		self.check_existing()
		if not self.salary_slip_based_on_timesheet:
			self.get_date_details()

		if not (len(self.get("earnings")) or len(self.get("deductions"))):
			# get details from salary structure
			self.get_emp_and_leave_details()
		else:
			self.get_leave_details(lwp = self.leave_without_pay)

		# if self.salary_slip_based_on_timesheet or not self.net_pay:
		self.calculate_net_pay()


		company_currency = erpnext.get_company_currency(self.company)
		self.total_in_words = money_in_words(self.rounded_total, company_currency)

		if frappe.db.get_single_value("HR Settings", "max_working_hours_against_timesheet"):
			max_working_hours = frappe.db.get_single_value("HR Settings", "max_working_hours_against_timesheet")
			if self.salary_slip_based_on_timesheet and (self.total_working_hour > float(max_working_hours)):
				pass #frappe.msgprint(_("Total working hours should not be greater than max working hours {0}").
					#			format(max_working_hours), alert=True)
		self.fill_attendance()
		dep=frappe.get_all("Employee Dependent",['name'],filters={"employee":self.employee})
		
		self.no_of_children=len(dep) if dep else 0
		emp_edu=frappe.get_all("Employee Education",['specialization'],filters={"employee":self.employee})
		if emp_edu:
			#frappe.msgprint(ed[0].employee)
			self.specialization=emp_edu[0].specialization
		emp_pers=frappe.get_all("Employee Personal Detail",['identity_no','marital_status'],filters={"employee":self.employee})
		if emp_pers:
			self.identity= emp_pers[0].identity_no
			self.marital_status= emp_pers[0].marital_status 

		emp_det=frappe.get_all("Employee Employment Detail",['department','branch','circle','designation','employment_type','date_of_joining'],filters={"employee":self.employee})
		if emp_det:
			self.circle=emp_det[0].circle
			self.branch=emp_det[0].branch
			self.designation=emp_det[0].designation
			self.department=emp_det[0].department
			self.employment_type=emp_det[0].employment_type
			self.date_of_joining=emp_det[0].date_of_joining


		emp_sal=frappe.get_all("Employee Salary Detail",['grade','grade_category','experience_years'],filters={"employee":self.employee})
		if emp_sal:
			self.grade=emp_sal[0].grade
			self.grade_category=emp_sal[0].grade_category
			self.experience_years=emp_sal[0].experience_year


	def validate_dates(self):
		if date_diff(self.end_date, self.start_date) < 0:
			frappe.throw(_("To date cannot be before From date"))


	def get_ils_exchange_rate(self):
		exchange_rate= frappe.db.get_single_value("HR Settings", "exchange_rate")
		if exchange_rate:
			return exchange_rate

	def calculate_component_amounts(self):
		if not getattr(self, '_salary_structure_doc', None):
			self._salary_structure_doc = frappe.get_doc('Salary Structure', self.salary_structure)

		data = self.get_data_for_eval()

		for key in ('earnings', 'deductions'):
			for struct_row in self._salary_structure_doc.get(key):
				amount = self.eval_condition_and_formula(struct_row, data)
				if amount and struct_row.statistical_component == 0:
					self.update_component_row(struct_row, amount, key)
		if self.company == "Nawa":
			exist=False
			for struct_row in self.get("deductions"):
				if struct_row.salary_component =="Savings":
					exist=True
			s_deta =frappe.get_doc("Employee Salary Detail",self.employee)			
			if s_deta.has_saving and s_deta.has_saving  == 1:
				if frappe.db.get_single_value("HR Settings", "employee_ratio_employee_saving"):
					employee_ratio_employee_saving = frappe.db.get_single_value("HR Settings", "employee_ratio_employee_saving")
					if len(frappe.get_list('Salary Component', ['name'],filters={"name":"Savings","type":"Deduction"})) <= 0:
						frappe.get_doc({"doctype" : "Salary Component","salary_component":"Savings","type":"Deduction","salary_component_abbr":"SA"}).insert(ignore_permissions=True)
					amount_savings = employee_ratio_employee_saving * self.basic_salary /100.0
					if not exist:
						if employee_ratio_employee_saving>0:
							self.append("deductions", {
							'amount': amount_savings,
							'default_amount': amount_savings ,
							'depends_on_lwp' : 0,
							'salary_component' : "Savings",
							'abbr' : struct_row.abbr,
							'do_not_include_in_total' : 0,
							'amount_ils':amount_savings * flt(self.get_ils_exchange_rate())
						})
			existt=False
			for struct_row in self.get("deductions"):
				if struct_row.salary_component =="Insurance":
					existt=True
				s_deta =frappe.get_doc("Employee Salary Detail",self.employee)			
			if s_deta.has_insurance and s_deta.has_insurance  == 1:
				if frappe.db.get_single_value("HR Settings", "the_percentage_of_the_employee_insurance"):
					employee_ratio_employee_insurance = frappe.db.get_single_value("HR Settings", "the_percentage_of_the_employee_insurance")
					if len(frappe.get_list('Salary Component', ['name'],filters={"name":"Insurance","type":"Deduction"})) <= 0:
						frappe.get_doc({"doctype" : "Salary Component","salary_component":"Insurance","type":"Deduction","salary_component_abbr":"IN"}).insert(ignore_permissions=True)
					amount_insurance = employee_ratio_employee_insurance * self.basic_salary /100.0
					if not existt:
						if employee_ratio_employee_insurance >0:
							self.append("deductions", {
							'amount': amount_insurance,
							'default_amount': amount_insurance ,
							'depends_on_lwp' : 0,
							'salary_component' : "Insurance",
							'abbr' : struct_row.abbr,
							'do_not_include_in_total' : 0,
							'amount_ils':amount_insurance * flt(self.get_ils_exchange_rate())
						})
		
		exista=False
		for struct_row in self.get("deductions"):
			if struct_row.salary_component =="Income Tax":
				exista=True

			if len(frappe.get_list('Salary Component', ['name'],filters={"name":"Income Tax","type":"Deduction"})) <= 0:
				frappe.get_doc({"doctype" : "Salary Component","salary_component":"Income Tax","type":"Deduction","salary_component_abbr":"TX"}).insert(ignore_permissions=True)

		if not exista:
			sal_ils = self.basic_salary * flt(self.get_ils_exchange_rate())
			if sal_ils <= 75000:
				amout_tax = 5 * sal_ils/100
			elif sal_ils > 75000 and sal_ils <= 15000:
				amout_tax = 10 * sal_ils/100
			else:
				amout_tax = 15 * sal_ils/100
			amout_tax_doll =  amout_tax /flt(self.get_ils_exchange_rate())
			self.append("deductions", {
			'amount': amout_tax_doll,
			'default_amount': amout_tax_doll ,
			'depends_on_lwp' : 0,
			'salary_component' : "Income Tax",
			'abbr' : struct_row.abbr,
			'do_not_include_in_total' : 0,
			'amount_ils':amout_tax
			})

				

	def update_component_row(self, struct_row, amount, key):
		component_row = None
		for d in self.get(key):
			if d.salary_component == struct_row.salary_component:
				component_row = d
		#if struct_row.salary_component == _('Basic'):
		#	amount = self.basic_salary

		if not component_row:
			self.append(key, {
				'amount': amount,
				'default_amount': amount ,
				'depends_on_lwp' : struct_row.depends_on_lwp,
				'salary_component' : struct_row.salary_component,
				'abbr' : struct_row.abbr,
				'do_not_include_in_total' : struct_row.do_not_include_in_total,
				'amount_ils':amount * flt(self.get_ils_exchange_rate())
			})
		else:
			component_row.amount = amount

	def eval_condition_and_formula(self, d, data):
		try:
			condition = d.condition.strip() if d.condition else None
			if condition:
				if not frappe.safe_eval(condition, None, data):
					return None
			amount = d.amount
			if d.amount_based_on_formula:
				formula = d.formula.strip() if d.formula else None
				if formula:
					amount = frappe.safe_eval(formula, None, data)
			if amount:
				data[d.abbr] = amount

			return amount

		except NameError as err:
			frappe.throw(_("Name error: {0}".format(err)))
		except SyntaxError as err:
			frappe.throw(_("Syntax error in formula or condition: {0}".format(err)))
		except Exception as e:
			frappe.throw(_("Error in formula or condition: {0}".format(e)))
			raise

	def get_data_for_eval(self):
		'''Returns data for evaluating formula'''
		data = frappe._dict()

		if not self.salary_structure:
			frappe.throw(_("Employee has not Salary Structure"))
		data.update(frappe.get_doc("Salary Structure Employee",
			{"employee": self.employee, "parent": self.salary_structure}).as_dict())

		data.update(frappe.get_doc("Employee", self.employee).as_dict())
		data.update(self.as_dict())

		# set values for components
		salary_components = frappe.get_all("Salary Component", fields=["salary_component_abbr"])
		for sc in salary_components:
			data.setdefault(sc.salary_component_abbr, 0)

		for key in ('earnings', 'deductions'):
			for d in self.get(key):
				data[d.abbr] = d.amount

		return data


	def get_emp_and_leave_details(self):
		'''First time, load all the components from salary structure'''
		if self.employee:
			self.set("earnings", [])
			self.set("deductions", [])

			if not self.salary_slip_based_on_timesheet:
				self.get_date_details()
			self.validate_dates()
			joining_date = frappe.db.get_value("Employee Employment Detail", self.employee,
				["date_of_joining"])
			relieving_date =''
			self.get_leave_details(joining_date, relieving_date)
			struct = self.check_sal_struct(joining_date, relieving_date)

			if struct:
				self._salary_structure_doc = frappe.get_doc('Salary Structure', struct)
				self.salary_slip_based_on_timesheet = self._salary_structure_doc.salary_slip_based_on_timesheet or 0
				self.set_time_sheet()
				self.pull_sal_struct()
				self.set_warnings()

	def set_time_sheet(self):
		#if self.salary_slip_based_on_timesheet:
		self.set("timesheets", [])
		#timesheets = frappe.db.sql(""" select * from `tabTimesheet` where employee = %(employee)s and start_date BETWEEN %(start_date)s AND %(end_date)s and type!='compensatory' and docstatus = 1""", {'employee': self.employee, 'start_date': self.start_date, 'end_date': self.end_date}, as_dict=1)
		timesheets = frappe.db.sql("select td.activity_type, td.hours as total_hours,t.docstatus,employee,date(from_time) as ddate,type from tabTimesheet as t join `tabTimesheet Detail` as td on t.name=td.parent and t.docstatus=1 where employee = %(employee)s and date(from_time) BETWEEN %(start_date)s AND %(end_date)s and type!='compensatory' and td.docstatus = 1", {'employee': self.employee, 'start_date': self.start_date, 'end_date': self.end_date}, as_dict=1)

		overtime_hour_price = frappe.db.get_single_value("HR Settings", "overtime_hour_price")
		overtime_hour_price_in_holidays = frappe.db.get_single_value("HR Settings", "overtime_hour_price_in_holidays")

		for data in timesheets:
			working_hours= data.total_hours
			if data.type == 'Normal':
				working_hours = data.total_hours * float(overtime_hour_price)
				self.over_hrs = overtime_hour_price
			if data.type == 'With Leave':
				working_hours = data.total_hours * float(overtime_hour_price_in_holidays)
				self.over_hrs = overtime_hour_price_in_holidays

			self.append('timesheets', {
				'time_sheet': data.activity_type,
				'working_hours': working_hours,
				'hour_rate': self.over_hrs,
				'date': data.ddate
			})


	def set_warnings(self):
		self.warnings_total_hours = 0.0
		self.set("warnings", [])
		warnings = frappe.db.sql("select * from `tabWarning Information` where  docstatus = 1 and penalty_type='Discount' and employee = %(employee)s and warning_date BETWEEN %(start_date)s AND %(end_date)s ", {'employee': self.employee, 'start_date': self.start_date, 'end_date': self.end_date}, as_dict=1)
		if warnings:
			for data in warnings:
				self.append('warnings', {
					'employee_violation': data.employee_violation,
					'penalty': data.penalty,
					'discount_hour': data.discount_hour,
					'warning_date': data.warning_date
				})
				self.warnings_total_hours += float(data.discount_hour)


	def get_date_details(self):
		date_details = get_start_end_dates(self.payroll_frequency, self.start_date or self.posting_date)
		self.start_date = date_details.start_date
		self.end_date = date_details.end_date

	def check_sal_struct(self, joining_date, relieving_date):
		cond = ''
		if self.payroll_frequency:
			cond = """and payroll_frequency = '%(payroll_frequency)s'""" % {"payroll_frequency": self.payroll_frequency}

		st_name = frappe.db.sql("""select parent from `tabSalary Structure Employee`
			where employee=%s and (from_date <= %s or from_date <= %s)
			and (to_date is null or to_date >= %s or to_date >= %s)
			and parent in (select name from `tabSalary Structure`
				where is_active = 'Yes'%s)
			"""% ('%s', '%s', '%s','%s','%s', cond),(self.employee, self.start_date, joining_date, self.end_date, relieving_date))

		if st_name:
			if len(st_name) > 1:
				frappe.msgprint(_("Multiple active Salary Structures found for employee {0} for the given dates")
					.format(self.employee), title=_('Warning'))
			return st_name and st_name[0][0] or ''
		else:
			self.salary_structure = None
			#frappe.msgprint(_("No active or default Salary Structure found for employee {0} for the given dates")
			#	.format(self.employee), title=_('Salary Structure Missing'))

	def pull_sal_struct(self):
		from erpnext.hr.doctype.salary_structure.salary_structure import make_salary_slip

		if self.salary_slip_based_on_timesheet:
			self.salary_structure = self._salary_structure_doc.name
			#self.hour_rate = self._salary_structure_doc.hour_rate
		self.total_working_hour = sum([d.working_hours or 0.0 for d in self.timesheets]) or 0.0
		wages_amount = 0.0
		if self.total_working_hour:
			wages_amount =  self.total_working_hour
			
		self.add_earning_for_hourly_wages(self, self._salary_structure_doc.salary_component, wages_amount)

		make_salary_slip(self._salary_structure_doc.name, self)

	def process_salary_structure(self):
		'''Calculate salary after salary structure details have been updated'''
		if not self.salary_slip_based_on_timesheet:
			self.get_date_details()
		self.pull_emp_details()
		self.get_leave_details()
		self.calculate_net_pay()

		hr_per_day= month_days(self.employee , self.start_date)
		self.day_salary = self.basic_salary / self.total_working_days
		if hr_per_day and hr_per_day[2] != 0:
			self.hour_cost = self.day_salary / hr_per_day[2]

	def add_earning_for_hourly_wages(self, doc, salary_component, amount):
		row_exists = False
		for row in doc.earnings:
			if row.salary_component == salary_component:				
				row.amount = amount
				row_exists = True
				break

		if not row_exists:
			wages_row = {
				"salary_component": salary_component,
				"abbr": frappe.db.get_value("Salary Component", salary_component, "salary_component_abbr"),
				"amount": self.total_working_hour if  self.total_working_hour else 0.0
			}
			doc.append('earnings', wages_row)

	def pull_emp_details(self):
		emp = frappe.db.get_value("Employee Salary Detail", self.employee, ["bank_name", "bank_ac_no"], as_dict=1)
		if emp:
			self.bank_name = emp.bank_name
			self.bank_account_no = emp.bank_ac_no


	def get_leave_details(self, joining_date=None, relieving_date=None, lwp=None):
		if not joining_date:
			joining_date = frappe.db.get_value("Employee Employment Detail", self.employee,
				["date_of_joining"])
		#####
		#job_number = frappe.db.get_value("job_description", self.employee, "job_number")
		#t_working_days = frappe.db.get_value("Employee Salary Detail", self.employee, ["working_hours_per_day"])
		days= month_days(self.employee, self.start_date)
		if self.payroll_frequency=='Monthly':
			working_days = days[0]
		elif self.payroll_frequency=='Hourly':
			working_days = int(days[1])
		else:
			working_days = date_diff(self.end_date, self.start_date)+1

		holidays = self.get_holidays_for_employee(self.start_date, self.end_date)
		actual_lwp = self.calculate_lwp(holidays, working_days)
		if not cint(frappe.db.get_value("HR Settings", None, "include_holidays_in_total_working_days")):
			working_days -= len(holidays)
			if working_days < 0:
				pass #frappe.throw(_("There are more holidays than working days this month."))

		if not lwp:
			lwp = actual_lwp
		elif lwp != actual_lwp:
			frappe.msgprint(_("Leave Without Pay does not match with approved Leave Application records"))


		self.total_working_days = working_days
		self.leave_without_pay = lwp

		payment_days = flt(self.get_payment_days(joining_date, relieving_date)) - flt(lwp)
		self.payment_days = payment_days > 0 and payment_days or 0
		#self.total_working_days = self.payment_days


	def get_payment_days(self, joining_date, relieving_date):
		start_date = getdate(self.start_date)
		if joining_date:
			if getdate(self.start_date) <= joining_date <= getdate(self.end_date):
				start_date = joining_date
			elif joining_date > getdate(self.end_date):
				return

		end_date = getdate(self.end_date)
		if relieving_date:
			if getdate(self.start_date) <= relieving_date <= getdate(self.end_date):
				end_date = relieving_date
			elif relieving_date < getdate(self.start_date):
				frappe.throw(_("Employee relieved on {0} must be set as 'Left'")
					.format(relieving_date))

		payment_days = date_diff(end_date, start_date) + 1

		if not cint(frappe.db.get_value("HR Settings", None, "include_holidays_in_total_working_days")):
			holidays = self.get_holidays_for_employee(start_date, end_date)
			payment_days -= len(holidays)
		return payment_days

	def get_holidays_for_employee(self, start_date, end_date):
		holiday_list = get_holiday_list_for_employee(self.employee)
		holidays = frappe.db.sql_list('''select holiday_date from `tabHoliday`
			where
				parent=%(holiday_list)s
				and holiday_date >= %(start_date)s
				and holiday_date <= %(end_date)s''', {
					"holiday_list": holiday_list,
					"start_date": start_date,
					"end_date": end_date
				})

		holidays = [cstr(i) for i in holidays]

		return holidays

	def calculate_lwp(self, holidays, working_days):
		lwp = 0
		lwhp = 0
		holidays = "','".join(holidays)
		for d in range(working_days):
			dt = add_days(cstr(getdate(self.start_date)), d)
			leave = frappe.db.sql("""
				select t1.name, t1.half_day
				from `tabLeave Application` t1, `tabLeave Type` t2
				where t2.name = t1.leave_type
				and t2.is_lwp = 1
				and t1.docstatus = 1
				and t1.status = 'Approved'
				and t1.employee = %(employee)s
				and CASE WHEN t2.include_holiday != 1 THEN %(dt)s not in ('{0}') and %(dt)s between from_date and to_date
				WHEN t2.include_holiday THEN %(dt)s between from_date and to_date
				END
				""".format(holidays), {"employee": self.employee, "dt": dt})
			if leave:
				lwp = cint(leave[0][1]) and (lwp + 0.5) or (lwp + 1)

			half_leave = frappe.db.sql("""
				select t1.name, t1.half_day
				from `tabLeave Application` t1, `tabLeave Type` t2
				where t2.name = t1.leave_type
				and t2.is_lwp = 0
				and t2.half_salary = 1
				and t1.docstatus = 1
				and t1.status = 'Approved'
				and t1.employee = %(employee)s
				and CASE WHEN t2.include_holiday != 1 THEN %(dt)s not in ('{0}') and %(dt)s between from_date and to_date
				WHEN t2.include_holiday THEN %(dt)s between from_date and to_date
				END
				""".format(holidays), {"employee": self.employee, "dt": dt})
			if half_leave:
				lwhp =  (lwhp + 0.5) 

		return lwp + lwhp 

	def check_existing(self):
		if not self.salary_slip_based_on_timesheet:
			ret_exist = frappe.db.sql("""select name from `tabSalary Slip`
						where start_date = %s and end_date = %s and docstatus != 2
						and employee = %s and name != %s""",
						(self.start_date, self.end_date, self.employee, self.name))
			if ret_exist:
				self.employee = ''
				frappe.throw(_("Salary Slip of employee {0} already created for this period").format(self.employee))
		else:
			for data in self.timesheets:
				if frappe.db.get_value('Timesheet', data.time_sheet, 'status') == 'Payrolled':
					frappe.throw(_("Salary Slip of employee {0} already created for time sheet {1}").format(self.employee, data.time_sheet))

	def sum_components(self, component_type, total_field):
		joining_date = frappe.db.get_value("Employee Employment Detail", self.employee,
			["date_of_joining"])
		
		#if not relieving_date:
		#	relieving_date = getdate(self.end_date)

		if not joining_date:
			frappe.throw(_("Please set the Date Of Joining for employee {0}").format(frappe.bold(self.employee_name)))

		for d in self.get(component_type):
			if (self.salary_structure and
				cint(d.depends_on_lwp) and
				(not
				    self.salary_slip_based_on_timesheet or
					getdate(self.start_date) < joining_date #or
					#getdate(self.end_date) > relieving_date
				)):

				d.amount = rounded(
					(flt(d.default_amount) * flt(self.payment_days)
					/ cint(self.total_working_days)), self.precision("amount", component_type)
				)

			elif not self.payment_days and not self.salary_slip_based_on_timesheet and \
				cint(d.depends_on_lwp):
				d.amount = 0
			elif not d.amount:
				d.amount = d.default_amount
			if not d.do_not_include_in_total:
				self.set(total_field, self.get(total_field) + flt(d.amount))

	def discount_salary_from_leave(self):
		flag = False
		leave_balance= get_leave_balance_on(self.employee,_('Annual Leave'), self.start_date,consider_all_leaves_in_the_allocation_period=True)
		if leave_balance[0]!= 0 and frappe.db.get_single_value("HR Settings", "discount_salary_from_leaves") == 1 and frappe.db.get_value("Employment Type", self.employment_type,"discount_salary_from_leaves") == 1:
			flag = True
		return flag

	def calculate_net_pay(self):
		if self.salary_structure:
			self.calculate_component_amounts()
			for e in self.earnings:
				if e.salary_component == 'Basic':
					#e.salary_component= 'Basic'
					e.amount = self.basic_salary *(self.payment_days/ self.total_working_days)
					e.amount_ils = self.basic_salary * flt(self.get_ils_exchange_rate())


		disable_rounded_total = cint(frappe.db.get_value("Global Defaults", None, "disable_rounded_total"))
		job_number = frappe.db.get_value("Employee Salary Detail", self.employee, 'job_number')
		overtime_type = frappe.db.get_value("Job Description", job_number, "overtime_type")
			
		self.total_deduction = 0.0001
		self.gross_pay = 0.0001
		self.total_overtime = 0.0001
		self.rounded_total = 0.0001
		self.net_pay = 0.0001

		self.sum_components('earnings' , 'gross_pay')
		self.sum_components('deductions', 'total_deduction')

		self.set_loan_repayment()

		if frappe.db.get_single_value("HR Settings", "daily_overtime") == 1 or overtime_type == 'Dailly':
			for d in self.timesheets:
				work_hrs = d.working_hours or 0.0
				self.total_overtime +=  flt(self.hour_cost) * flt(work_hrs) 
				#self.total_overtime = self.total_overtime+( flt(self.hour_cost) * flt(self.over_hrs) * flt(work_hrs))
		

		if overtime_type == 'Monthly':
			self.total_overtime= flt(self.hour_cost) *  flt(self.total_working_hour) 
			#self.total_overtime= flt(self.hour_cost) * flt(self.over_hrs) * flt(self.total_working_hour)

		self.total_hours_discount = flt(self.hrs_disc) * flt(self.hour_cost) or 0.0001

		if self.discount_salary_from_leave():
			disc_hrs = 0.0
			self.total_hours_discount = 0.0001
		else: disc_hrs = self.total_hours_discount

		if frappe.db.get_single_value("HR Settings", "auto_discount_from_salary") == 1:
			disc_funds = self.total_fund_amount
		else: 
			disc_funds = 0.0
			self.total_fund_amount = 0.0001
		
		self.net_pay = flt(self.gross_pay) - ( flt(self.total_deduction) + flt(self.total_loan_repayment) +flt(disc_funds)+flt(disc_hrs) ) + flt(self.total_overtime) 


		self.rounded_total = self.net_pay 
			#rounded(self.net_pay,self.precision("net_pay") if disable_rounded_total else 0.0001)


	def set_loan_repayment(self):
		self.set('loans', [])
		self.total_loan_repayment = 0.0001
		self.total_interest_amount = 0.0001
		self.total_principal_amount = 0.0001

		for loan in self.get_employee_loan_details():
			self.append('loans', {
				'employee_loan': loan.name,
				'total_payment': loan.total_payment,
				'interest_amount': loan.interest_amount,
				'principal_amount': loan.principal_amount #,
				#'employee_loan_account': loan.employee_loan_account,
				#'interest_income_account': loan.interest_income_account
			})

			self.total_loan_repayment += loan.total_payment
			self.total_interest_amount += loan.interest_amount
			self.total_principal_amount += loan.principal_amount

	def get_employee_loan_details(self):
		return frappe.db.sql("""select rps.principal_amount, rps.interest_amount, el.name,
				rps.total_payment, el.employee_loan_account, el.interest_income_account
			from
				`tabRepayment Schedule` as rps, `tabEmployee Loan` as el
			where
				el.name = rps.parent and rps.payment_date between %s and %s and
				el.repay_from_salary = 1 and el.docstatus = 1 and el.employee = %s""",
			(self.start_date, self.end_date, self.employee), as_dict=True) or []

	def on_submit(self):
		#if self.net_pay < 0:
		#	pass#frappe.throw(_("Net Pay cannot be less than 0"))
		if flt(self.net_pay) > 0.0:
			self.set_status()
			#self.update_status(self.name)
			if frappe.db.get_single_value("HR Settings", "email_salary_slip_to_employee") == 1:
				self.email_salary_slip()

		#leave_balance= get_leave_balance_on(self.employee,_('Annual Leave'), self.start_date,consider_all_leaves_in_the_allocation_period=True)
		self.update_leave_balance()
		if self.company == "Nawa":	
			s_deta =frappe.get_doc("Employee Salary Detail",self.employee)			
			if s_deta.has_saving and s_deta.has_saving  == 1:
				self.update_savings()
			if s_deta.has_insurance and s_deta.has_insurance  == 1:
				self.update_insurance ()

	def on_cancel(self):
		self.set_status()
		#self.update_status()

	def email_salary_slip(self):
		receiver = frappe.db.get_value("Employee Personal Detail", self.employee, "user_id")

		if receiver:
			email_args = {
				"recipients": [receiver],
				"message": _("Please see attachment"),
				"subject": 'Salary Slip - from {0} to {1}'.format(self.start_date, self.end_date),
				"attachments": [frappe.attach_print(self.doctype, self.name, file_name=self.name)],
				"reference_doctype": self.doctype,
				"reference_name": self.name
				}
			enqueue(method=frappe.sendmail, queue='short', timeout=300, async=True, **email_args)
		else:
			msgprint(_("{0}: Employee email not found, hence email not sent").format(self.employee_name))

	def update_savings(self):
		employee_ratio_employee_saving = 0.0
		company_ratio_employee_saving = 0.0
		if frappe.db.get_single_value("HR Settings", "employee_ratio_employee_saving"):
			employee_ratio_employee_saving = frappe.db.get_single_value("HR Settings", "employee_ratio_employee_saving")
		if frappe.db.get_single_value("HR Settings", "company_ratio_employee_saving"):
			company_ratio_employee_saving = frappe.db.get_single_value("HR Settings", "company_ratio_employee_saving")
		
		employee_savings = float(employee_ratio_employee_saving) * float(self.basic_salary) /100.0
		company_savings = float(company_ratio_employee_saving) * float(self.basic_salary) /100.0
		s_d =frappe.get_doc("Employee Salary Detail",self.employee)
		if s_d:
			s_d.employee_savings= s_d.employee_savings + employee_savings + company_savings
			s_d.flags.ignore_permissions=True
			s_d.save()

	def update_insurance(self):
		employee_ratio_employee_ins = 0.0
		company_ratio_employee_ins = 0.0
		if frappe.db.get_single_value("HR Settings", "the_percentage_of_the_employee_insurance"):
			employee_ratio_employee_ins = frappe.db.get_single_value("HR Settings", "the_percentage_of_the_employee_insurance")
		if frappe.db.get_single_value("HR Settings", "company_ratio_employee_ insurance"):
			company_ratio_employee_ins = frappe.db.get_single_value("HR Settings", "company_ratio_employee_ insurance")
		
		employee_in = float(employee_ratio_employee_ins) * float(self.basic_salary) /100.0
		company_in = float(company_ratio_employee_ins) * float(self.basic_salary) /100.0
		s_d =frappe.get_doc("Employee Salary Detail",self.employee)
		if s_d:
			s_d.employee_insurrance= s_d.employee_insurrance + employee_in + company_in
			s_d.flags.ignore_permissions=True
			s_d.save()




	def update_status(self, salary_slip=None):
		for data in self.timesheets:
			if data.time_sheet:
				timesheet = frappe.get_doc('Timesheet', data.time_sheet)
				timesheet.salary_slip = salary_slip
				timesheet.flags.ignore_validate_update_after_submit = True
				timesheet.set_status()
				timesheet.save()

	def set_status(self, status=None):
		'''Get and update status'''
		if not status:
			status = self.get_status()
		self.db_set("status", status)

	def get_status(self):
		if self.docstatus == 0:
			status = "Draft"
		elif self.docstatus == 1:
			status = "Submitted"
		elif self.docstatus == 2:
			status = "Cancelled"
		return status

	def update_leave_balance(self):
		if  not frappe.db.get_value("Leave Type",_('Annual Leave'), "name") :
			frappe.throw(_("{0} not found, you should add it to complete the process").format(_('Annual Leave')) )
		if self.discount_salary_from_leave():
			#from_date = add_days(cstr(getdate(today())), 1)
			from erpnext.hr import get_emp_work_shift
			day = calendar.day_name[getdate(self.start_date).weekday()];
			shift_diff = get_emp_work_shift(self.employee,day)
			#emp_wshift = frappe.db.get_value("Employee Employment Detail", self.employee, "work_shift")
			#employee_start_time = frappe.db.get_value("Work Shift Details", {"parent":emp_wshift,"day":day}, "start_work")
			#employee_end_time = frappe.db.get_value("Work Shift Details", {"parent":emp_wshift,"day":day}, "end_work")
			#shift_diff = time_diff_in_hours(employee_end_time, employee_start_time)
			day_count = flt(self.hrs_disc) / flt(shift_diff)
			to_date = add_days(cstr(getdate(self.start_date)), day_count)
			#to_date= datetime.datetime.strptime(to_date,'%Y-%m-%d')

			doc = frappe.db.get_value('Leave Application',{'leave_type':_('Annual Leave'),'employee':self.employee,'status':'Approved','from_date':(">=",self.start_date ),'to_date':("<=",to_date ),'description': _('Auto Entry: Discount form Leaves')})
			if not doc and self.hrs_disc >= shift_diff:
				leave = frappe.new_doc('Leave Application')
				leave.employee= self.employee
				leave.employee_name= self.employee_name
				leave.leave_type= _('Annual Leave')
				leave.from_date = self.start_date
				leave.to_date = to_date
				leave.total_leave_days = get_number_of_leave_days(self.employee, _('Annual Leave'),self.start_date,to_date)
				leave.status = 'Approved'
				leave.hours = self.hrs_disc
				leave.balance_hrs = self.hrs_disc
				leave.leave_balance = get_leave_balance_on(self.employee,_('Annual Leave'), self.start_date,
					consider_all_leaves_in_the_allocation_period=True)
				leave.description = _('Auto Entry: Discount form Leaves')
				leave.docstatus= 1
				leave.discount_salary_from_leaves= 1
				leave.flags.ignore_validate = True
				leave.insert(ignore_permissions=True)
				leave.submit()

	def fill_attendance(self):
		emp_map  = frappe.db.sql("""select distinct att.attendance_date, emp.employee_name, att.name as attname,dept.name as deptname, emp.name,emp.employee ,dept.departure_date, DAYNAME(att.attendance_date) as day,att.attendance_time, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as total_hours ,GREATEST(round((TIMESTAMPDIFF(MINUTE,shd.start_work,shd.end_work))/60,3),0) as total_work_hrs,ifnull(overtime_hours,0) as overtime_hours,ifnull(tsh.holiday_overtime_hours,0) as holiday_overtime_hours,compensatory,tsh.type, tsh.from_time ,att.status,shd.start_work, ifnull(ext.early_diff,0) as early_departure,ifnull(ext.ext_diff,0) as ext_diff, work_shift, emp.holiday_list,ifnull(GREATEST(round(TIMESTAMPDIFF(MINUTE,shd.start_work,att.attendance_time)/60,2),0),0) as late_hrs from `tabEmployee Employment Detail` as emp   
join  tabAttendance as att on att.employee=emp.employee and discount_salary_from_leaves=0 and att.docstatus = 1
left join  tabDeparture as dept on dept.employee=emp.employee and att.attendance_date=dept.departure_date and dept.docstatus = 1
left join `tabWork Shift Details` as shd on shd.parent =  work_shift and shd.day = DAYNAME(att.attendance_date)
left join (select t.docstatus,employee,from_time,ifnull(sum(CASE WHEN type='compensatory' THEN hours END),0) as compensatory, ifnull(sum(CASE WHEN type='Normal' THEN hours END),0) as overtime_hours, ifnull(sum(CASE WHEN type='With Leave' THEN hours END),0) as holiday_overtime_hours,type from tabTimesheet as t join `tabTimesheet Detail` as td on t.name=td.parent and t.docstatus=1 group by date(from_time),employee) as tsh on emp.employee=tsh.employee and att.attendance_date=date(tsh.from_time) and tsh.docstatus = 1 
left join (select employee,depstat,exitstat, permission_date,sum(early_diff)/60 as early_diff, sum(diff) as ext_diff from (
select employee,docstatus as depstat,0 as exitstat, permission_date,early_diff, 0 as diff from `tabExit permission` where permission_type='Early Departure' and docstatus = 1
union all 
select employee,0 as depstat,docstatus as exitstat, permission_date,0 as early_diff ,TIME_TO_SEC(diff_exit)/3600 as diff from `tabExit permission` where type='Return' and permission_type='Exit with return' and docstatus = 1) as d group by permission_date,employee) as ext 
on emp.employee=ext.employee and att.attendance_date=ext.permission_date 
where  emp.employee = %s and  att.attendance_date >= %s and att.attendance_date <= %s order by emp.employee, attendance_date""" 
,(self.employee,self.start_date, self.end_date,), as_dict=1)
		
		att=[]
		for em in emp_map:
			if em.total_hours:
				total= em.total_hours
			else: 
				total= 0.0
			if em.ext_diff:
				total-=em.ext_diff
			if em.overtime_hours:
				total+=em.overtime_hours
			if total<0:
				total=0
			total_hours= 0.0
			if em.total_hours:total_hours = round(float(em.total_hours),1)
			row= {"day":em.attendance_date,
			"total_hours": total_hours,
			"status": em.status,
			"late_hours" : round(em.late_hrs,1),
			"overtime": round(em.overtime_hours,1),
			"early_depature":round(em.early_departure,1),
			"exit_permition": round(em.ext_diff,1),
			"total_working" : round(total,1)}
			att.append(row)
		self.set("attendance",att)



def unlink_ref_doc_from_salary_slip(ref_no):
	linked_ss = frappe.db.sql_list("""select name from `tabSalary Slip`
	where journal_entry=%s and docstatus < 2""", (ref_no))
	if linked_ss:
		for ss in linked_ss:
			ss_doc = frappe.get_doc("Salary Slip", ss)
			frappe.db.set_value("Salary Slip", ss_doc.name, "journal_entry", "")



@frappe.whitelist()
def get_working_total_hours(employee=None, start_date=None, end_date=None):
	from erpnext.hr import get_compensatory, get_permissions
	from datetime import date, timedelta
	from datetime import datetime 
	cur_date = getdate(start_date)
	if start_date and ( isinstance(start_date, str) or isinstance(start_date, unicode)) :
		start_date = datetime.strptime(start_date , '%Y-%m-%d')
	if end_date and ( isinstance(end_date, str) or isinstance(end_date, unicode)):
		end_date= datetime.strptime(end_date , '%Y-%m-%d')
	month = cur_date.month
	year  = cur_date.year
	total_hrs, real_hrs, total_real_hrs= 0.0, 0.0, 0.0
	
	delta = cint(monthrange( cint(year), cint(month) )[1])
	if end_date and start_date:
		delta = end_date- start_date	
		delta=delta.days
	sdate=  getdate(start_date)
	
	total_ho=0
	next_total_hrs=0
	
	status=""
	total_work_hrss=0
	total_d=0
	disc=0
	total_all=0
	total_l=0
	from erpnext.hr.report.monthly_attendance_sheet.monthly_attendance_sheet import get_wsh_history
	for i in range(delta + 1):
		total=0
    		day = sdate + timedelta(days=i)
		total_work_hrs, start_work, end_work,next_day,next_total_work_hrs = get_wsh_history(employee, getdate(day))
		if next_day and next_day==1:
			emp_map  = frappe.db.sql("""select  att.attendance_date, dept.departure_date,att.attendance_time, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as total_hours ,GREATEST(24-round((TIMESTAMPDIFF(MINUTE,dept.departure_time,att.attendance_time))/60,3),0) as next_total_hrs ,att.status 
from tabAttendance as att left join  tabDeparture as dept on att.employee=dept.employee and date_add(att.attendance_date,interval 1 day)  =dept.departure_date and dept.docstatus = 1 and att.docstatus=1  where att.docstatus=1  and dept.docstatus = 1 and att.employee= '{0}' and att.attendance_date = '{1}' """.format(employee,getdate(day)), as_dict=1)
		else:
			emp_map  = frappe.db.sql("""select  att.attendance_date, dept.departure_date,att.attendance_time, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as total_hours ,GREATEST(24-round((TIMESTAMPDIFF(MINUTE,dept.departure_time,att.attendance_time))/60,3),0) as next_total_hrs ,att.status 
	from tabAttendance as att join  tabDeparture as dept on att.employee=dept.employee and att.attendance_date=dept.departure_date and dept.docstatus = 1 and att.docstatus=1  where att.docstatus=1  and dept.docstatus = 1  and att.employee= '{0}' and att.attendance_date = '{1}' """.format(employee,getdate(day)), as_dict=1)
		attend=""
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
		else:
			total_work_hrs=0
			next_total_work_hrs =0
			
		if not start_work:
			total= 0.0
			
		else:
		
			if next_day and next_day==1:
				total= next_total_hrs
				total_work_hrs=next_total_work_hrs
			else:

				total= total_ho
				total_work_hrs=total_work_hrs


		total_all +=total
		total_l+=total_work_hrs



	compensatory_total_hours= get_compensatory(employee, start_date, end_date)
	permission_total_hours= get_permissions(employee, start_date, end_date)


	#if total_hrs > total_real_hrs : total_hrs= total_real_hrs



	total_work_hrss = total_work_hrss
	disc=0
	total_all = total_all + compensatory_total_hours - permission_total_hours
	if  float(total_all) < float(total_l):
		disc = float(total_l)- float(total_all) 

	if total_all <= 0: 
		total_all = 0.0


	if disc < 0.0 : disc = 0.0
	return total_l , disc ,total_all, compensatory_total_hours, permission_total_hours
			

