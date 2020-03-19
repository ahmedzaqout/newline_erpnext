# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Evaluators(Document):
	def validate(self):
		form = frappe.get_doc('Evaluation Form',self.evaluation_form)
																						
		per = frappe.get_all("Evaluation Section" ,["evaluation_item"],filters={'parent' : form.name ,"parentfield" : 'personal',"parenttype": "Evaluation Form"} )
		performance = frappe.get_all("Evaluation Section" ,["evaluation_item"],filters={'parent' : form.name ,"parentfield" : 'performance',"parenttype": "Evaluation Form"} )
		technical = frappe.get_all("Evaluation Section" ,["evaluation_item"],filters={'parent' : form.name ,"parentfield" : 'technical',"parenttype": "Evaluation Form"} )

		em_de = frappe.get_doc('Employee', self.employee)

		for m in self.get("evaluators"):
			em = frappe.get_doc("Employee", m.employee)
			eva = frappe.get_list("Employee Evaluation" , ['name'] ,filters={"employee" : self.employee,"docstatus": 0,"user": em.user_id})


			if not eva or len(eva) == 0 :
				doc = frappe.new_doc('Employee Evaluation')
				doc.update({
					'employee': self.employee,
					'employee_name': self.employee_name,
					'department': em_de.department,
					'designation': em_de.designation,
					'user': em.user_id,
					'evaluation_form': self.evaluation_form
				})
				if per:
					for r in per:
						doc.append("personal", {
							'evaluation_item':r.evaluation_item
							})
				if performance:
					for r in performance:
						doc.append("performance", {
							'evaluation_item':r.evaluation_item
							})
				if per:
					for r in technical:
						doc.append("technical", {
							'evaluation_item':r.evaluation_item
							})



				doc.insert(ignore_permissions=True)

