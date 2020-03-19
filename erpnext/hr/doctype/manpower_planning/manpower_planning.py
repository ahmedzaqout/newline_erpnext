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
		conditions= " where emp.department=%s"
	else: 
		conditions= " where 1=%s"
		department = "1"

	return frappe.db.sql("select emp.employee_number, emp.image,emp.basic_salary,emp.grade,emp.experience_years,emp.grade_category,emp.hour_cost,emp.department,\
		emp.work_hrs,emp.ar_fname,emp.ar_family_name,emp.date_of_joining,emp.designation,ss.parent as salary_struc from tabEmployee as emp  left join `tabSalary Structure Employee` as ss on ss.employee=emp.employee_number and  ss.parent in (select name from `tabSalary Structure` where is_active='Yes') %s"% conditions,department,as_dict=1)  



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

