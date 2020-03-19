# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.hr.doctype.employee.employee import get_employee_emails

class TrainingResult(Document):
	def validate(self):
		pass
		#training_event = frappe.get_doc("Training Event", self.training_event)
		#if training_event.docstatus != 1:
		#	frappe.throw(_('{0} must be submitted').format(_('Training Event')))

#		self.employee_emails = ', '.join(get_employee_emails([d.employee
#			for d in self.employees]))

	def on_submit(self):
		prog= frappe.get_doc("Training Program",self.training_event)
		emp_data = frappe.get_doc("Employee",self.employee)
		tra = emp_data.get("employee_training_courses")
		tra.append({"course_name" : prog.training_program,
				"start_date" : prog.get('from'),
				"end_date" : prog.to,
				"training_center" : prog.training_place ,
				"grade" : self.total,
				"total_hours" : prog.traning_period
				})
		emp_data.set("employee_training_courses",tra)
		emp_data.flags.ignore_validate = True
		emp_data.save(ignore_permissions=True)
#		training_event = frappe.get_doc("Training Event", self.training_event)
#		training_event.status = 'Completed'
#		for e in self.employees:
#			for e1 in training_event.employees:
#				if e1.employee == e.employee:
#					e1.status = 'Completed'
#					break
#
#		training_event.save()




def get_employees(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select employee from `tabTraining Target` where parent=%s""", (filters.get('training_event')))


@frappe.whitelist()
def get_employeess(training_event):
	return frappe.get_doc("Training Event", training_event).employees

@frappe.whitelist()
def get_questions(training_event):
	return frappe.get_list("Training Evaluation Questions", fields=["question"], filters={"type":"Trainer","parent":training_event}, order_by="question")

