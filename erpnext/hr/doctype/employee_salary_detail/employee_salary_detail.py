# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate,cstr
from frappe import _

class EmployeeSalaryDetail(Document):
	def validation(self):
		if not self.validate_salary_structure():
			frappe.msgprint(_("Press Make Salary Structure Button"))


	def validate_salary_structure(self):
		employee_name = self.employee_name
		if not self.employee_name:
			employee_name = self.employee

		if frappe.db.get_value('Salary Structure', _('Salary Structure')+'_'+ employee_name ):
			return True
		else:
			return False

	def make_salary_structure(self, arg=None):
		if self.validate_salary_structure():
			employee_name = self.employee_name
			if not self.employee_name:
				employee_name = self.employee
			sal_struct = frappe.get_doc('Salary Structure', _('Salary Structure')+'_'+ employee_name )
			if sal_struct:
				self.update_earnings(sal_struct)
				self.update_deductions(sal_struct)
		else:
			self.new_salary_structure()
		

	def new_salary_structure(self):
		employee_name = self.employee_name
		if not self.employee_name:
			employee_name = self.employee

		date_of_joining = frappe.db.get_value("Employee Employment Detail", {'employee':self.employee}, "date_of_joining")
		if date_of_joining:
			joining_date = date_of_joining
		else: joining_date = getdate(nowdate())
		
		from erpnext.hr.doctype.payroll_entry.payroll_entry import get_end_date
		if self.payroll_frequency:
			end_date = get_end_date(cstr(joining_date), self.payroll_frequency)['end_date']

		doc = frappe.new_doc('Salary Structure')
		doc.update({
			'name':_('Salary Structure')+'_'+ employee_name,
			'employee_name':employee_name,
			'salary_period':self.payroll_frequency,
			'employees': [{
				'employee': self.employee,
				'base':self.basic_salary,
				'from_date':joining_date,
				'to_date':end_date,
				'day_salary':self.day_salary,
				'hour_cost':self.hour_cost,
				'overtime_hour_cost': self.over_hrs
				}]
			
			})
		doc.save(ignore_permissions=True)

		doc.append('earnings',{
			'salary_component':'Basic',
			'abbr': 'B',
			'formula':'',
			'amount': self.basic_salary,
			'type': _('Earning')
				})
		doc.save(ignore_permissions=True)

		for e in self.earnings:
			doc.append('earnings',{
				'salary_component':e.salary_component,
				'abbr': e.abbr,
				'formula': e.formula,
				'amount': e.amount,
				'type': e.type
					})
			doc.save(ignore_permissions=True)

		for d in self.deductions:
			doc.append('deductions',{
				'salary_component':d.salary_component,
				'abbr': d.abbr,
				'formula': d.formula,
				'amount': d.amount,
				'type': d.type
					})
			doc.save(ignore_permissions=True)


	def update_earnings(self, sal_struct):
		sal_struct_name = sal_struct.name
		earning_arr, earning_amount= [], []
		for e in sal_struct.get("earnings"):
			earning_arr.append(e.salary_component)
			#earning_amount.append(e.amount)

		for earning in self.earnings:
			if earning.salary_component not in earning_arr:
				sal_struct.append(
					'earnings',{
						'salary_component':earning.salary_component,
						'amount': earning.amount
					})
				sal_struct.save(ignore_permissions=True)
			else:
				if frappe.db.get_value('Salary Detail',{'parent':sal_struct_name,'type':'Earning'}):					
					pass#sal_struct_det = frappe.get_doc('Salary Detail',{'parent':sal_struct_name,'type':'Earning'})
					#sal_struct_det.amount = earning.amount
					#sal_struct_det.save(ignore_permissions=True)

	def update_deductions(self, sal_struct):
		deduction_arr= []
		for d in sal_struct.get("deductions"):
			deduction_arr.append(d.salary_component)

		for deduction in self.deductions:
			if deduction.salary_component not in deduction_arr:
				sal_struct.append(
					'deductions',{
						'salary_component':deduction.salary_component,
						'amount': deduction.amount
					}					
				)
				sal_struct.save(ignore_permissions=True)
			else:
				if frappe.db.get_value('Salary Detail',{'parent':sal_struct.name,'type':'Deduction'}):					
					sal_struct_det = frappe.get_doc('Salary Detail',{'parent':sal_struct.name,'type':'Deduction'})
					sal_struct_det.amount = deduction.amount
					sal_struct_det.save(ignore_permissions=True)
			


	def get_salary_remaining(self):
		return frappe.get_all("Salary Slip", fields=["month","start_date","name","salary_ratio","remaining_salary","basic_salary"],filters={'employee':self.employee,'salary_ratio':("!=", 0)})

	def get_emp_warnings(self):
		return frappe.get_all("Warning Information", fields=["warning_date","penalty","penalty_type","warning_type","discount_hour","discount_period_type","employee_violation"],filters={'employee':self.employee})
			
	def update_salary_history(self,last_salary,basic_salary):
		doc = frappe.new_doc('Salary Change History')
		doc.update({
			#'name':_('Salary Structure')+'_'+ employee_name,
			'employee':self.employee,
			'last_salary':last_salary,
			'new_salary':basic_salary,
			'change_date':getdate(nowdate()),
			'user': frappe.session.user
			})
		doc.save(ignore_permissions=True)

@frappe.whitelist(allow_guest=True)
def employee_child(employee):
	return frappe.db.sql("""select count(name) as count from `tabEmployee Dependent` where relation in ('Son','Daughter') and parent=%s""", employee, as_dict=1)



		
