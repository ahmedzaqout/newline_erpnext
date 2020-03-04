# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from frappe import _
from frappe.utils import comma_and, validate_email_add

sender_field = "email_id"

class DuplicationError(frappe.ValidationError): pass

class JobApplicant(Document):
	def onload(self):
		offer_letter = frappe.get_all("Offer Letter", filters={"job_applicant": self.name})
		if offer_letter:
			self.get("__onload").offer_letter = offer_letter[0].name

	def autoname(self):
		keys = filter(None, (self.first_name,self.family_name, self.email_id, self.job_title))
		if not keys:
			frappe.throw(_("Name or Email is mandatory"), frappe.NameError)
		self.name = "-".join(keys)

	def validate(self):
		self.check_email_id_is_unique()
		self.check_identity_is_unique()
		if not self.company:
			self.company=frappe.defaults.get_global_default("company")
		if self.email_id:
			validate_email_add(self.email_id, True)

		if not self.applicant_name and self.email_id:
			guess = self.email_id.split('@')[0]
			self.applicant_name = ' '.join([p.capitalize() for p in guess.split('.')])

	def check_email_id_is_unique(self):
		if self.email_id:
			names = frappe.db.sql_list("""select name from `tabJob Applicant`
				where identity_no=%s and name!=%s and job_title=%s""", (self.identity_no, self.name, self.job_title))

			if names:
				frappe.throw(_("Identity No. must be unique, already exists for {0}").format(comma_and(names)), frappe.DuplicateEntryError)
	def check_identity_is_unique(self):
		if self.email_id:
			names = frappe.db.sql_list("""select name from `tabJob Applicant`
				where email_id=%s and name!=%s and job_title=%s""", (self.email_id, self.name, self.job_title))

			if names:
				frappe.throw(_("Email Address must be unique, already exists for {0}").format(comma_and(names)), frappe.DuplicateEntryError)


@frappe.whitelist(allow_guest=True)
def test_interview(**kwards):
	job_title= kwards['job_title']
	job_applicant= kwards['job_applicant']


	job_opening= frappe.get_doc("Job Opening" , job_title)
	applicant= frappe.get_doc("Job Applicant" , job_applicant)
	result=0
	re=[]
	if len(applicant.get("quiz"))>0:
		return  {"status":"repaited","re":re}
		
	for key in kwards:
		if key != "job_applicant" and key != "job_title" and key != "cmd":
			q = frappe.get_doc("Interview Question" , key)
			applicant.append("quiz",{	
					"question" : q.question,
					"answer1" : q.answer1,
					"answer2" : q.answer2,
					"answer3" : q.answer3,
					"answer4" : q.answer4,
					"solution" : kwards[key],	
	})
			if int(q.solution) == int(kwards[key]):
				result+=1
				re.append(q.solution)
				re.append(kwards[key])
	applicant.result=result
	
	if result >= job_opening.min_passing_score:
		applicant.result_status="Pass"
		applicant.flags.ignore_permission=True
		applicant.save(ignore_permissions=True)
		return {"status":"success","re":re}
	applicant.result_status="Fail"
	applicant.flags.ignore_permission=True
	applicant.save(ignore_permissions=True)

	return  {"status":"fail","re":re}

@frappe.whitelist()
def send_email(job_applicant, method):
    	if job_applicant:
		if job_applicant.email_id:
			email_args = {
				"recipients": [job_applicant.email_id],
				"message": "Job Application Test ",
				"subject": "Job Application Test Url : <a href='job_applicant_questions?job_applicant={0}&&job_title={1}'> here </a>".format(job_applicant.name,job_applicant.job_title),
				}
			enqueue(method=frappe.sendmail, queue='short', timeout=300, async=True, **email_args)




