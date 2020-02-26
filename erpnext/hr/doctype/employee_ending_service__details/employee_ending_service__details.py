# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime
from erpnext.hr.doctype.leave_application.leave_application import get_leave_allocation_records,get_leave_balance_on, get_approved_leaves_for_period,get_leaves_for_period
from frappe import _
from frappe.utils import getdate, nowdate, date_diff,cstr, flt



class EmployeeEndingServiceDetails(Document):
	def validate(self):
		if self.type and not self.relieving_date:
			frappe.throw(_("Please enter relieving date."))
		elif self.type and self.relieving_date:
			self.service_years = self.get_service_years()
			self.amount = flt(self.calculate_end_service_amount())
			#self.update_emp_status('Left')

	def update_emp_status(self, status):
		frappe.db.set_value('Employee Employment Detail', self.employee,'status',status)
		frappe.db.set_value('Employee Employment Detail', self.employee,'contract_end_date',self.relieving_date)
		frappe.db.set_value("Employee", self.employee, "status", status)
		frappe.db.set_value("Employee", self.employee, "relieving_date", self.relieving_date)
		frappe.db.set_value("User", {"employee":self.employee}, "enabled", 0)


	def get_leaves_taken(self):
		offer_date = frappe.db.get_value('Employee Employment Detail',self.employee,'scheduled_confirmation_date')
		leaves_taken = get_approved_leaves_for_period(self.employee, _('Annual Leave'), offer_date, self.relieving_date )
		leave_balance ,leaves_hours = get_leave_balance_on(self.employee, _('Annual Leave'), self.relieving_date ,consider_all_leaves_in_the_allocation_period=True)
		#leave_allocations = get_leave_allocation_records(self.relieving_date, self.employee).get(self.employee, frappe._dict())
		#from_date = leave_allocations.get(_('Annual Leave'), frappe._dict()).from_date

		#leave_allocation_records = frappe.db.sql("""select employee, leave_type, total_leaves_allocated, from_date, to_date,carry_forward
		#from `tabLeave Allocation` where employee=%s and leave_type = %s and docstatus=1 order by from_date desc""", (self.employee, _('Annual Leave')), as_dict=1)
		#for d in leave_allocation_records:
			#leaves_allocated += d.total_leaves_allocated
		#	leave_balance ,leaves_hours = get_leave_balance_on(self.employee, _('Annual Leave'), d.from_date ,consider_all_leaves_in_the_allocation_period=True)
		#	leave_balance += leave_balance
		
		return leave_balance

	def calculate_end_service_amount(self):
		service_years = self.get_service_years()
		basic_salary ,day_salary= frappe.db.get_value('Employee Salary Detail',self.employee,['basic_salary','day_salary'])

		if self.type =='Resignation':
			taken_leaves = self.get_leaves_taken()
			amount = service_years * basic_salary +(taken_leaves* day_salary)

			if service_years <=5:
				amount= 0.3333 * flt(amount)
			elif service_years <=9:
				amount= 0.6667 * flt(amount)
			elif service_years >=10:
				amount= amount
		elif self.type =='End of the decade':
			amount = service_years * basic_salary 

		return amount


	def get_service_years(self):
		offer_date = frappe.db.get_value('Employee Employment Detail',self.employee,'scheduled_confirmation_date')
		service_years = date_diff(self.relieving_date, offer_date)/365
		return service_years

