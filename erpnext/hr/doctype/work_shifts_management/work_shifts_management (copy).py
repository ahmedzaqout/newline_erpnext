# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate,get_time, time_diff,time_diff_in_seconds,get_datetime,cint,today,time_diff_in_hours
import datetime, calendar, time
from frappe.model.naming import make_autoname


class WorkShiftsManagement(Document):
	def autoname(self):
		wname = self.employee + self.day
		self.name = wname

	def validate(self):
		pass



@frappe.whitelist()
def update_shifts(name=None,start=None,end=None):
	today = calendar.day_name[getdate(frappe.utils.today()).weekday()];
	#frappe.msgprint(str(name))

	if frappe.db.get_value("Private Work Shift",name, "name"):
		doc = frappe.get_doc('Private Work Shift',name)
		doc.append('work_shift_details', {
				'day':today,
				'from_date':start,
				'to_date':end,
				'start_work':start,
				'end_work':end
				})
		doc.save(ignore_permissions=True)
		
	else:
		sh_doc = frappe.new_doc('Private Work Shift')
		sh_doc.update({
			'name':name,
			'work_shift':name,
			'work_shift_details': [{
				'day':today,
				'from_date':start,
				'to_date':end,
				'start_work':start,
				'end_work':end
					}]
			})
		sh_doc.insert(ignore_permissions=True)
		frappe.db.sql("update `tabEmployee Employment Detail` set private_work_shift=%s ",name)

	#emp_doc = frappe.get_doc('Employee Employment Detail',self.employee)
	#emp_doc.append({'private_work_shift':self.name})
	#emp_doc.save(ignore_permissions=True)
			

@frappe.whitelist()
def get_curday():
	return calendar.day_name[getdate(frappe.utils.today()).weekday()];


@frappe.whitelist()
def get_shifts():
	today = calendar.day_name[getdate(frappe.utils.today()).weekday()];
	data= frappe.db.sql('select employee,department,designation,emp.work_shift,cast(concat(CURDATE(), " ", dsh.start_work) as datetime) as start,cast(concat(CURDATE(), " ", dsh.end_work) as datetime) as end,day from `tabEmployee Employment Detail` as emp join `tabWork Shift Details` as dsh on emp.work_shift=dsh.parent where day=%s',today,as_dict=1)
	for emp in data:
		hrs_diff= time_diff_in_hours(emp.end,emp.start)
		progress=100
		wname= emp.employee+today
		if not frappe.db.get_value("Work Shifts Management", {"name": wname}):
			doc = frappe.new_doc('Work Shifts Management')
			doc.update({
				'name':wname,
				'employee':emp.employee,
				'department':emp.department,
				'designation':emp.designation,
				'work_shift':emp.work_shift,
				'day':today,
				'hours':hrs_diff,
				'progress':progress,
				'start_hour':emp.start,
				'end_hour':emp.end
		
				})
			doc.insert(ignore_permissions=True)


@frappe.whitelist()
def get_totals_hrs(department):
	total  = 0.0
	wshift_list = frappe.get_list("Work Shifts Management", fields=["hours"] ,filters={"department": department},order_by= "name")
	for wsh in wshift_list:
		total = total + wsh.hours
	
	return total
