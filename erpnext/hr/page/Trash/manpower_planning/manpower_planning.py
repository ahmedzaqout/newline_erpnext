# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import frappe.defaults
from frappe import _, msgprint



@frappe.whitelist(allow_guest=True)
def get_departments():
	return frappe.db.get_list("Department")



@frappe.whitelist(allow_guest=True)
def get_data():
	return frappe.db.sql("select emp.employee_number, emp.image,sal.basic_salary,sal.grade,sal.experience_years,sal.grade_category,sal.hour_cost,det.department,det.work_hrs,per.ar_fname,\
per.ar_family_name,det.date_of_joining,det.designation,ss.parent as salary_struc from tabEmployee as emp  left join `tabEmployee Salary Detail` as sal on emp.employee_number = sal.employee  join `tabEmployee Employment Detail` as det on emp.employee_number = det.employee join `tabEmployee Personal Detail` as per on emp.employee_number = per.employee left join `tabSalary Structure Employee` as ss on ss.employee=emp.employee_number and  ss.parent in (select name from `tabSalary Structure` where is_active='Yes')",as_dict=1)  

	#return frappe.db.get_list("Employee",fields=["image","ar_fname","ar_family_name","employee","employee_name","date_of_joining", "department","basic_salary","designation","grade_category","grade","experience_years","hour_cost","job_number","work_hrs"])


@frappe.whitelist(allow_guest=True)
def get_salary_components():
	salary_components = {_("Earning"): [], _("Deduction"): []}
	for component in frappe.db.sql("""select distinct sd.salary_component, sc.type from `tabSalary Detail` sd, `tabSalary Component` sc where sc.name=sd.salary_component and sd.amount != 0 """, as_dict=1):
		salary_components[_(component.type)].append(component.salary_component)
	return salary_components[_("Earning")], salary_components[_("Deduction")]


@frappe.whitelist(allow_guest=True)
def get_salary_components_data():
	salary_components = {_("Earning"): [], _("Deduction"): []}
	for component in frappe.db.sql("""select distinct sd.salary_component, sc.type,sd.amount,sd.formula,sd.parent from `tabSalary Detail` sd, `tabSalary Component` sc where sc.name=sd.salary_component and sd.amount != 0  and sd.parent in (select name from `tabSalary Structure` where is_active='Yes')""", as_dict=1):
		salary_components[_(component.type)].append({"name":component.salary_component,"parent":component.parent,"amount":component.amount,"formula":component.formula})
	return salary_components[_("Earning")], salary_components[_("Deduction")]

@frappe.whitelist(allow_guest=True)
def get_grade(category):
	grades=[]
	#category = ["Top category","First category","second category","Third category","Fourth category","Fifth category"]
	#return frappe.db.get_value("Grade Category", {"category":"Top category"}, "name")
	#category= ["الفئة العليا","الفئة الأولى","الفئة الثانية","الفئة الثالثة","الفئة الرابعة","الفئة الخامسة"]
	#for cat in category:
	return frappe.db.get_list("Grade Category", {"category":category}, "name")
		#grade =frappe.db.sql("select grade_category from `tabGrade Category` where category=%s",("الفئة العليا"))
		#grades.append(doc)
	#return grades


@frappe.whitelist(allow_guest=True)
def get_salary(grade,year):
	return frappe.db.sql("select basic_salary from `tabGrade Category Detail` where experience_year=%s and parent=%s",(year,grade))
	 


@frappe.whitelist()
def get_sample_data():
    return {
    "get_sample_data": frappe.db.sql("""select false, name, employee_name, status from `tabEmployee`  order by name""", as_list=1)
    }



