# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today
from frappe import _, msgprint

class EarningsDeductionsTool(Document):
	def add_earning_deduction(self,fromdate, todate, employee, department,all_employee):
		if all_employee == 0 and employee:
			doc= frappe.get_all('Salary Slip',fields=["start_date","end_date","name"],filters={'employee':employee,'docstatus':("<",2)})
			for emp_slip in doc:
				if getdate(emp_slip.start_date) >= getdate(fromdate) and getdate(emp_slip.end_date) <= getdate(todate):
					earn_doc = frappe.get_doc("Salary Slip", emp_slip.name)
					for e in self.earnings:
						if not self.duplicated_salary_component(earn_doc.earnings,e.salary_component):
							earn_doc.append('earnings',{
								'salary_component':e.salary_component,
								'abbr': e.abbr,
								'formula': e.formula,
								'amount': e.amount,
								'type': e.type
									})
							earn_doc.save(ignore_permissions=True)

					for d in self.deductionss:
						if not self.duplicated_salary_component(earn_doc.deductions,d.salary_component):
							earn_doc.append('deductions',{
								'salary_component':d.salary_component,
								'abbr': d.abbr,
								'formula': d.formula,
								'amount': d.amount,
								'type': d.type
									})
							earn_doc.save(ignore_permissions=True)

		elif all_employee == 1:
			#employees = frappe.get_all("Employee", fields=["name","employee_name"],filters={'status':'Active'})
			doc= frappe.get_all('Salary Slip',fields=["start_date","end_date","name"],filters={'docstatus':0,'start_date':(">=",getdate(fromdate)), 'end_date':("<=",getdate(todate)) })
			#for emp in employees:
			if doc:
				for emp_slip in doc:
				#if emp_slip.start_date >= getdate(fromdate) and emp_slip.end_date <= getdate(todate):
					earn_doc = frappe.get_doc("Salary Slip", emp_slip.name)
					for e in self.earnings:
						if not  self.duplicated_salary_component(earn_doc.earnings,e.salary_component):
							earn_doc.append('earnings',{
								'salary_component':e.salary_component,
								'abbr': e.abbr,
								'formula': e.formula,
								'amount': e.amount,
								'type': e.type
									})
							earn_doc.save(ignore_permissions=True)

					for d in self.deductionss:
						if not  self.duplicated_salary_component(earn_doc.earnings,e.salary_component):
							earn_doc.append('deductions',{
								'salary_component':d.salary_component,
								'abbr': d.abbr,
								'formula': d.formula,
								'amount': d.amount,
								'type': d.type
									})
							earn_doc.save(ignore_permissions=True)

		elif all_employee == 0 and department:
			employees = frappe.get_all("Employee", fields=["name","department"],filters={'status':'Active','department':department })
			for emp in employees:
				doc= frappe.get_all('Salary Slip',fields=["start_date","end_date","name"],filters={'employee':emp,'docstatus':("<",2)})
				for emp_slip in doc:
					if emp_slip.start_date >= getdate(fromdate) and emp_slip.end_date <= getdate(todate):
						earn_doc = frappe.get_doc("Salary Slip", emp_slip.name)
						for e in self.earnings:
							if not self.duplicated_salary_component(earn_doc.earnings,e.salary_component):
								earn_doc.append('earnings',{
									'salary_component':e.salary_component,
									'abbr': e.abbr,
									'formula': e.formula,
									'amount': e.amount,
									'type': e.type
										})
								earn_doc.save(ignore_permissions=True)

						for d in self.deductionss:
							if not self.duplicated_salary_component(earn_doc.earnings,e.salary_component):
								earn_doc.append('deductions',{
									'salary_component':d.salary_component,
									'abbr': d.abbr,
									'formula': d.formula,
									'amount': d.amount,
									'type': d.type
										})
								earn_doc.save(ignore_permissions=True)
		else:
			frappe.throw(_("No salary slip found between {0} and {1}").format(fromdate,todate) )

	def duplicated_salary_component(self,doc,salary_component):
		for e in doc:
			if salary_component == e.salary_component:
				#frappe.msgprint(salary_component+" true "+e.salary_component)
				return True
			else:
				return False



