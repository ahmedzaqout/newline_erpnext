# -*- coding: utf-8 -*-
# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import date 

def execute(filters=None):

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	data = get_results(conditions, filters)
	return columns, data


def get_columns(filters):
	columns = [
		 {"label":_("Job Opening") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Job Applicant") ,"width":80,"fieldtype": "Link","options":"Job Applicant"},
		 {"label":_("Applicant Name") ,"width":120,"fieldtype": "Data"},
 		 {"label":_("Age") ,"width":120,"fieldtype": "Int"},
		 {"label":_("Governorate") ,"width":80,"fieldtype": "Data"},
		 {"label":_("City") ,"width":80,"fieldtype": "Data"},
		 {"label":_("Diploma") ,"width":100,"fieldtype": "Data"},
		 {"label":_("BA") ,"width":100,"fieldtype": "Data"},
		 {"label":_("M.A.") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Ph.D.") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Graduation Year") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Experience Years") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Appropriate qualifications") ,"width":90,"fieldtype": "Int"},
		 {"label":_("Related Experience") ,"width":80,"fieldtype": "Int"},
		 {"label":_("Job Appropriateness") ,"width":80,"fieldtype": "Int"},
		 {"label":_("Training") ,"width":80,"fieldtype": "Int"},
		 {"label":_("Society Knowledge") ,"width":80,"fieldtype": "Int"},
		 {"label":_("Other Qualifications") ,"width":80,"fieldtype": "Int"},
		 {"label":_("Languages") ,"width":80,"fieldtype": "Int"},
		 {"label":_("Extent of computer") ,"width":80,"fieldtype": "Int"},
		 {"label":_("Personal") ,"width":80,"fieldtype": "Int"},
		 {"label":_("Appearance") ,"width":80,"fieldtype": "Int"},
		 {"label":_("Readiness") ,"width":80,"fieldtype": "Int"},
		 {"label":_("Total") ,"width":80,"fieldtype": "Int"},

]
	return columns

def get_results(conditions, filters):
	data=[]
	ss  = frappe.db.sql("""select distinct(job_applicant) ,job_opening,applicant_name from `tabInterview`  where docstatus <2 %s order by applicant_name """ %conditions, filters, as_dict=1)
	if filters.get("order_desc"):
		ss  = frappe.db.sql("""select distinct(job_applicant) ,job_opening,applicant_name from `tabInterview`  where docstatus <2 %s 
		order by average desc """ %
		conditions, filters, as_dict=1)
	technical=['ملائمة المؤهلات العلمية','خبرة متعلقة بهذا المجال','مدى الملائمة للوظيفة','التدريب','مدى المعرفة بالجمعية','مؤهلات أخرى','اللغات','مدى المعرفة بالكمبيوتر','الشخصية','المظهر','الجاهزية']
	for emp in ss:
		app = frappe.get_doc("Job Applicant" ,emp.job_applicant)
		row=[emp.job_opening,emp.job_applicant,emp.applicant_name]
		today = date.today() 
		age=0
		if app.date_of_birth:
			age = today.year - app.date_of_birth.year -((today.month, today.day) <  (app.date_of_birth.month, app.date_of_birth.day)) 
		row.append(age)

		if filters.get("age"):
			if int(age) != int(filters.get("age")):
				continue;
		row.append(app.governorate)
		row.append(app.city)
		qual=['دبلوم','بكالوريوس','ماجستير','دكتوراة']
		grad=[]
		ff=False
		if filters.get("qualification"):
			ff=True

		for q in qual:
			dd= frappe.db.sql("""select ed.* from `tabEmployee Education` as ed where ed.docstatus <2 
				and ed.parent= '{0}' and ed.parenttype ='Job Applicant' and ed.qualification = '{1}' """.format(app.name,q), as_dict=1)
			if dd  and dd[0]:
				 row.append(dd[0].college)
				 grad.append(dd[0].year_of_passing)
				 if filters.get("qualification"):
					 if(filters.get("qualification") == q):
					 	ff=False
			else:
				row.append("")

		if(ff):
			continue;

		if len(grad) >0:
			row.append(max(grad))
		else:
			row.append("")


		row.append(app.experience_years)

		tott=0
		cc=0
		for mm in technical:
			dd= frappe.db.sql("""select td.degree as degree_total from `tabTrial Period Evaluation Details` as td join `tabInterview` as inter on td.parent = inter.name  where inter.docstatus = 1 and inter.job_applicant = '{0}' and td.quantification = '{1}' """.format(emp.job_applicant,mm), as_dict=1)
			if dd:	
				if dd[0].degree_total:		
					reaa = dd[0].degree_total
					tott += dd[0].degree_total
				else:
					reaa = 0
					tott += 0
			
			else:
				reaa = 0
				tott += 0
			
			cc+=1
				
			
			row.append(reaa)
		row.append(float(tott)/float(cc))
		if filters.get("experience_years") and app.experience_years != filters.get("experience_years"):
			continue;
		
		if filters.get("city") and app.city != filters.get("city"):
			continue;
		if filters.get("governorate") and app.governorate != filters.get("governorate"):
			continue;


		
		data.append(row)
		
	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("job_opening"): conditions += " and job_opening = %(job_opening)s"
	if filters.get("job_applicant"): conditions += " and job_applicant = %(job_applicant)s"
	return conditions, filters

