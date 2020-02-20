# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import datetime
from frappe.utils import today,getdate


class WorkshiftSchedule(Document):
	def validate(self):
		employee_shifts = self.get("employee_shift")
		for shift in employee_shifts:
			work_shift_details=[]
			day_list = ["Saturday","Sunday","Monday","Tuesday","Wednesday","Thursday","Friday"]
			fileds_list = ["saturday","sunday","monday","tuesday","wednesday","thursday","friday"]
			i=0
			for field in fileds_list:					
				if shift.get(field):
					shift_Time= frappe.get_doc("Shift Time" , shift.get(field) )
					work_shift_details.append({
								"day" : day_list[i],
								"start_work" :shift_Time.start_time,
								"end_work" : shift_Time.end_time,
								"next_day" : shift_Time.next_day })
				i+=1
			work_shift = frappe.get_doc({"doctype" : "Work Shift",
					"work_shift" : shift.employee+"_"+ datetime.date.today().strftime("%d-%m-%Y_%H:%i:%s"),
					"holiday_list" : "بدون عطل",
					"work_shift_details" : work_shift_details
					
				})
			work_shift.save(ignore_permissions=True)
			if frappe.db.get_value('Employee Employment Detail',{'employee':shift.employee}):
				sh = frappe.get_doc('Employee Employment Detail',{'employee':shift.employee})
				if sh:
					sh.update({
						'work_shift': work_shift.name,
						'holiday_list':work_shift.holiday_list,
						'shift_change_date' : getdate(today())
						})
					sh.flags.ignore_validate = True 
					sh.flags.ignore_mandatory = True
					sh.flags.ignore_links = True
					sh.save()
					wsh_history = frappe.new_doc('Work Shift History')
					wsh_history.employee= shift.employee
					wsh_history.work_shift= work_shift.name
					wsh_history.shift_change_date= getdate(today())
					wsh_history.flags.ignore_validate = True
					wsh_history.insert(ignore_permissions=True)



@frappe.whitelist()
def get_employees(department):
	return frappe.get_list("Employee Employment Detail",['employee','employee_name'],filters={"department":department})
