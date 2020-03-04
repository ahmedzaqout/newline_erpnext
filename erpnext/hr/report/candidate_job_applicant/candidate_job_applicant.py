# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _
import datetime
from datetime import date 


def execute(filters=None):

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)

	data = get_data(conditions, filters)
	
	return columns, data

def get_columns(filters):
	columns = [
		 {"label":_("Applicant Name") ,"width":150,"fieldtype": "Data"},
		 {"label":_("Job Opening") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Interview") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Email Address") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Age") ,"width":120,"fieldtype": "Int"},
		 {"label":_("Gender") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Diploma") ,"width":100,"fieldtype": "Data"},
		 {"label":_("BA") ,"width":100,"fieldtype": "Data"},
		 {"label":_("M.A.") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Ph.D.") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Degree") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Graduation Year") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Ex Designation") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Ex Work Place") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Ex Designation") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Ex Work Place") ,"width":100,"fieldtype": "Data"}, 
		 {"label":_("Ex Designation") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Ex Work Place") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Experience Years") ,"width":100,"fieldtype": "Data"},
		 {"label":_("City") ,"width":100,"fieldtype": "Data"},

	]
	return columns

def get_data(conditions, filters):
	data=[]
	ss  = frappe.db.sql("""select ja.* from `tabJob Applicant` as ja where ja.docstatus <2  %s 
		order by ja.applicant_name """ %
		conditions, filters, as_dict=1)
	
	

	for emp in ss:
		row=[emp.applicant_name]
		row.append(emp.job_title)
		inters = frappe.get_all("Interview",['name'] , filters={"job_applicant":emp.name , "job_opening":emp.job_title})
		route=""
		if inters:
			route = "<a href='#Form/Interview/"+inters[0].name+"'>Interview</a>"
		else:
			route = "<a href='#Form/Interview/جديد المقابلات 1'>New Interview</a>"

		row.append(route)

		row.append(emp.email_id)
		
		today = date.today() 
		age=0
		if emp.date_of_birth:
			age = today.year - emp.date_of_birth.year -((today.month, today.day) <  (emp.date_of_birth.month, emp.date_of_birth.day)) 
		row.append(age)
		row.append(emp.gender)


		if filters.get("age"):
			if int(age) != int(filters.get("age")):
				continue;

		qual=['دبلوم','بكالوريوس','ماجستير','دكتوراة']
		grad=[]
		ff=False
		if filters.get("qualification"):
			ff=True

		for q in qual:
			dd= frappe.db.sql("""select ed.* from `tabEmployee Education` as ed where ed.docstatus <2 
				and ed.parent= '{0}' and ed.parenttype ='Job Applicant' and ed.qualification = '{1}' """.format(emp.name,q), as_dict=1)
			
			if dd  and dd[0]:
				 row.append(dd[0].college)
				 grad.append(dd[0].year_of_passing)
				 if filters.get("qualification"):
					 if(filters.get("qualification") == q):
					 	ff=False
			else:
				row.append("")

		if(ff):
			continue

		if len(grad) >0:
			row.append(max(grad))
		else:
			row.append("")
		
		ex= frappe.db.sql("""select designation ,company_name from `tabEmployee External Work History` as ed where ed.docstatus <2 
				and ed.parent= '{0}' and ed.parenttype ='Job Applicant' """.format(emp.name), as_list=1)
		
		mmm=0
		for mmm in range(0, len(ex)):
			row.append(ex[mmm][0])
			row.append(ex[mmm][1])

		for s in range(len(ex), 3):
			row.append("")
			row.append("")
			


		row.append(emp.experience_years)
		row.append(emp.city)

		data.append(row)
	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("job_opening"): conditions += " and ja.job_title = %(job_opening)s"
	if filters.get("city"): conditions += " and ja.city = %(city)s"
	if filters.get("experience_years"): conditions += " and ja.experience_years = %(experience_years)s"
	if filters.get("gender"): conditions += " and ja.gender = %(gender)s"
	return conditions, filters

