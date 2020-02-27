# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime
from frappe import msgprint, _
from frappe.utils import getdate

class EmployeeEmploymentDetail(Document):
	def validate(self):
		try:
			if self.designation:
				emp_doc = frappe.get_doc('Employee',self.employee)
				emp_doc.designation = self.designation
				emp_doc.save(ignore_permissions=True)

			if self.supervisor:
				self.add_manager_staff()


			self.deactivate_employee()
			self.update_emp_work_shift()
			self.update_emp_work_history()
		except:
			pass

	def update_emp_work_shift(self):
		if getdate(self.shift_change_date) != getdate(frappe.db.get_value('Employee Employment Detail',self.name,'shift_change_date')):
			from erpnext.hr import clear_employee_holidays
			from erpnext.hr.doctype.attendance.attendance import update_holiday
			clear_employee_holidays(self.employee, self.shift_change_date)
			update_holiday(self.employee, self.holiday_list, self.shift_change_date)
			wsh_history = frappe.new_doc('Work Shift History')
			wsh_history.employee= self.employee
			wsh_history.work_shift= self.work_shift
			wsh_history.shift_change_date= self.shift_change_date
			wsh_history.flags.ignore_validate = True
			wsh_history.insert(ignore_permissions=True)
			
			
				
	def add_manager_staff(self):
		if self.supervisor and not frappe.db.get_value("Responsible Of Staff",{ "parent":self.supervisor,"employee": self.employee}, "employee"):
			if frappe.db.get_value('Employee Employment Detail',self.supervisor):
				emp_doc = frappe.get_doc('Employee Employment Detail',self.supervisor)
				emp_doc.append('responsible_of_staff',{
					'employee':self.employee,
					'employee_name':self.employee_name
					})
				emp_doc.flags.ignore_links = True
				emp_doc.flags.ignore_mandatory = True
				emp_doc.flags.ignore_validate =True
				emp_doc.save(ignore_permissions=True)


	def deactivate_employee(self):
		today = datetime.today()
		frappe.db.set_value("Employee", self.employee, "status", self.status)
		if self.status != "Active":
			frappe.db.set_value("Employee", self.employee, "relieving_date", today)
			frappe.db.set_value("User", {"employee":self.employee}, "enabled", 0)
			frappe.db.set_value("Employee Ending Service  Details", self.employee, "relieving_date", today)
		else:
			frappe.db.set_value("Employee", self.employee, "relieving_date", None)
			frappe.db.set_value("User", {"employee":self.employee}, "enabled", 1)
			frappe.db.set_value("Employee Ending Service  Details", self.employee, "relieving_date", None)


	def update_end_serv(self):
		if frappe.db.get_value("Employee Ending Service Details",{"employee": self.employee}, "employee"):
			frappe.db.set_value("Employee Ending Service  Details", self.employee, "relieving_date", self.contract_end_date)
			
	def update_emp_work_history(self):
		if (self.work_place_change_date) != (frappe.db.get_value('Employee Employment Detail',self.name,'work_place_change_date')):
			from_date=frappe.db.get_value('Employee Employment Detail',self.name,'work_place_change_date')
			to_date =self.work_place_change_date
	
			wh_history = frappe.new_doc('Employee Internal Work History')
			wh_history.employee= self.employee
			wh_history.branch= frappe.db.get_value('Employee Employment Detail',self.name,'branch')
			wh_history.circle= frappe.db.get_value('Employee Employment Detail',self.name,'circle')
			wh_history.management= frappe.db.get_value('Employee Employment Detail',self.name,'management')
			wh_history.department= frappe.db.get_value('Employee Employment Detail',self.name,'department')
			wh_history.designation= frappe.db.get_value('Employee Employment Detail',self.name,'designation')
			wh_history.from_date= from_date
			wh_history.to_date= to_date
			wh_history.parentfield= "employee_internal_work_history"
			wh_history.parent= self.employee
			wh_history.parenttype= "Employee Data"
			wh_history.flags.ignore_validate = True
			wh_history.flags.ignore_mandatory = True
			wh_history.insert(ignore_permissions=True)
			
				

