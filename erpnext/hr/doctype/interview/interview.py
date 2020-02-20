# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class Interview(Document):
	def validate(self):
		en=[]
		if not self.is_new():
			self.is_recommended= 1
		

		
		
	def on_submit(self):
		job_app = frappe.get_doc("Job Applicant" ,self.job_applicant)
		if self.status:
			job_app.status= self.status
			job_app.flags.ignore_permissions=True
			job_app.save()		

		technical=['ملائمة المؤهلات العلمية','خبرة متعلقة بهذا المجال','مدى الملائمة للوظيفة','التدريب','مدى المعرفة بالجمعية','مؤهلات أخرى','اللغات','مدى المعرفة بالكمبيوتر','الشخصية','المظهر','الجاهزية']
		result=frappe.get_list('Interviewer Result','name',filters={"job_opening":self.job_opening,"docstatus":["<",2]})
		rec=[]			
		for mm in technical:
			lis = frappe.get_list("Trial Period Evaluation Details" , ['degree'],filters={"quantification":mm,"parent":self.name})
			if lis and  lis[0]:
				rec.append(float(lis[0].degree))
			else:
  				rec.append(0)
		for i in range(len(rec),10):
			rec.append(0)
		
		if result and len(result)>0:
			result=frappe.get_doc('Interviewer Result',result[0].name)
			en=result.get("interviewers")
			
		else:
			result=frappe.get_doc({"doctype":"Interviewer Result",
						"job_opening":self.job_opening})
			en=[]
		en.append({
			"applicant": self.job_applicant ,
			"applicant_name" :self.applicant_name,
			"appropriate_qualifications": rec[0] ,
			"related_experience": rec[1] ,
			"job_appropriateness":  rec[2],
			"training":  rec[3],
			"society_knowledge": rec[4] ,
			"other_qualifications":  rec[5],
			"languages":  rec[6],
			"extent_of_computer":rec[7]  ,
			"personal":  rec[8],
			"appearance":  rec[9],
			"readiness":  rec[10],
			"total": self.average ,
		})
		result.set("interviewers",en)
		result.flags.ignore_permissions=True
		result.save()		

	def autoname(self):
		keys = filter(None, (self.job_applicant, self.job_opening))
		self.name = make_autoname('Interview/'+"-".join(keys) + '/.#####')
		#self.name = make_autoname('Interview/' +self.job_opening+'/'+self.job_applicant + '/.#####')

