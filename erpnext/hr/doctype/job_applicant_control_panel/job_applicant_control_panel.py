# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _
import datetime
from datetime import date 
from frappe.model.document import Document
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from frappe.utils.background_jobs import enqueue

class JobApplicantControlPanel(Document):
	def send_interview_sms(self):
		if self.applicant_name:
			doc = frappe.db.get_value("Job Applicant",self.applicant_name, ["name","phone_number"] , as_dict=1)
		    	if doc:
				if doc.email_id:
					email_args = {
						"recipients": [doc.email_id],
						"message": self.message,
						"subject": 'interview - {0}'.format(self.job_opening),
						}
					enqueue(method=frappe.sendmail, queue='short', timeout=300, async=True, **email_args)
				if doc.phone_number:
				    context = {"doc": doc, "alert": doc, "comments": 'test'}
				    messages = self.message
				    messages = frappe.render_template(messages, context)
				    number = [doc.phone_number]
				    send_sms(number,messages)
				    frappe.msgprint(_("SMS Sent for job Applicant {0}").format(self.applicant_name) , alert=True)
				else:
				    frappe.msgprint(_("{0} Has no mobile number to send interview SMS").format(self.job_applicant) , alert=True)
				


		else:
			frappe.msgprint(_("Please choose the job applicant you want to send message for.") ,alert=True)
	def change_status(self):
		if (not self.status) or (not self.job_opening): 
			frappe.throw(_("You have to specify the opening job and status"))
		conditions = ""
		if self.job_opening: conditions += " and ja.job_title = %(job_opening)s"
		if self.city: conditions += " and ja.city = %(city)s"
		if self.experience_years: conditions += " and ja.experience_years = %(experience_years)s"
		if self.gender: conditions += " and ja.gender = %(gender)s"
		if self.governorate: conditions += " and ja.governorate = %(governorate)s"
		data=[]
		filters={"job_opening": self.job_opening ,
			"city" :self.city , 
			"experience_years" :self.experience_years ,
			"gender" :self.experience_years ,
			"governorate" :self.governorate}
		ss  = frappe.db.sql("""select ja.* from `tabJob Applicant` as ja where ja.docstatus <2  %s 
			order by ja.applicant_name """ %
			conditions, filters, as_dict=1)
		
		
		count=0
		for emp in ss:	
			today = date.today() 
			age=0
			if emp.date_of_birth:
				age = today.year - emp.date_of_birth.year -((today.month, today.day) <  (emp.date_of_birth.month, emp.date_of_birth.day)) 
			


			if self.age:
				if int(age) < int(self.age):
					continue;

			qual=['دبلوم','بكالوريوس','ماجستير','دكتوراة']
			grad=[]
			ff=False
			if self.qualification:
				ff=True

			for q in qual:
				dd= frappe.db.sql("""select ed.* from `tabEmployee Education` as ed where ed.docstatus <2 
					and ed.parent= '{0}' and ed.parenttype ='Job Applicant' and ed.qualification = '{1}' """.format(emp.name,q), as_dict=1)
				
				if dd  and dd[0]:

					 grad.append(dd[0].year_of_passing)
					 if self.qualification:
						 if(self.qualification == q):
						 	ff=False
						 if self.grade > 0:
							 if float(self.grade) > float(dd[0].class_per):
								frappe.msgprint(""+self.grade)
								frappe.msgprint(""+dd[0].class_per)
							 	ff=True

				

			if(ff):
				continue

			if self.experience_years:
				if self.experience_years > emp.experience_years:
					continue;
				


			frappe.db.sql("""update `tabJob Applicant` as ja  set status ='{0}' where ja.name ='{1}'""".format(self.status,emp.name), as_dict=1)
			count +=1

		frappe.msgprint("The status form {0} job applicant is changed.".format(count) )
