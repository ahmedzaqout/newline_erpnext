# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class ManpowerPlanning(Document):
	pass

@frappe.whitelist(allow_guest=True)
def get_job_description(designation):
	return	frappe.db.sql("select sum(sd.amount) as earnings, sum(sde.amount) as deductions,  category,basic_salary,experience_year,grade,monthly_work_hours,salary_period,hour_cost, jd.name, sd.name from `tabJob Description` as jd join `tabSalary Detail` as sd on jd.name= sd.parent and sd.type='Earning' join `tabSalary Detail` as sde on jd.name= sde.parent and sde.type='Deduction' where designation =%s", designation ,as_dict=1) 

@frappe.whitelist(allow_guest=True)
def get_dep(department= None):
	if department: 
		conditions= " where det.department=%s"
	else: 
		conditions= " where 1=%s"
		department = "1"

	return frappe.db.sql("select emp.employee_number, emp.image,sal.basic_salary,sal.grade,sal.experience_years,sal.grade_category,sal.hour_cost,det.department,det.work_hrs,per.ar_fname,\
per.ar_family_name,det.date_of_joining,det.designation,ss.parent as salary_struc from tabEmployee as emp  left join `tabEmployee Salary Detail` as sal on emp.employee_number = sal.employee  join `tabEmployee Employment Detail` as det on emp.employee_number = det.employee join `tabEmployee Personal Detail` as per on emp.employee_number = per.employee left join `tabSalary Structure Employee` as ss on ss.employee=emp.employee_number and  ss.parent in (select name from `tabSalary Structure` where is_active='Yes') %s"% conditions,department,as_dict=1)  


@frappe.whitelist(allow_guest=True)
def get_salary_components():
	salary_components = {_("Earning"): [], _("Deduction"): []}
	for component in frappe.db.sql("""select distinct sd.salary_component, sc.type from `tabSalary Detail` sd, `tabSalary Component` sc where sc.name=sd.salary_component and sd.amount != 0 """, as_dict=1):
		salary_components[_(component.type)].append(component.salary_component)
	return salary_components[_("Earning")], salary_components[_("Deduction")]



@frappe.whitelist(allow_guest=True)
def add_field(doctype, field_label, field_name, field_type, options=None, default=None):
	return "done"
	dt = frappe.get_doc('DocType', doctype)
	df = frappe.new_doc('DocField')

	df.name = field_name
	df.label = field_label
	df.fieldname = field_name
	df.fieldtype = field_type
	df.parent = doctype
	df.parentfield = 'fields'
	df.parenttype = 'DocType'
	df.parent_doc = dt
	df.in_list_view = 1
	df.width = 1
	df.columns = 1


	if options:
		df.options = options
	if default:
		df.default = default

	df.save()
	df.submit()
	dt.on_update()
	frappe.db.commit()
	return "done"

