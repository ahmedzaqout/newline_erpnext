# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import getdate, nowdate,get_time, time_diff,time_diff_in_seconds,get_datetime,cint
from frappe import _, msgprint
from frappe.model.document import Document
from erpnext.hr.utils import set_employee_name
import datetime, calendar
from calendar import monthrange



@frappe.whitelist(allow_guest=True)
def get_employess(date=None,department=None):
	result={}
	today = datetime.datetime(2018, 3, 20)
	dow=today.get_weekday() 
	if department:
		employees=Frappe.get_list("Employee",["name","work_shift","image"],filters={"department":department});
	else:
		employees=Frappe.get_list("Employee",["name","work_shift","image"]);

		print dow
		if employees:
			for employee in employees:
				em=frappe.get_doc("Employee",employee.name)
				ws=frappe.get_doc("Work Shift",em.work_shift)
				childs=frappe.get_list("Work Shift Details",["start_work","total_work_hrs","is_work_day","end_work","is_sleeping_day"],filters={"parent":ws,"day":dow})


				result['employee.name']['name']=employee.name;
				result['employee.name']['start_work'] = childs.start_work
				result['employee.name']['total_work_hrs'] = childs.total_work_hrs
				result['employee.name']['is_work_day'] = childs.is_work_day
				result['employee.name']['end_work'] = childs.end_work
				result['employee.name']['is_sleeping_day'] = childs.is_sleeping_day
		return result