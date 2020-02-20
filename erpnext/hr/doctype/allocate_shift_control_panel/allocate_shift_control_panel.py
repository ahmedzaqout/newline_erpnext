# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

from frappe.utils import cint, cstr, flt, nowdate, comma_and, date_diff
from frappe import msgprint, _

class AllocateShiftControlPanel(Document):
	def get_employees(self):
		conditions, values = [], []
		for field in ["company", "employment_type", "branch", "designation", "department"]:
			if self.get(field):
				conditions.append("{0}=%s".format(field))
				values.append(self.get(field))

		condition_str = " and " + " and ".join(conditions) if len(conditions) else ""

		e = frappe.db.sql("select name from tabEmployee where status='Active' {condition}"
			.format(condition=condition_str), tuple(values))

		return e

	def to_date_validation(self):
		if date_diff(self.to_date, self.from_date) <= 0:
			return "Invalid period"

	def validate_values(self):
		for f in ["from_date", "to_date", "holiday_list", "work_shift"]:
			if not self.get(f):
				frappe.throw(_("{0} is required").format(self.meta.get_label(f)))

	def allocate_shift(self):
		self.validate_values()
		def add_shift(employee):
			shift_allocated_for = []
			try:
				sh = frappe.new_doc('Work Shift')
				sh.employee = cstr(employee)
				sh.employee_name = frappe.db.get_value('Employee',cstr(employee),'employee_name')
				sh.holiday_list = self.holiday_list
				#'Work Shift Details'
				#sh.from_date = self.from_date
				#sh.to_date = self.to_date
				sh.save()
				shift_allocated_for.append(employee)
			except:
				pass

		if self.all_employee:
			employees = self.get_employees()
			if not employees:
				frappe.throw(_("No employee found"))
			for d in self.get_employees():
				add_shift(d[0])

		elif self.employee:
				add_shift(self.employee)


		if shift_allocated_for:
			msgprint(_("Shift Allocated Successfully for {0}").format(comma_and(shift_allocated_for)))


