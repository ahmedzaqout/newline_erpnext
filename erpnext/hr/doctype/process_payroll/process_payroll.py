# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from dateutil.relativedelta import relativedelta
from frappe.utils import cint, flt, nowdate, add_days, getdate, fmt_money, add_to_date, DATE_FORMAT
from frappe import _
from erpnext.accounts.utils import get_fiscal_year

from frappe.model.document import Document

class ProcessPayroll(Document):
	def get_emp_list(self):
		"""
			Returns list of active employees based on selected criteria
			and for which salary structure exists
		"""
		cond = self.get_filter_condition()
		cond += self.get_joining_releiving_condition()


		condition = ''
		if self.payroll_frequency:
			condition = """and payroll_frequency = '%(payroll_frequency)s'""" % {"payroll_frequency": self.payroll_frequency}

		sal_struct = frappe.db.sql("""
				select
					name from `tabSalary Structure`
				where
					docstatus != 2 and
					is_active = 'Yes'
					and company = %(company)s 
					{condition}""".format(condition=condition),
				{"company": self.company})

		if sal_struct:
			cond += "and t2.parent IN %(sal_struct)s "
			emp_list = frappe.db.sql("""
				select
					t1.name
				from
					`tabEmployee` t1, `tabSalary Structure Employee` t2
				where
					t1.docstatus!=2
					and t1.name = t2.employee
			%s """% cond, {"sal_struct": sal_struct})
			return emp_list

	def get_filter_condition(self):
		self.check_mandatory()

		cond = ''
		if self.get('company'):
			cond += " and t1.company = '" + self.get('company').replace("'", "\'") + "'"

		return cond

	def get_joining_releiving_condition(self):
		cond = """
			and ifnull(t1.date_of_joining, '0000-00-00') <= '%(end_date)s'
			and ifnull(t1.relieving_date, '2199-12-31') >= '%(start_date)s'
		""" % {"start_date": self.start_date, "end_date": self.end_date}
		return cond

	def check_mandatory(self):
		for fieldname in ['company', 'start_date', 'end_date']:
			if not self.get(fieldname):
				frappe.throw(_("Please set {0}").format(self.meta.get_label(fieldname)))

	def create_salary_slips(self):
		"""
			Creates salary slip for selected employees if already not created
		"""
		self.check_permission('write')

		emp_list = self.get_emp_list()
		ss_list = []
		if emp_list:
			for emp in emp_list:
				if not frappe.db.sql("""select
						name from `tabSalary Slip`
					where
						docstatus!= 2 and
						employee = %s and
						start_date >= %s and
						end_date <= %s and
						company = %s
						""", (emp[0], self.start_date, self.end_date, self.company)):
					r=frappe.get_doc('Employee Salary Detail', emp[0])
					if r:
						ss = frappe.get_doc({
							"doctype": "Salary Slip",
							"payroll_frequency": self.payroll_frequency,
							"start_date": self.start_date,
							"end_date": self.end_date,
							"employee": emp[0],
							"employee_name": frappe.get_value("Employee", {"name":emp[0]}, "employee_name"),
							"company": self.company,
							"posting_date": self.posting_date,
							"basic_salary": r.basic_salary,
							"hour_rate": r.over_hrs,
							"bank_name": r.bank_name,
							"bank_account_no": r.bank_ac_no,
							"payroll_frequency": r.payroll_frequency,
							"total_overtime" : 0.0
					})
						ss.insert()
						ss_dict = {}
						ss_dict["Employee Name"] = ss.employee_name
						ss_dict["Total Pay"] = fmt_money(ss.rounded_total,currency = frappe.defaults.get_global_default("currency"))
						ss_dict["Salary Slip"] = self.format_as_links(ss.name)[0]
						ss_list.append(ss_dict)
		return self.create_log(ss_list)

	def create_log(self, ss_list):
		if not ss_list or len(ss_list) < 1: 
			log = "<p>" + _("No employee for the above selected criteria OR salary slip already created") + "</p>"
		else:
			log = frappe.render_template("templates/includes/salary_slip_log.html",
						dict(ss_list=ss_list,
							keys=sorted(ss_list[0].keys()),
							title=_('Created Salary Slips')))
		return log

	def get_sal_slip_list(self, ss_status, as_dict=False):
		"""
			Returns list of salary slips based on selected criteria
		"""
		cond = self.get_filter_condition()

		ss_list = frappe.db.sql("""
			select t1.name, t1.salary_structure from `tabSalary Slip` t1
			where t1.docstatus = %s and t1.start_date >= %s and t1.end_date <= %s
			and (t1.journal_entry is null or t1.journal_entry = "")  %s
		""" % ('%s', '%s', '%s', cond), (ss_status, self.start_date, self.end_date), as_dict=as_dict)
		return ss_list

	def submit_salary_slips(self):
		"""
			Submit all salary slips based on selected criteria
		"""
		self.check_permission('write')
		jv_name = ""
		ss_list = self.get_sal_slip_list(ss_status=0)
		submitted_ss = []
		not_submitted_ss = []
		for ss in ss_list:
			ss_obj = frappe.get_doc("Salary Slip",ss[0])
			ss_dict = {}
			ss_dict["Employee Name"] = ss_obj.employee_name
			ss_dict["Total Pay"] = fmt_money(ss_obj.net_pay,
				currency = frappe.defaults.get_global_default("currency"))	
			ss_dict["Salary Slip"] = self.format_as_links(ss_obj.name)[0]
			
			if ss_obj.net_pay<0:
				not_submitted_ss.append(ss_dict)
			else:
				try:
					ss_obj.submit()
					submitted_ss.append(ss_dict)
				except frappe.ValidationError:
					not_submitted_ss.append(ss_dict)
			

		return self.create_submit_log(submitted_ss, not_submitted_ss, jv_name)

	def create_submit_log(self, submitted_ss, not_submitted_ss, jv_name):
		log = ''
		if not submitted_ss and not not_submitted_ss:
			log = "No salary slip found to submit for the above selected criteria"

		if submitted_ss:
			log = frappe.render_template("templates/includes/salary_slip_log.html",
					dict(ss_list=submitted_ss,
						keys=sorted(submitted_ss[0].keys()),
						title=_('Submitted Salary Slips')))
			if jv_name:
				log += "<b>" + _("Accural Journal Entry Submitted") + "</b>\
					%s" % '<br>''<a href="#Form/Journal Entry/{0}">{0}</a>'.format(jv_name)			

		if not_submitted_ss:
			log += frappe.render_template("templates/includes/salary_slip_log.html",
					dict(ss_list=not_submitted_ss,
						keys=sorted(not_submitted_ss[0].keys()),
						title=_('Not Submitted Salary Slips')))
			log += """
				Possible reasons: <br>\
				1. Net pay is less than 0 <br>
				2. Company Email Address specified in employee master is not valid. <br>
				"""
		return log

	def format_as_links(self, salary_slip):
		return ['<a href="#Form/Salary Slip/{0}">{0}</a>'.format(salary_slip)]

	def get_loan_details(self):
		"""
			Get loan details from submitted salary slip based on selected criteria
		"""
		cond = self.get_filter_condition()
		return frappe.db.sql(""" select eld.employee_loan_account,
				eld.interest_income_account, eld.principal_amount, eld.interest_amount, eld.total_payment
			from
				`tabSalary Slip` t1, `tabSalary Slip Loan` eld
			where
				t1.docstatus = 1 and t1.name = eld.parent and start_date >= %s and end_date <= %s %s
			""" % ('%s', '%s', cond), (self.start_date, self.end_date), as_dict=True) or []

	def get_total_salary_amount(self):
		"""
			Get total salary amount from submitted salary slip based on selected criteria
		"""
		cond = self.get_filter_condition()
		totals = frappe.db.sql(""" select sum(rounded_total) as rounded_total from `tabSalary Slip` t1
			where t1.docstatus = 1 and start_date >= %s and end_date <= %s %s
			""" % ('%s', '%s', cond), (self.start_date, self.end_date), as_dict=True)
		return totals and totals[0] or None

	def get_salary_component_account(self, salary_component):
		account = frappe.db.get_value("Salary Component Account",
			{"parent": salary_component, "company": self.company}, "default_account")

		if not account:
			frappe.throw(_("Please set default account in Salary Component {0}")
				.format(salary_component))

		return account

	def get_salary_components(self, component_type):
		salary_slips = self.get_sal_slip_list(ss_status = 1, as_dict = True)
		if salary_slips:
			salary_components = frappe.db.sql("""select salary_component, amount, parentfield
				from `tabSalary Detail` where parentfield = '%s' and parent in (%s)""" %
				(component_type, ', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=True)
			return salary_components

	
	

	def set_start_end_dates(self):
		self.update(get_start_end_dates(self.payroll_frequency, 
			self.start_date or self.posting_date, self.company))

@frappe.whitelist()
def get_start_end_dates(payroll_frequency, start_date=None, company=None):
	'''Returns dict of start and end dates for given payroll frequency based on start_date'''

	if payroll_frequency == "Monthly" or payroll_frequency == "Bimonthly" or payroll_frequency == "":
		fiscal_year = get_fiscal_year(start_date, company=company)[0]
		month = "%02d" % getdate(start_date).month
		m = get_month_details(fiscal_year, month)
		if payroll_frequency == "Bimonthly":
			if getdate(start_date).day <= 15:
				start_date = m['month_start_date']
				end_date = m['month_mid_end_date']
			else:
				start_date = m['month_mid_start_date']
				end_date = m['month_end_date']
		else:
			start_date = m['month_start_date']
			end_date = m['month_end_date']

	if payroll_frequency == "Weekly":
		end_date = add_days(start_date, 6)

	if payroll_frequency == "Fortnightly":
		end_date = add_days(start_date, 13)

	if payroll_frequency == "Daily":
		end_date = start_date

	return frappe._dict({
		'start_date': start_date, 'end_date': end_date
	})

def get_frequency_kwargs(frequency_name):
	frequency_dict = {
		'monthly': {'months': 1},
		'fortnightly': {'days': 14},
		'weekly': {'days': 7},
		'daily': {'days': 1}
	}
	return frequency_dict.get(frequency_name)

@frappe.whitelist()
def get_end_date(start_date, frequency):
	start_date = getdate(start_date)
	frequency = frequency.lower() if frequency else 'monthly'
	kwargs = get_frequency_kwargs(frequency) if frequency != 'bimonthly' else get_frequency_kwargs('monthly')

	# weekly, fortnightly and daily intervals have fixed days so no problems
	end_date = add_to_date(start_date, **kwargs) - relativedelta(days=1)
	if frequency != 'bimonthly':
		return dict(end_date=end_date.strftime(DATE_FORMAT))

	else:
		return dict(end_date='')

def get_month_details(year, month):
	ysd = frappe.db.get_value("Fiscal Year", year, "year_start_date")
	if ysd:
		from dateutil.relativedelta import relativedelta
		import calendar, datetime
		diff_mnt = cint(month)-cint(ysd.month)
		if diff_mnt<0:
			diff_mnt = 12-int(ysd.month)+cint(month)
		msd = ysd + relativedelta(months=diff_mnt) # month start date
		month_days = cint(calendar.monthrange(cint(msd.year) ,cint(month))[1]) # days in month
		mid_start = datetime.date(msd.year, cint(month), 16) # month mid start date
		mid_end = datetime.date(msd.year, cint(month), 15) # month mid end date
		med = datetime.date(msd.year, cint(month), month_days) # month end date
		return frappe._dict({
			'year': msd.year,
			'month_start_date': msd,
			'month_end_date': med,
			'month_mid_start_date': mid_start,
			'month_mid_end_date': mid_end,
			'month_days': month_days
		})
	else:
		frappe.throw(_("Fiscal Year {0} not found").format(year))
