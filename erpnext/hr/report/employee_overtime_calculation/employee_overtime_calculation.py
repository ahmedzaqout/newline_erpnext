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
	emp_map = get_employee_details()

	data = []
	for emp in sorted(emp_map):
		if not emp:
			continue

		row = [emp, emp.employee_name, emp.department, emp.start_date,emp.end_date,emp.total_hours]

		data.append(row)

	return columns, data


def get_columns(filters):
	columns = [
		_("Employee") + ":Link/Employee:100", _("Employee Name") + "::140", _("Department") + ":Link/Department:120",_("Start Date")+ ":Date:90", _("End Date")+ ":Date:90", _("Overtime Hours") + ":Float:100", _("Overtime Hours with labs") + ":Float:150"]
	

	return columns


def get_conditions(filters):

	conditions = " and start_date >= %(start_date)s and end_date <= %(end_date)s"

	if filters.get("company"): conditions += " and company = %(company)s"
	if filters.get("employee"): conditions += " and employee = %(employee)s"

	return conditions, filters

def get_employee_details():
	return frappe.db.sql("""select tsh.name, tsh.employee_name, designation, management, tsh.company,start_date,end_date,round(total_hours,2) as total_hours from tabEmployee as emp join tabTimesheet as tsh on emp.employee=tsh.employee """, as_dict=1)


