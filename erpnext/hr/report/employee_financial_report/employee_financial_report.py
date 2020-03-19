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
		row =[emp.employee,emp.employee_name,emp.salary_structure,emp.basic_salary,emp.total_working_days,emp.day_salary,emp.hour_cost,emp.total_working_hours,emp.over_hrs,emp.total_overtime]
		for e in earning_types:
			row.append(ss_earning_map.get(emp.name, {}).get(e))

		row += [emp.gross_pay]

		for d in ded_types:
			row.append(ss_ded_map.get(emp.name, {}).get(d))

		row += [emp.total_deduction, emp.net_pay]
		#row += [int(emp.basic_salary)+ int(emp.gross_pay)- int(emp.total_deduction)+int(emp.total_overtime)]
		row += [emp.designation,emp.bank_name,emp.bank_account_no,emp.branch,emp.department,emp.company]
			
		data.append(row)
		
	return columns, data

def get_columns(salary_slips):
	columns = [
		 {"label":_("Employee Number") ,"width":100,"fieldtype": "Link","options":"Employee"},
		 {"label":_("Employee Name") ,"width":150,"fieldtype": "Data"},
		 {"label":_("Salary Structure") ,"width":100,"fieldtype": "Link","options":"Salary Structure"},
		 {"label":_("Basic Salary") ,"width":80,"fieldtype": "Currency","options": "Company:company:default_currency"},
		 {"label":_("Work Days") ,"width":70,"fieldtype": "Data"},
		 {"label":_("Day Cost") ,"width":70,"fieldtype": "Currency","options": "Company:company:default_currency"},
		 {"label":_("Hour Cost") ,"width":70,"fieldtype": "Currency","options": "Company:company:default_currency"},
		 {"label":_("Overtime Cost") ,"width":80,"fieldtype": "Currency","options": "Company:company:default_currency"},
		 {"label":_("Overtime Working Hours") ,"width":80,"fieldtype": "Data"},
		 {"label":_("Total Overtime") ,"width":80,"fieldtype": "Currency","options": "Company:company:default_currency"}



	]

	salary_components = {_("Earning"): [], _("Deduction"): []}

	for component in frappe.db.sql("""select distinct sd.salary_component, sc.type
		from `tabSalary Detail` sd, `tabSalary Component` sc
		where sc.name=sd.salary_component and sd.amount != 0 and sd.parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1):
		salary_components[_(component.type)].append(component.salary_component)

	for e in salary_components[_("Earning")]:
		columns += [{"label":_(e) ,"width":80,"fieldtype": "Currency","options": "Company:company:default_currency"}]

	columns += [{"label":_("Gross Pay") ,"width":80,"fieldtype": "Currency","options": "Company:company:default_currency"}]

	for d in salary_components[_("Deduction")]:
		columns += [{"label":_(d) ,"width":80,"fieldtype": "Currency","options": "Company:company:default_currency"}]
	columns += [
	 	{"label":_("Total Deduction") ,"width":80,"fieldtype": "Currency","options": "Company:company:default_currency"},
	 	{"label":_("Net Pay(Total Salary)") ,"width":80,"fieldtype": "Currency","options": "Company:company:default_currency"}]

	#columns = columns + [(e + ":Currency:Company:company:default_currency:100") for e in salary_components[_("Earning")]] + \
		#[_("Gross Pay") + ":Currency:Company:company:default_currency:80"] + [(d + ":Currency:Company:company:default_currency:90") for d in salary_components[_("Deduction")]] + \
		#[_("Total Deduction") + ":Currency:Company:company:default_currency:100", _("Net Pay(Total Salary)") + ":Currency:Company:company:default_currency:100"]
	#columns += [{"label":_("Total") ,"width":90,"fieldtype": "Currency"}]

	columns += [
		 {"label":_("Designation") ,"width":80,"fieldtype": "Data"},
		 {"label":_("Bank") ,"width":80,"fieldtype": "Data"},
		 {"label":_("Bank Number") ,"width":80,"fieldtype": "Data"},
		 {"label":_("Branch") ,"width":80,"fieldtype": "Data"},
		 {"label":_("Department") ,"width":80,"fieldtype": "Data"},
		 {"label":_("Company") ,"width":80,"fieldtype": "Data"}
	]
	return columns, salary_components[_("Earning")], salary_components[_("Deduction")]



def get_conditions(filters):

	conditions = ""
	if filters.get("basic_salary") and not filters.get("basic_salary_to"): conditions += " and basic_salary = %(basic_salary)s"	
	if filters.get("basic_salary_to") and filters.get("basic_salary_to"): conditions += " and emp.basic_salary IN (select name from tabEmployee where basic_salary >= %(basic_salary)s and emp.basic_salary <= %(basic_salary_to)s)"

	if filters.get("employee") and not filters.get("employee"): conditions += " and sal.employee = %(employee)s"
	if filters.get("branch"): conditions += " and emp.branch = %(branch)s"
	if filters.get("bank"): conditions += " and emp.bank_name = %(bank)s"
	if filters.get("bank_account_no"): conditions += " and bank_account_no = %(bank_account_no)s"
	#if filters.get("management"): conditions += " and management = %(management)s"
	#if filters.get("circle"): conditions += " and circle = %(circle)s"
	if filters.get("department"): conditions += " and emp.department = %(department)s"
	#if filters.get("work_shift"): conditions += " and work_shift = %(work_shift)s"
	#if filters.get("city"): conditions += " and emp.city = %(city)s"
	#if filters.get("status"): conditions += " and emp.status = %(status)s"
	#if filters.get("governorate"): conditions += " and emp.governorate = %(governorate)s"
	#if filters.get("qualification"): conditions += " and edu.qualification = %(qualification)s"
	if filters.get("designation"): conditions += " and emp.designation = %(designation)s"
	if filters.get("from_date"): conditions += " and start_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and end_date <= %(to_date)s"
	if filters.get("company"): conditions += " and emp.company = %(company)s"

	return conditions, filters

def get_salary_slips(conditions, filters):
	salary_slips  = frappe.db.sql("""select sal.employee,sal.employee_name,emp.designation,emp.company,start_date,end_date,payment_days,salary_structure, emp.basic_salary,emp.bank_name,bank_account_no,gross_pay,total_deduction,total_working_days, net_pay,emp.day_salary,emp.hour_cost,total_working_hours,emp.over_hrs,total_overtime,emp.branch,emp.department from `tabEmployee` as emp left join `tabSalary Slip` as sal on emp.name=sal.employee where sal.docstatus = 1 %s  order by emp.name,start_date""" %
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


