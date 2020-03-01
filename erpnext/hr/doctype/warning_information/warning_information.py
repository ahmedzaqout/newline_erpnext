# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe , erpnext
from frappe.model.document import Document
from frappe.utils import now_datetime,add_days,nowdate, cstr,getdate
from frappe import _

class WarningInformation(Document):
	def on_submit(self):
		if self.warning_type =='Email':
			send_email(self.employee ,self.description, _('Employee Task Late Warning')) 

		if self.penalty_type == 'Separation':
			end_service_type = 'Separation'
		elif self.penalty_type == 'Stop working with no salary':
			end_service_type = 'Separation'

			doc = frappe.get_doc('Employee Ending Service  Details',{"employee":self.employee})
			if doc:
				doc.update({
					'type':end_service_type,
					'reason_of_separation':self.separation_reasons,
					'warning_date' : self.warning_date,
					'relieving_date' : self.warning_date
				})
				#doc.flags.ignore_validate = True
				#doc.flags.ignore_links = True
				doc.save(ignore_permissions=True)

		#if self.warning_type == 'Discount' :
		#	shift_hrs = get_emp_work_shift(self.employee)
		#	if self.penalty >= shift_hrs:
		#		update_att_status(emp.attname, emp.deptname,emp.name, emp.get("attendance_date"), emp.employee_name)

		#if frappe.db.get_value('Salary Slip',{"employee":self.employee}):
		#	doc = frappe.get_doc('Salary Slip',{"employee":self.employee})
		#if doc and self.discount_hour:
		#	doc.update({
		#		'deductions': [{
		##			'salary_component':_(self.employee_violation),
		#			'type':_('Deduction'),
		#			'amount': self.discount_hour
		#			}]
		#		})
		#	doc.flags.ignore_validate = True
		#	doc.flags.ignore_validate_update_after_submit = True 
		#	doc.save(ignore_permissions=True)


@frappe.whitelist()
def get_emp_penalty(employee,employee_violation,warning_date):
	return get_penalty_name(get_penalty_count(employee_violation,employee,warning_date))




@frappe.whitelist()
def check_employee_task():
	employees = frappe.get_all("Employee Personal Detail", fields=["employee_name","employee_number"],filters={'status':'Active'})
	date = add_days(nowdate(), days=-1)
	now = now_datetime()
	for emp in employees:
		emplyee_task = frappe.db.sql("""select name from `tabEmployee Task` where employee= %s  and posting_date =  %s""",(emp.employee_number,date) )
		if not emplyee_task:
			violations_count = get_penalty_count("Employee Task Report",emp.employee_number)
	   		winfo = frappe.new_doc('Warning Information')
			winfo.update({
				'employee':emp.employee_number,
				'employee_name':emp.employee_name,
				'employee_violation':_('Employee Task Report'),
				'warning_date' : now,
				'docstatus':1
			})
			winfo.flags.ignore_validate = True
			winfo.flags.ignore_links = True
			winfo.insert(ignore_permissions=True)
		
			penalty_name =get_penalty_name(violations_count)
			if penalty_name:
				penalty_n = frappe.db.get_value("Employee Violation", {'violation_type':"Employee Task Report"},[penalty_name])
				if penalty_n:
					penalty = frappe.db.sql("""select penalty_type,warning_type,send_email,email_text from `tabPenalty` where penalty_name= %s """,(penalty_n), as_dict=1 ) 
					if penalty:
						if penalty[0].send_email == 1 or penalty[0].warning_type == 'Email':
							send_email(emp.employee_number ,penalty[0].email_text, _('Employee Task Late Warning')) 
	
	

def get_penalty_name(times):
	
	penalty = None
	if times<1:
		penalty = 'penalty_first_time'
	elif times==1:
		penalty = 'penalty_second_time'
	elif times==2:
		penalty = 'penalty_third_time'
	elif times==3:
		penalty = 'penalty_forth_time'
	elif times==4:
		penalty = 'penalty_fifth_time'
	elif times==5:
		penalty = 'penalty_sixth_time'
	elif times==6:
		penalty = 'penalty_seventh_time'
	elif times==7:
		penalty = 'penalty_eighth_time'
	elif times==8:
		penalty = 'penalty_ninth_time'
	elif times>=9:
		penalty = 'penalty_tenth_time'

	return penalty


def send_email(emp,email_text, subject):
	recipient_email = frappe.db.get_value("Employee Personal Detail", emp , "user_id")
	if not isinstance(recipient_email, list):
		#contact = frappe.get_doc('User', contact).email or contact
		sender      	    = dict()
		sender['email']     = frappe.db.get_value('Email Account',dict(enable_outgoing=1, default_outgoing=1),'email_id') #"maysaaelsafadi@gmail.com"
		sender['full_name'] = frappe.utils.get_fullname(sender['email'])
		#frappe.msgprint(str(frappe.db.get_value('Email Account',dict(enable_outgoing=1, default_outgoing=1),'email_id')))

		if recipient_email:
			try:
				print recipient_email
				frappe.sendmail(
					recipients = recipient_email,
					sender = sender['email'],
					subject = subject,
					message = email_text,
				)
				frappe.msgprint(_("Email sent to {0}").format(recipient_email))
			except frappe.OutgoingEmailError:
				pass 

@frappe.whitelist()
def get_penalty_count(employee_violation,employee,wdate= None):
	#from erpnext.accounts.utils import get_fiscal_year
	#f_year= get_fiscal_year(date=wdate,company=frappe.defaults.get_user_default('company'))[0]
	if not wdate:
		wdate = nowdate() #frappe.msgprint(_("Date does not existed!"))
	times = frappe.db.sql("""select count(*) from `tabWarning Information` where docstatus=1 and year(warning_date)= year(%s) and employee_violation= %s and employee= %s""",(wdate,employee_violation,employee) )
	count=0
	if times:
		count = times[0][0]
	return count



