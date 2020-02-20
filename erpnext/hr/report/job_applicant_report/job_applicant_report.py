# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _

def execute(filters=None):

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)

	data = salaries(conditions, filters)
	

	return columns, data


def get_columns(filters):
	columns = [
		 {"label":_("Applicant Name") ,"width":150,"fieldtype": "Data"},
		 {"label":_("Email Address") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Status") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Job Opening") ,"width":120,"fieldtype": "Data"},
		
]

	return columns

def salaries(conditions, filters):
	data=[]
	ss  = frappe.db.sql("""select ja.* from `tabJob Applicant` as ja where ja.docstatus <2 %s 
		order by ja.applicant_name """ %
		conditions, filters, as_dict=1)

	for emp in ss:
		row=[emp.applicant_name,emp.email_id,emp.status,emp.job_title]
		data.append(row)
	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("job_opening"): conditions += " and ja.job_title = %(job_opening)s"
	if filters.get("status"): conditions += " and ja.status = %(status)s"

	return conditions, filters

