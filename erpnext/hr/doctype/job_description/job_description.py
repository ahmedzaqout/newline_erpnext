# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe,erpnext
from frappe.model.document import Document
from calendar import monthrange
from frappe.utils import getdate, nowdate, add_days,datetime,cint,flt, time_diff_in_hours,comma_and
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee 
from erpnext.hr.doctype.payroll_entry.payroll_entry import get_month_details 
from erpnext.hr.doctype.leave_application.leave_application import get_holidays 
from erpnext.accounts.utils import get_fiscal_year
from frappe.model.mapper import get_mapped_doc
from frappe.model.naming import make_autoname
from frappe import _




class JobDescription(Document):
	def autoname(self):
		if self.job_number:
			self.name = self.job_number

	def validate(self):
		if self.designation:
			names = frappe.db.sql_list("""select name from `tabJob Description`
				where designation=%s and name!=%s """, (self.designation, self.name))

			if names:
				frappe.throw(_("Designation must be unique, already exists for {0}").format(comma_and(names)), frappe.DuplicateEntryError)




@frappe.whitelist(allow_guest=True)
def month_days(employee=None,cur_date=None):
	#employee= "EMP/0001"
	if not cur_date:cur_date= nowdate()
	mydate= datetime.datetime.strptime(str(cur_date), "%Y-%m-%d")
	month=mydate.month
	year=mydate.year
	total_days_in_month = cint(monthrange( cint(year), cint(month) )[1])

	fiscal_year = get_fiscal_year(nowdate(), company=erpnext.get_default_company())[0]
	#month = "%02d" % getdate(nowdate()).month
	m = get_month_details(fiscal_year, month)
	start_date = m['month_start_date']
	end_date = m['month_end_date']

	if employee:
		number_of_days =  flt(total_days_in_month) - flt(get_holidays(employee, start_date, end_date))
	else:
		number_of_days =  26

	#get working_hours_day	
	total_time, count ,hr_per_day = 0, 0, 0.0
	wshift = frappe.db.get_value("Employee Employment Detail", employee, "work_shift")
	total_time = frappe.db.sql("select ifnull(sum(round(TIMESTAMPDIFF(MINUTE,start_work,end_work)/60,2)),0) as total_hours, count(start_work)  from `tabWork Shift Details` where parent=%s", wshift)
	if total_time and total_time[0][1] !=0:
		hr_per_day =float(total_time[0][0])/float(total_time[0][1])
	#wsh_time = frappe.get_all("Work Shift Details", fields=["start_work","end_work"],filters={'parent':wshift})
	#for t in wsh_time:
	#	count =count+1
	#	time_dif = frappe.db.sql("select TIMESTAMPDIFF(MINUTE,%s,%s)/60" ,(t.start_work,t.end_work) ) 
	#	total_time = total_time + round( float(time_dif[0][0] or 0.0),2)
	
	return total_days_in_month, number_of_days, hr_per_day


@frappe.whitelist(allow_guest=True)
def add_PNW_SComponent():
	salary_component = frappe.new_doc("Salary Component")
	if not salary_component:
		salary_component.update({
			"name": 'Premium nature work',
			"salary_component": 'Premium nature work',
			"salary_component_abbr": 'PNW'
		})
		salary_component.insert()

	return "done"

@frappe.whitelist()
def make_planned_job(source_name, target_doc=None):
	def set_missing_values(source, target):
		planned_job = frappe.get_doc(target)	
		planned_job.run_method("set_missing_values")


	doclist = get_mapped_doc("Job Description", source_name, {
		"Job Description": {
			"doctype": "Planned Job",
			"field_map": {
				"designation": "designation",
				"grade": "grade",
				"name" : "job_number" ,
				"category": "category"

			}
		},
		"Duties and Responsibilities": {
			"doctype": "Duties and Responsibilities",
			"field_map": {
				"parent": "prevdoc_docname",
				"parenttype": "prevdoc_doctype",

			},
			"add_if_empty": True
		},
		"Functional Specification Items": {
			"doctype": "Functional Specification Items",
			"field_map": {
				"parent": "prevdoc_docname",
				"parenttype": "prevdoc_doctype",

			},
			"add_if_empty": True
		},
		"Job Performance Requirements": {
			"doctype": "Job Performance Requirements",
			"field_map": {
				"parent": "prevdoc_docname",
				"parenttype": "prevdoc_doctype",

			},
			"add_if_empty": True
		},


	}, target_doc, set_missing_values)

	return doclist



@frappe.whitelist()
def make_unplanned_job(source_name, target_doc=None):
	def set_missing_values(source, target):
		planned_job = frappe.get_doc(target)	
		planned_job.run_method("set_missing_values")


	doclist = get_mapped_doc("Job Description", source_name, {
		"Job Description": {
			"doctype": "Unplanned Job",
			"field_map": {
				"designation": "designation",
				"grade": "grade",
				"name" : "job_number" ,
				"category": "category",
				"job_code": "job_number"
			}
		}

	}, target_doc, set_missing_values)

	return doclist


@frappe.whitelist()
def get_experience(grade):
	result=[]
	ex =frappe.get_list('Grade Category Detail', ['experience_year'],filters={'parent': grade})
	for e in ex:
		result.append(e.experience_year)



	
	return result

