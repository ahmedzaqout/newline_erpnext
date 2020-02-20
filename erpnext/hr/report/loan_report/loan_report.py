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
		 {"label":_("Employee Name") ,"width":100,"fieldtype": "link","options":"Employee"},
		 {"label":_("Loan Type") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Loan Amount") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Loan Amount Shekel") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Disbursememt Date") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Repayment Method") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Ratio") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Repayment Period In Days") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Repayment Period In Month") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Repayment Period In Year") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Daily Repayment amount ") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Monthly Repayment amount") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Yearly Repayment amount") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Mode Of Payment") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Total Payment") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Total Interest Payment") ,"width":100,"fieldtype": "Data"},
]

	return columns

def salaries(conditions, filters):
	data=[]
	ss  = frappe.db.sql("""select em.employee_name,ed.*,l.* from `tabEmployee Loan` as l left  join `tabEmployee` as em  on em.employee = l.employee left Join `tabEmployee Employment Detail` as ed on em.employee=ed.employee  where l.docstatus <2 %s 
		order by l.employee """ %
		conditions, filters, as_dict=1)

	for emp in ss:
		row=[emp.employee,emp.loan_type,emp.loan_amount,emp.loan_amount_sh,emp.disbursement_date,emp.repayment_method, emp.ratio,emp.repayment_period_in_days,emp.repayment_periods,emp.repayment_period_in_year,emp.daily_repayment_amount,emp.monthly_repayment_amount,emp.yearly_repayment_amount,
emp.mode_of_payment,emp.total_payment,emp.total_interest_payable]
		data.append(row)

	return data




def get_conditions(filters):
	conditions = ""
	if filters.get("employee"): conditions += " and ed.employee = %(employee)s"
	if filters.get("department"): conditions += " and ed.management = %(department)s"


	return conditions, filters
