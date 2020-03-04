# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _

def execute(filters=None):
	data=[]
	if not filters: filters = {}
	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	sal_data = get_query(conditions, filters)
	for d in sorted(sal_data):
		row =[d.basic_salary_modified_date, d.employee, frappe.db.get_value("Employee", {'employee_number':d.employee}, "employee_name"),d.last_salary,d.basic_salary,d.diff]
		data.append(row)

	return columns, data


def get_columns(filters):
	columns = [
		 {"label":_("Modified Date") ,"width":80,"fieldtype": "Date"},
		 {"label":_("Employee Number") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Employee") ,"width":150,"fieldtype": "Data"},
		 {"label":_("Last Salary Value") ,"width":100,"fieldtype": "currency","options":"Company:company:default_currency"},
		 {"label":_("Basic Salary") ,"width":80,"fieldtype": "currency","options":"Company:company:default_currency"},
		 {"label":_("Difference") ,"width":70,"fieldtype": "currency","options":"Company:company:default_currency"}
	]
	return columns


def get_conditions(filters):
	conditions = ""
	if filters.get("modified_date"): conditions += " and basic_salary_modified_date = %(modified_date)s"
	if filters.get("year"): conditions += " and  year(basic_salary_modified_date) = %(year)s"
	if filters.get("employee"): conditions += " and emp.employee = %(employee)s" 
	if filters.get("company"): conditions += " and emp.company = %(company)s"
	#if filters.get("department"): conditions += " company = %(company)s"
	if filters.get("designation"): conditions += " and emp.designation = %(designation)s"
	return conditions, filters


def get_query(conditions, filters): 
	doc=frappe.db.sql("""select emp.basic_salary_modified_date, emp.basic_salary,emp.employee,det.designation,emp.company, last_salary, (basic_salary-last_salary) as diff from `tabEmployee Salary Detail` as emp left join `tabEmployee Employment Detail` as det on emp.employee= det.employee where det.status='Active' and basic_salary_modified_date IS NOT NULL and (basic_salary-last_salary) !=0 %s order by emp.basic_salary_modified_date """ %
		conditions, filters, as_dict=1)
	return doc



@frappe.whitelist()
def get_years():
	year_list = frappe.db.sql_list("""select distinct YEAR(basic_salary_modified_date) from `tabEmployee Salary Detail` ORDER BY YEAR(basic_salary_modified_date) DESC""")
	if not year_list:
		year_list = [getdate().year]

	return "\n".join(str(year) for year in year_list)

