# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.model.document import Document
from frappe.utils import today,getdate


class WorkShift(Document):
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

	def allocate_shift(self):
		def add_shift(employee):
			if frappe.db.get_value('Employee',{'employee':employee}):
				sh = frappe.get_doc('Employee',{'employee':employee})
				if sh:
					sh.update({
						'work_shift': self.work_shift,
						'holiday_list':self.holiday_list,
						'shift_change_date' : getdate(today())
						})
					sh.flags.ignore_validate = True 
					sh.flags.ignore_mandatory = True
					sh.flags.ignore_links = True
					sh.save()

		if self.all_employees == 1:
			employees = self.get_employees()
			if not employees:
				frappe.throw(_("No employee found"))
			for d in self.get_employees():
				add_shift(d[0])
			msgprint(_("Shift Allocated Successfully"))

		elif self.employee:
				add_shift(self.employee)
				msgprint(_("Shift Allocated Successfully"))



@frappe.whitelist()
def add_shift_details():
	last_idx = max([cint(d.idx) for d in self.get("work_shift_details")] or [0,])
	day_list = ["Saturday","Sunday","Monday","Tuesday","Wednesday","Thursday","Friday"]
	for i, d in enumerate(day_list):
		ch = self.append('work_shift_details', {})
		ch.day = day_list[i]
		ch.idx = last_idx + i + 1



