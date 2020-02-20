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
		 {"label":_("Employee") ,"width":100,"fieldtype": "link","options":"Employee"},
		 {"label":_("Employee Name") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Identity No") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Gender") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Marital Status") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Nationality") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Governorate") ,"width":100,"fieldtype": "Data"},
		 {"label":_("City") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Religion") ,"width":100,"fieldtype": "Data"},

		 {"label":_("Designation") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Branch") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Management") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Circle") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Sub Departement") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Departement") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Employment Type") ,"width":100,"fieldtype": "Data"},

		 {"label":_("Date Of Joining") ,"width":100,"fieldtype": "Date"},
		 {"label":_("Contract End Date") ,"width":100,"fieldtype": "Date"},
		
		 ]
	
	return columns

def salaries(conditions, filters):
	data=[]
	hours={}
	ss  = frappe.db.sql("""select emp.employee_name ,pd.*, ed.* ,cd.* ,ed.employee as emm from `tabEmployee` as emp join `tabEmployee Employment Detail` as ed on emp.name=ed.employee
	 					left Join `tabEmployee Contact Details` as cd on emp.name=cd.employee 
	 					left join `tabEmployee Personal Detail` as pd on  emp.name=pd.employee where emp.docstatus <2 %s 
						order by emp.employee """ %
		conditions, filters, as_dict=1)


	for add in ss:
		data.append([add.emm,add.employee_name,add.identity_no ,add.gender,add.marital_status,add.nationality ,
			add.governorate,add.city,add.religion ,
			add.designation,add.branch,add.management,add.circle,add.sub_dep,add.department,add.employment_type,add.date_of_joining,add.contract_end_date])
	
	return data


def get_conditions(filters):
	conditions = ""

	if filters.get("employee"): conditions += " and emp.employee = %(employee)s"
	if filters.get("department"): conditions += " and ed.department_list = %(department)s"
	if filters.get("designation"): conditions += " and ed.designation = %(designation)s"
	if filters.get("branch"): conditions += " and ed.branch = %(branch)s"
	if filters.get("management"): conditions += " and ed.management = %(management)s"
	if filters.get("circle"): conditions += " and ed.circle = %(circle)s"
	if filters.get("sub_departement"): conditions += " and ed.sub_departement = %(sub_departement)s"
	if filters.get("employment_type"): conditions += " and ed.employment_type = %(employment_type)s"

	if filters.get("gender"): conditions += " and pd.gender = %(gender)s"
	if filters.get("marital_status"): conditions += " and pd.marital_status = %(marital_status)s"
	if filters.get("nationality"): conditions += " and pd.nationality = %(nationality)s"
	if filters.get("governorate"): conditions += " and pd.governorate = %(governorate)s"
	if filters.get("city"): conditions += " and pd.city = %(city)s"




	return conditions, filters
