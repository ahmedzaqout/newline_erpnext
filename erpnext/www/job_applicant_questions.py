# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
import frappe.utils
import json
from frappe import _


no_cache = True

@frappe.whitelist()
def get_context(context):

	data= frappe.local.form_dict
	context["job_title"] = data['job_title']
	context["job_applicant"] = data['job_applicant']
	app = frappe.db.sql("""select
		name ,applicant_name 
		from `tabJob Applicant`
		where name=%s """, (data['job_applicant']), as_dict=1) or []
	job =frappe.db.sql("""select
		name, department,quiz_time ,questions_no,has_quiz
		from `tabJob Opening`
		where name=%s
			""", (data['job_title']), as_dict=1) or []


	questions = frappe.db.sql("""select
		question,answer1,answer2,answer3,answer4,name ,image
		from `tabInterview Question`
		where question_type=%s  order by RAND() limit %s""", (job[0]['department'],job[0]['questions_no']), as_dict=1) or []
	context["questions"] = questions
	context["quiz_time"] = job[0]['quiz_time']
	context["app"] = app[0]['applicant_name']
	context["quiz"] = job[0]['has_quiz']
	
	#questions = frappe.get_list("Interview Question",['question','answer1','answer2','answer3','answer4','name'],  	filters={'question_type':job.department})

	context.no_header = True
	context.for_test = 'job_applicant_questions.html'
	kwargs=frappe._dict(kwargs)
	context["title"] = "Job Application Question"
	context["doc"] = frappe.as_json(job)
	context["data"] = job[0].name
	
	return context


