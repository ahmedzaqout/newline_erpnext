# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _
from calendar import monthrange
from frappe.utils import flt, time_diff_in_hours, get_datetime, getdate, cint

def execute(filters=None):
	if not filters: filters = {}

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	perm_map = get_exit_permission_details(conditions, filters)

	data = []
	for perm in sorted(perm_map):
		row =[perm.employee_name,perm.supervisor,perm.department,perm.permission_type,perm.permission_date,perm.from_date,perm.to_date,perm.total,perm.reason]
		data.append(row)

	return columns, data

def get_columns(filters):
	columns = [
		 {"label":_("Employee Name") ,"width":140,"fieldtype": "Data"},
		 {"label":_("Supervisor") ,"width":140,"fieldtype": "Data"},
		 {"label":_("Department") ,"width":140,"fieldtype": "Data"},
		 {"label":_("Permission Type") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Permission Date") ,"width":100,"fieldtype": "Date"},
		 {"label":_("From") ,"width":90,"fieldtype": "Time"},
		 {"label":_("To") ,"width":90,"fieldtype": "Time"},
		 {"label":_("Total") ,"width":90,"fieldtype": "Float"},
		 {"label":_("Status") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Reason") ,"width":150,"fieldtype": "Data"}

	]
	return columns


def get_conditions(filters):
	conditions = ""
	if filters.get("employee"): conditions += " and ex.employee = %(employee)s"
	if filters.get("supervisor"): conditions += " and emp.supervisor = %(supervisor)s"
	if filters.get("department"): conditions += " and emp.department = %(department)s"
	if filters.get("from_date"): conditions += " and ex.permission_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and ex.permission_date <= %(to_date)s"
	if filters.get("permission_type"): conditions += " and ex.permission_type = %(permission_type)s"
	if filters.get("status") =='Open': 
		conditions += " and ex.docstatus = 0"
	elif filters.get("status") =='Approved': 
		conditions += " and ex.docstatus = 1"
	elif filters.get("status") =='Rejected': 
		conditions += " and ex.docstatus = 2"

	return conditions, filters

def get_exit_permission_details(conditions, filters):
	perm_map  = frappe.db.sql("""select emp.supervisor,emp.supervisor_name,emp.department, ex.employee, ex.employee_name,ex.permission_type,ex.permission_date,ex.from_date,ex.to_date,ex.reason,ex.status, GREATEST(round(TIMESTAMPDIFF(MINUTE,ex.from_date,ex.to_date)/60,2),0) as total from `tabExit permission` as ex left join `tabEmployee Employment Detail` as emp on ex.employee= emp.employee where ex.docstatus <2 %s order by ex.employee,ex.permission_date """ %
		conditions, filters, as_dict=1)
	
	return perm_map


