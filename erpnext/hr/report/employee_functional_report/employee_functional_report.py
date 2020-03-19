# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _

def execute(filters=None):
	if not filters: filters = {}

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	emp_map = get_employee_details(conditions, filters)


	data = []
	for emp in emp_map:
		row =[emp.employee_number,emp.employee_name,emp.date_of_birth, emp.grade,emp.qualification, emp.specialization,emp.gender,emp.emp_city,emp.gov,emp.branch, emp.management, emp.circle,emp.department, emp.work_shift,emp.emp_status]
			
		data.append(row)

	return columns, data

def get_columns(filters):
	columns = [
		 {"label":_("Employee Number") ,"width":90,"fieldtype": "Link","options":"Employee"},
		 {"label":_("Employee Name") ,"width":150,"fieldtype": "Data"},
		 {"label":_("Date Of Birth") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Grade") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Qualification") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Specialization") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Gender") ,"width":90,"fieldtype": "Data"},
		 {"label":_("City") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Branch") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Management") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Circle") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Work Shift") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Status") ,"width":80,"fieldtype": "Data"}

	]
	return columns


def get_conditions(filters):

	conditions = ""
	
	if filters.get("employee"): conditions += " and emp.name = %(employee)s"
	if filters.get("branch"): conditions += " and emp.branch = %(branch)s"
	if filters.get("management"): conditions += " and emp.management = %(management)s"
	if filters.get("circle"): conditions += " and  emp.circle = %(circle)s"
	if filters.get("work_shift"): conditions += " and emp.work_shift = %(work_shift)s"
	if filters.get("date_of_birth"): conditions += " and emp.date_of_birth = %(date_of_birth)s"
	if filters.get("gender"): conditions += " and emp.gender = %(gender)s"
	if filters.get("city"): conditions += " and emp.city = %(city)s"
	if filters.get("qualification"): conditions += " and edu.qualification = %(qualification)s"
	if filters.get("specialization"): conditions += " and edu.specialization = %(specialization)s"



	return conditions, filters

def get_employee_details(conditions, filters):
	emp_map  = frappe.db.sql("""select emp.name as employee_number, emp.employee_name,emp.status as emp_status,\
	 emp.branch,emp.management,emp.circle,emp.work_shift,ifnull(emp.date_of_birth,'') , \
	 emp.gender ,emp.city as emp_city,edu.qualification,edu.specialization, edu.name from tabEmployee as emp  left join `tabEmployee Education` as edu on emp.name=edu.employee where emp.docstatus < 2 %s  order by emp.name""" %
		conditions, filters, as_dict=1)

	return emp_map



