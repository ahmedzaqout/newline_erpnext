# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _

def execute(filters=None):

	allawances=frappe.db.sql_list("select name from `tabSalary Component` where type='Earning' order by name asc")
	conditions, filters = get_conditions(filters)
	columns = get_columns(filters,allawances)

	data = salaries(conditions, filters,allawances)
	return columns, data


def get_columns(filters,allawances):
	columns = [
		 {"label":_("Employee ") ,"width":100,"fieldtype": "link","options":"Employee"},
		 {"label":_("Employee Name") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Designation") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Departement") ,"width":100,"fieldtype": "Data"}]
	for allawance in allawances:
		columns.append({"label":_(allawance) ,"width":100,"fieldtype": "Float"})
	columns.append({"label":_("Total Earning") ,"width":100,"fieldtype": "Float"})
	return columns

def salaries(conditions, filters,allawances):
	data=[]
	hours={}
	ss  = frappe.db.sql("""select ss.* ,ed.designation as des ,ed.management as mang from `tabSalary Slip` as ss left join `tabEmployee Employment Detail` as ed on ss.employee= ed.employee where ss.docstatus <2 %s 
		order by ss.employee """ %
		conditions, filters, as_dict=1)

	for emp in ss:
		row=[emp.employee,emp.employee_name,emp.des,emp.mang]
		totale=0

		for allawance in allawances:
			ee=frappe.get_list("Salary Detail",['amount'],filters= {"salary_component" : allawance,"parent": emp.name})
			if ee:
				row.append(ee[0].amount)
				totale+=ee[0].amount
			else:
				row.append(0)

		row.append(totale)

		data.append(row)


	return data




def get_conditions(filters):
	conditions = ""
	if filters.get("start_date"): conditions += " and ss.start_date >= %(start_date)s"
	if filters.get("end_date"): conditions += " and ss.end_date <= %(end_date)s"
	if filters.get("employee"): conditions += " and ss.employee = %(employee)s"
	if filters.get("department"): conditions += " and ed.management = %(department)s"

	return conditions, filters