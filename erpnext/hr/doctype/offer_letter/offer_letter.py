# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe import msgprint, _
from frappe.utils.background_jobs import enqueue
from frappe.model.naming import make_autoname
from frappe.core.doctype.sms_settings.sms_settings import send_sms


class OfferLetter(Document):
	def autoname(self):
		#keys = filter(None, ((self.job_applicant).strip(), (self.job_opening).strip()))
		keys = filter(None, ( (self.job_number).strip()))
		self.name = make_autoname('OfferLetter_'+keys + '/.#####')
		#self.name = make_autoname('Offer Letter/' +self.job_opening+'/'+self.job_applicant + '/.#####')

	def validate(self):
		self.validate_duplicate()

	def validate_duplicate(self):
		duplicate = frappe.db.get_value("Offer Letter",
			filters = {
				"job_applicant": self.job_applicant,
				"job_number": self.job_number,
				"name": ["!=", self.name]
			}
		)
		if duplicate:
			frappe.throw(_("Duplicate Offer Letter of job number {0} for employee {1}").format(self.job_number,self.applicant_name))	


	def on_submit(self):
		if self.status == 'Accepted':
			self.email_offer_letter()
			if self.company == 'Nawa':
				self.send_offer_sms()
			

	def send_offer_sms(self):
		doc = frappe.db.get_value("Job Applicant",self.job_applicant, ["name","phone_number"] , as_dict=1)
	    	if doc:
	        	if doc.phone_number:
	        	    context = {"doc": doc, "alert": doc, "comments": 'test'}
	        	    messages = _("You have been accepted for the job {0}").format(self.job_opening)
	        	    messages = frappe.render_template(messages, context)
	        	    number = [doc.phone_number]
	        	    #send_sms(number,messages)
	        	else:
	        	    frappe.msgprint(_("{0} Has no mobile number to send offer letter SMS").format(self.job_applicant) , alert=True)


	def email_offer_letter(self):
		receiver = frappe.db.get_value("Job Applicant", self.job_applicant, "email_id" ,as_dict=1)
		mr_list = []
		if receiver:
			#msg = frappe.render_template("templates/emails/employee_offer_letter.html", {"mr_list": mr_list})
			email_args = {
				"recipients": [receiver.email_id],
				#"message": msg, #_("Please see attachment"),
				"template":'employee_offer_letter',
				"args":mr_list,
				"subject": 'Offer Letter - {0}'.format(self.offer_date),
				"attachments": [frappe.attach_print(self.doctype, self.name, file_name=self.name)],
				"reference_doctype": self.doctype,
				"reference_name": self.name
				}
			enqueue(method=frappe.sendmail, queue='short', timeout=300, async=True, **email_args)
		else:
			msgprint(_("{0}: Employee email not found, hence email not sent").format(self.applicant_name))


	def make_employees(self):
		emp= frappe.new_doc("Employee")
		emp.update({
			"employee_name": self.applicant_name,
			"date_of_joining":  self.offer_date,
			"designation": self.designation
		})
		emp.save(ignore_permissions=True)
		#employee_number = frappe.db.get_value("Employee", {'employee_name':self.applicant_name}, "name")
		frappe.db.set_value("Employee", emp.name, "employee_number", emp.name)
		from erpnext.hr.doctype.employee.employee import make_employee_docs	
		make_employee_docs(''.join(emp.name) )
		frappe.msgprint(_("Employee Added"))



@frappe.whitelist()
def make_employee(source_name, target_doc=None):
	def set_missing_values(source, target=None):
		global applicant_name, date_of_joining
		applicant_name = source.applicant_name
		date_of_joining = source.offer_date
		pass #target.personal_email = frappe.db.get_value("Job Applicant", source.job_applicant, "email_id")
	doc = get_mapped_doc("Offer Letter", source_name, {
			"Offer Letter": {
				"doctype": "Employee",
				"field_map": {
					"applicant_name": "employee_name",
					"offer_date": " date_of_joining",
					"designation": "designation"
					#"job_number": "name"
				}}
		}, target_doc, set_missing_values)

	employee_number = frappe.db.get_value("Employee", {'employee_name':applicant_name,'date_of_joining':date_of_joining}, "employee_number")
	#frappe.db.set_value("Employee", { "employee_name": applicant_name } ,"employee_number", applicant_name)
	from erpnext.hr.doctype.employee.employee import make_employee_docs	
	make_employee_docs(employee_number )
	frappe.msgprint(_("Employee Added"))
	return doc



