# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _

def execute(filters=None):
	if not filters: filters = {}

	conditions, filters = get_conditions(filters)
	#columns = get_columns(filters)
	salary_slips = get_salary_slips(conditions, filters)

	columns, earning_types, ded_types = get_columns(salary_slips)
	ss_earning_map = get_ss_earning_map(salary_slips)
	ss_ded_map = get_ss_ded_map(salary_slips)


	data = []
	for emp in sorted(salary_slips):
		row =[emp.employee_number,emp.employee_name,emp.basic_salary,emp.bank_name,emp.bank_branch,emp.hour_rate]
			

		for e in earning_types:
			row.append(ss_earning_map.get(emp.name, {}).get(e))

		row += [emp.gross_pay]

		for d in ded_types:
			row.append(ss_ded_map.get(emp.name, {}).get(d))

		row += [emp.total_deduction, emp.net_pay]
		row += [int(emp.basic_salary)+ int(emp.gross_pay)- int(emp.total_deduction)]
		data.append(row)

	return columns, data

def get_columns(salary_slips):
	columns = [
		 {"label":_("Employee Number") ,"width":120,"fieldtype": "Link","options":"Employee"},
		 {"label":_("Employee Name") ,"width":150,"fieldtype": "Data"},
		 {"label":_("Basic Salary") ,"width":90,"fieldtype": "Currency"},
		 #{"label":_("Earning") ,"width":90,"fieldtype": "Data"},
		 #{"label":_("Deduction") ,"width":90,"fieldtype": "Data"},
		 #{"label":_("Total") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Bank") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Bank Branch") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Work Days") ,"width":80,"fieldtype": "Currency"},
		 {"label":_("Day Cost") ,"width":80,"fieldtype": "Currency"},
		 {"label":_("Hour Cost") ,"width":80,"fieldtype": "Currency"},
		 {"label":_("Overtime Hours") ,"width":80,"fieldtype": "Currency"},
		 {"label":_("Overtime Cost") ,"width":80,"fieldtype": "Currency"}


	]

	salary_components = {_("Earning"): [], _("Deduction"): []}

	for component in frappe.db.sql("""select distinct sd.salary_component, sc.type
		from `tabSalary Detail` sd, `tabSalary Component` sc
		where sc.name=sd.salary_component and sd.amount != 0 and sd.parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1):
		salary_components[_(component.type)].append(component.salary_component)

	columns = columns + [(e + ":Currency:120") for e in salary_components[_("Earning")]] + \
		[_("Gross Pay") + ":Currency:120"] + [(d + ":Currency:120") for d in salary_components[_("Deduction")]] + \
		[_("Total Deduction") + ":Currency:120", _("Net Pay") + ":Currency:120"]

	columns += [{"label":_("Total") ,"width":90,"fieldtype": "Currency"}]
	return columns, salary_components[_("Earning")], salary_components[_("Deduction")]


def get_conditions(filters):

	conditions = ""
	if filters.get("basic_salary") and not filters.get("basic_salary_to"): conditions += " and basic_salary = %(basic_salary)s"	
	if filters.get("basic_salary_to") and filters.get("basic_salary_to"): conditions += " and basic_salary IN (select name from tabEmployee where basic_salary >= %(basic_salary)s and basic_salary <= %(basic_salary_to)s)"

	if filters.get("employee") and not filters.get("employee"): conditions += " and emp.name = %(employee)s"
	if filters.get("branch"): conditions += " and emp.emp.branch = %(branch)s"
	if filters.get("bank"): conditions += " and emp.bank_name = %(bank)s"
	if filters.get("bank_branch"): conditions += " and bank_branch = %(bank_branch)s"
	#if filters.get("management"): conditions += " and management = %(management)s"
	#if filters.get("circle"): conditions += " and circle = %(circle)s"
	if filters.get("department"): conditions += " and department = %(department)s"
	#if filters.get("work_shift"): conditions += " and work_shift = %(work_shift)s"
	if filters.get("date_of_birth"): conditions += " and date_of_birth = %(date_of_birth)s"
	if filters.get("gender"): conditions += " and gender = %(gender)s"
	if filters.get("grade"): conditions += " and grade = %(grade)s"
	#if filters.get("city"): conditions += " and emp.city = %(city)s"
	#if filters.get("status"): conditions += " and emp.status = %(status)s"
	#if filters.get("governorate"): conditions += " and emp.governorate = %(governorate)s"
	#if filters.get("qualification"): conditions += " and edu.qualification = %(qualification)s"
	#if filters.get("specialization"): conditions += " and edu.specialization = %(specialization)s"
	if filters.get("from_date"): conditions += " and start_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and end_date <= %(to_date)s"

	return conditions, filters

def get_salary_slips(conditions, filters):
	salary_slips  = frappe.db.sql("""select emp.name,emp.employee_name,employee_number,emp.status as emp_status,start_date,end_date,payment_days, basic_salary,emp.bank_name,bank_branch,gross_pay,total_deduction, net_pay,hour_rate, emp.branch,management,circle,emp.department,work_shift,ifnull(date_of_birth,'') ,gender,grade, emp.city as emp_city,emp.governorate as gov,edu.qualification,edu.specialization,final_confirmation_date, edu.name from tabEmployee as emp left join `tabEmployee Education` as edu  on emp.name=edu.employee left join `tabSalary Slip` as sal on emp.name=sal.employee where sal.docstatus = 1 %s  order by emp.name""" %
		conditions, filters, as_dict=1)

	if not salary_slips:
		frappe.throw(_("No salary slip found between {0} and {1}").format(
			filters.get("from_date"), filters.get("to_date")))	
	return salary_slips

def get_ss_earning_map(salary_slips):
	ss_earnings = frappe.db.sql("""select parent, salary_component, amount
		from `tabSalary Detail` where parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

	ss_earning_map = {}
	for d in ss_earnings:
		ss_earning_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, [])
		ss_earning_map[d.parent][d.salary_component] = flt(d.amount)

	return ss_earning_map

def get_ss_ded_map(salary_slips):
	ss_deductions = frappe.db.sql("""select parent, salary_component, amount
		from `tabSalary Detail` where parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

	ss_ded_map = {}
	for d in ss_deductions:
		ss_ded_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, [])
		ss_ded_map[d.parent][d.salary_component] = flt(d.amount)

	return ss_ded_map


