# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns()
	data = get_employees(filters)

	return columns, data

def get_columns():
	return [
		_("Employee") + ":Link/Employee:120", _("Name") + ":Data:200", _("Date of Birth")+ ":Date:100",
		_("Branch") + ":Link/Branch:120", _("Department") + ":Link/Department:120",
		_("Designation") + ":Link/Designation:120", _("Gender") + "::60"
	]

def get_employees(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql("""select e.name, e.employee_name, pd.date_of_birth,
	ed.branch, ed.management, ed.designation,
	pd.gender from tabEmployee  as e left join `tabEmployee Employment Detail` as ed on e.employee=ed.employee left join `tabEmployee Personal Detail` as pd  on e.employee=pd.employee where ed.status = 'Active' %s""" % conditions, as_list=1)

def get_conditions(filters):
	conditions = ""
	if filters.get("month"):
		month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
			"Dec"].index(filters["month"]) + 1
		conditions += " and month(pd.date_of_birth) = '%s'" % month




	return conditions
