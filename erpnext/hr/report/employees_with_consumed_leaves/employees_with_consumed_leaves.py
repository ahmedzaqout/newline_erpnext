# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _
from erpnext.hr.doctype.leave_application.leave_application \
	import get_leave_allocation_records, get_leave_balance_on, get_approved_leaves_for_period

def execute(filters=None):
	leaves=frappe.get_list("Leave Type",['name'])

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	data = salaries(conditions, filters,leaves)
	return columns, data


def get_columns(filters):
	columns = [
		 {"label":_("Employee") ,"width":100,"fieldtype": "link","options":"Employee"},
		 {"label":_("Employee Name") ,"width":120,"fieldtype": "link","options":"Employee"},
		 {"label":_("Designation") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Managment") ,"width":150,"fieldtype": "Data"},
		 {"label":_("leave Type") ,"width":150,"fieldtype": "Data"},

		 ]
		
	return columns

def salaries(conditions, filters,leaves):
	data=[]
	hours={}
	ss  = frappe.db.sql("""select * from `tabEmployee` where docstatus <2 %s order by name """ % conditions, filters, as_dict=1)
	for add in ss:
		for leave_type in leaves:

			# leaves taken
			leaves_taken = get_approved_leaves_for_period(add.name, leave_type.name,
				filters.from_date, filters.to_date)
			allocation_records = get_leave_allocation_records(filters.to_date, add.name).get(add.name, frappe._dict())
			allocation = allocation_records.get(leave_type.name, frappe._dict())

			# closing balance
			closing =  flt(allocation.total_leaves_allocated) - flt(leaves_taken)

			if closing<=0:
				row = [add.name, add.employee_name, add.department,add.designation,leave_type.name]
				if allocation.total_leaves_allocated >0 :
					data.append(row)
	
	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("employee"): conditions += " and name = %(employee)s"
	if filters.get("department"): conditions += " and department = %(department)s"
	if filters.get("designation"): conditions += " and designation = %(designation)s"

	return conditions, filters
