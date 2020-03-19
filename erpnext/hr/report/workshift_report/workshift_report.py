# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _
import datetime, calendar, time
from calendar import monthrange
from datetime import date, timedelta

def execute(filters=None):

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	data = salaries(conditions, filters)
	return columns, data


def get_columns(filters):
	columns = [
		 {"label":_("Employee ") ,"width":100,"fieldtype": "link","options":"Employee"},
		 {"label":_("Employee Name") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Designation") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Departement") ,"width":100,"fieldtype": "Data"},
 		 {"label":_("Working Hours") ,"width":180,"fieldtype": "Float"},
		 {"label":_("Actual Working Hours") ,"width":180,"fieldtype": "Float"},
		 ]
		
	return columns


def salaries(conditions, filters):
	from erpnext.hr import get_compensatory, get_permissions
	data=[]
	hours={}
	employees  = frappe.db.sql("""select emp.name, emp.employee_name,emp.* from `tabEmployee` as emp  where emp.docstatus <2 %s order by name""" % conditions, filters, as_dict=1)

	delta = (datetime.datetime.strptime(filters.to_date, '%Y-%m-%d')).date() - (datetime.datetime.strptime(filters.from_date, '%Y-%m-%d')).date()   
	for emp in employees:
		total, total_r =0.0, 0.0
		if emp.work_shift:
			ws=frappe.get_doc("Work Shift",emp.work_shift)
		else:
			continue #frappe.throw(_("Work shift does not Exist"))


		compensatory_total_hours= get_compensatory(emp.name, filters.from_date, filters.to_date)
		permission_total_hours= get_permissions(emp.name, filters.from_date, filters.to_date)

		for i in range(delta.days + 1):
			dayy = calendar.day_name[(datetime.datetime.strptime( filters.from_date, '%Y-%m-%d').date()+timedelta(i)).weekday()]
			#dayy=((datetime.datetime.strptime(filters.from_date, '%Y-%m-%d').date() + timedelta(i)).weekday())

			totalshift  = frappe.db.sql("""select  GREATEST(round(TIMESTAMPDIFF(MINUTE,ws.start_work,ws.end_work)/60,2),0) as total_hours from `tabWork Shift Details` as ws where ws.parent=%(workshift)s and ws.day= %(day)s""",{'workshift':ws.name,'day':dayy}, as_dict=1)
		
			m=(datetime.datetime.strptime(filters.from_date, '%Y-%m-%d').date() + timedelta(i))
			ds=datetime.datetime(m.year, m.month, m.day)

			totalreal  = frappe.db.sql("""select  GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as total_hours,att.status from tabAttendance as att left join  tabDeparture as dept on att.attendance_date=dept.departure_date and att.employee=dept.employee and dept.docstatus = 1 where att.discount_salary_from_leaves=0 and att.docstatus=1 and att.employee=%(employee)s and att.attendance_date= %(date)s""",{'employee':emp.name,'date':datetime.datetime.strftime(ds, '%Y-%m-%d')}, as_dict=1)

			if totalreal:
				#if totalreal[0].status == "Present" or totalreal[0].status == "Half Day":
				if totalreal[0].total_hours:
					if totalreal[0].total_hours > totalshift[0].total_hours:
						total_r = total_r  + (totalreal[0].total_hours-(totalreal[0].total_hours - totalshift[0].total_hours) )
					else: total_r += totalreal[0].total_hours

			if totalshift:
				if totalshift[0].total_hours:
					total+=totalshift[0].total_hours


		total_r=total_r + compensatory_total_hours - permission_total_hours

		if (not filters.less) and total > total_r:
			continue
		elif (not filters.more) and total < total_r:
			continue
		elif (not filters.exact) and total == total_r:
			continue
		else:
 			row=[emp.employee,emp.employee_name,emp.designation,emp.department,total_r, total]	
			data.append(row)
	

			
	
	
	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("employee"): conditions += " and emp.name = %(employee)s"
	if filters.get("department"): conditions += " and emp.management = %(department)s"

	if filters.get("designation"): conditions += " and emp.designation = %(designation)s"

	return conditions, filters
