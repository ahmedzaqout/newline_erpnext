# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.utils import today,getdate

class EarningsClassification(Document):	
	def validate(self):
		if not frappe.db.get_value("Salary Component",{"salary_component":_("Premium nature work")}):
			from erpnext.hr import add_PNW_SComponent
			add_PNW_SComponent()
			#frappe.throw(_("{0} does not found,").format(_('Annual Leave'))
		
		for data in self.designation:
			self.update_pnw(data.designation, data.ratio, data.degree)

	def update_pnw(self, designation, ratio, degree):
		employees = frappe.get_all("Employee", fields=["name","employee_name","designation"],filters={'status':'Active'})
		for emp in employees:
			sal_det = frappe.db.get_value("Employee",{'name':emp.name},["name","grade","grade_category"],as_dict=1)
			if  sal_det and sal_det.grade == degree and emp.designation == designation: #if degree var:
				sal_doc = frappe.get_doc("Employee",{'name':emp.name})
				sal_doc.update({'earnings':[{
						'salary_component': _('Premium nature work'),
						'amount':ratio }] })
				sal_doc.flags.ignore_validate = True
				sal_doc.save(ignore_permissions=True)
			# update salary structure 
			sal_stru_emp = frappe.db.get_value("Salary Structure Employee",{'employee':emp.name},"parent",as_dict=1)
			if sal_stru_emp:
				sal_stru = frappe.db.get_value("Salary Structure",{"name":sal_stru_emp.parent},"name",as_dict=1)
				if  sal_det and sal_stru and sal_det.grade == degree and emp.designation == designation: #if degree var:
					stru_doc = frappe.get_doc("Salary Structure",sal_stru.name)
					stru_doc.update({'earnings':[{
							'salary_component': _('Premium nature work'),
							'amount':ratio }] })
					stru_doc.flags.ignore_validate = True
					stru_doc.save(ignore_permissions=True)
			# update salary slip
			curmonth= getdate(today()).month
			curyear = getdate(today()).year
			sal_slip = frappe.db.sql("select name from `tabSalary Slip` where employee= %s and docstatus!=2 and month(start_date)=%s and year(start_date)= %s",(emp.name,curmonth,curyear),as_dict=1)
			if  sal_det and sal_slip and sal_det.grade == degree and emp.designation == designation: #if degree var:
				slip_doc = frappe.get_doc("Salary Slip",{'employee':emp.name})
				slip_doc.update({'earnings':[{
						'salary_component': _('Premium nature work'),
						'amount':ratio }] })
				slip_doc.flags.ignore_validate = True
				slip_doc.flags.ignore_validate_update_after_submit = True 
				slip_doc.save(ignore_permissions=True)


				



