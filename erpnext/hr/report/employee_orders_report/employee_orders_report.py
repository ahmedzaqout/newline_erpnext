# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _

def execute(filters=None):

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	data = salaries(conditions, filters)
	return columns, data


def get_columns(filters):
	columns = [
		 {"label":_("Employee") ,"width":100,"fieldtype": "link","options":"Employee"},
		 {"label":_("Employee Name") ,"width":120,"fieldtype": "Data",},
		 {"label":_("Designation") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Managment") ,"width":150,"fieldtype": "Data"}]


	if filters.type=="Employee Edit Time":
		columns.append({"label":_("Date") ,"width":100,"fieldtype": "Date"})
		columns.append({"label":_("Attendance Time") ,"width":120,"fieldtype": "Time"})
		columns.append({"label":_("Departure Time") ,"width":120,"fieldtype": "Time"})
		columns.append({"label":_("Status") ,"width":120,"fieldtype": "Data"})
		

	if filters.type=="Timesheet":
		columns.append({"label":_("Start Date"), "width":100,"fieldtype": "Date"})
		columns.append({"label":_("End Date") ,"width":100,"fieldtype": "Date"})
		columns.append({"label":_("Type") ,"width":120,"fieldtype": "Data"})
		columns.append({"label":_("Total Working Hours") ,"width":100,"fieldtype": "Float"})
		columns.append({"label":_("Status") ,"width":100,"fieldtype": "Date"})

	
	if filters.type=="Exit Permission":
		columns.append({"label":_("Permission Date") ,"width":100,"fieldtype": "Date"})
		columns.append({"label":_("Permission Type") ,"width":120,"fieldtype": "Data"})
		columns.append({"label":_("From Date") ,"width":120,"fieldtype": "Date"})
		columns.append({"label":_("To Date") ,"width":120,"fieldtype": "Date"})
		columns.append({"label":_("Status") ,"width":100,"fieldtype": "Data"})
		columns.append({"label":_("Reson") ,"width":100,"fieldtype": "Data"})

	if filters.type=="Leave Application":
		columns.append({"label":_("From Date") ,"width":100,"fieldtype": "Date"})
		columns.append({"label":_("To Date") ,"width":100,"fieldtype": "Date"})
		columns.append({"label":_("Leave Type") ,"width":120,"fieldtype": "Data"})
		columns.append({"label":_("Total Leave Days") ,"width":100,"fieldtype": "Float"})
 		columns.append({"label":_("Leave Balance") ,"width":100,"fieldtype": "Data"})
		columns.append({"label":_("Status") ,"width":110,"fieldtype": "Data"})
		columns.append({"label":_("Reson") ,"width":150,"fieldtype": "Data"})

	
	
	return columns

def salaries(conditions, filters):
	data=[]
	
	
	if filters.type=="Employee Edit Time":
		edit_time_orders= frappe.db.sql("""select em.employee_name , ed.management, ed.designation, ed.circle, et.attendance_date, et.attendance_time,et.departure_time,et.docstatus from `tabEmployee Edit Time` et left join `tabEmployee` as em on et.employee=em.employee left join `tabEmployee Employment Detail` as ed on em.employee = ed.employee  where  et.docstatus <2 %s order by et.attendance_date desc """ %
		conditions, filters, as_dict=1 )
		for emp in edit_time_orders:
			row=[emp.employee, emp.employee_name,emp.designation, emp.management,emp.attendance_date, emp.attendance_time ,emp.departure_time]
			if emp.docstatus ==0:
				row.append("Pending Request") 
			if emp.docstatus ==1:
				row.append("Initial Approval")
			data.append(row)

	if filters.type=="Timesheet":
		timesheet = frappe.db.sql("""select em.employee_name , ed.management, ed.designation, ed.circle,ts.end_date,ts.start_date,ts.type,ts.docstatus,ts.total_hours from `tabTimesheet` ts left join `tabEmployee` as em on ts.employee=em.employee left join `tabEmployee Employment Detail` as ed on em.employee = ed.employee  where  ts.docstatus <2 %s order by ts.start_date desc""" %
		conditions, filters, as_dict=1 )
		for emp in timesheet:
			row=[emp.employee,emp.employee_name,emp.designation,emp.management, emp.start_date, emp.end_date ,emp.type, emp.total_hours]
			if emp.docstatus ==0:
				row.append("Pending Request") 
			if emp.docstatus ==1:
				row.append("Initial Approval")
			data.append(row)

	if filters.type=="Exit Permission":
		permission_orders = frappe.db.sql("""select em.employee_name , ed.management, ed.designation, ep.* from `tabExit permission` as ep  left join `tabEmployee` as em on ep.employee=em.employee left join `tabEmployee Employment Detail` as ed on em.employee = ed.employee where  ep.docstatus <2 %s order by ep.permission_date desc """ %
		conditions, filters, as_dict=1 )
		for emp in permission_orders:
			row=[emp.employee,emp.employee_name,emp.designation,emp.management,emp.permission_date, emp.permission_type,emp.from_date,emp.to_date]
			if emp.docstatus ==0:
				row.append("Pending Request") 
			if emp.docstatus ==1:
				row.append("Initial Approval")
			row.append(emp.reason)
			data.append(row)

		
	if filters.type=="Leave Application":
		leave_orders = frappe.db.sql("""select em.employee_name , ed.management, ed.designation, la.* from `tabLeave Application` as la left join `tabEmployee` as em on la.employee=em.employee left join `tabEmployee Employment Detail` as ed on em.employee = ed.employee  where  la.docstatus <2 %s order by la.from_date desc """ %
		conditions, filters, as_dict=1 )
		for emp in leave_orders:
			row=[emp.employee,emp.employee_name,emp.designation,emp.management,emp.from_date,emp.to_date, emp.leave_type,emp.total_leave_days,emp.leave_balance]
			if emp.docstatus ==0:
				row.append("Pending Request") 
			if emp.docstatus ==1:
				row.append("Initial Approval")
			row.append(emp.reason)
			data.append(row)





	return data


def get_conditions(filters):
	conditions = ""
	
	if filters.get("employee"): conditions += " and em.employee = %(employee)s"
	if filters.get("department"): conditions += " and ed.management = %(department)s"
	if filters.get("designation"): conditions += " and ed.designation = %(designation)s"

	return conditions, filters
