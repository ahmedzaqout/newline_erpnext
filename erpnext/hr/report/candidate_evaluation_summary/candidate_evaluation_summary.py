# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	if not filters: filters = {}
	conditions, filters = get_conditions(filters)
	train_data = get_data(conditions, filters)
	#eval_det= frappe.db.sql_list("select quantification, degree from `tabTrial Period Evaluation Details` where parent=%s", train_data['name'])
	columns = get_columns()

	for d in sorted(train_data):
		row =[ d.candidate_name, d.final_result ]
		data.append(row)
		
	return columns, data


def get_columns():
	columns= [
		 {"label":_("Candidate Name") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Technical Side") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Skills") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Others") ,"width":120,"fieldtype": "Data"}
	]
	#for e in eval_det:
	#	columns.append({"label":_(e.quantification) ,"width":100,"fieldtype": "Data"})
	
	columns+= [
		 {"label":_("Total") ,"width":80,"fieldtype": "Float"},
		 {"label":_("Recommendations") ,"width":80,"fieldtype": "Data"}
	]
	return columns


def get_conditions(filters):
	conditions = ""
	if filters.get("from_date"): conditions += " and posting_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and  posting_date <= %(to_date)s"
	if filters.get("company"): conditions += " and company = %(company)s"
	return conditions, filters


def get_data(conditions, filters): 
	return frappe.db.sql("""select name,posting_date,company,final_result,candidate_name  from `tabInterviewer Evaluation` where 1=1 %s """ %conditions, filters, as_dict=1)

