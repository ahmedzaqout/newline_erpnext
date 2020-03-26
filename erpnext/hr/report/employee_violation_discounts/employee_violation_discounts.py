# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _


def execute(filters=None):
	columns, data = [], []
	if not filters: 
		filters = {}

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	data = get_data(conditions, filters,data)
	return columns, data



def get_columns(filters):
	columns = [
		 {"label":_("Employee Name") ,"width":150,"fieldtype": "Data"},
 		 {"label":_("Department") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Warning Date") ,"width":100,"fieldtype": "Date"},
		 {"label":_("Violation") ,"width":160,"fieldtype": "Data"},
		 {"label":_("Discount Value") ,"width":100,"fieldtype": "Float"},
		 {"label":_("Salary Slip") ,"width":160,"fieldtype": "Data"}

	]
	return columns


def get_data(conditions, filters, data):
	warn_data= frappe.db.sql("""select slip.name as slipname,slip.employee,slip.designation,slip.employee_name,slip.department, \
		slip.start_date,slip.end_date, warn.employee_violation,warn.discount_hour,warn.warning_date from `tabSalary Slip` as slip join `tabSalary Slip Warning Information` as warn \
		on slip.name= warn.parent %s order by slip.employee, slip.start_date""" %conditions, filters, as_dict=1)
	for warn in warn_data:
		if warn.employee_name:
			row = [warn.employee_name, warn.department,warn.warning_date,warn.employee_violation,warn.discount_hour, warn.slipname]
			data.append(row)
	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("employee"): conditions += " slip.employee = %(employee)s"
	if filters.get("designation"): conditions += " and slip.designation = %(designation)s"
	if filters.get("department"): conditions += " and slip.department = %(department)s"
	if filters.get("from_date"): conditions += " and slip.start_date <= %(from_date)s"
	if filters.get("to_date"): conditions += " and slip.end_date >= %(to_date)s"

	return conditions, filters
