# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
import frappe

class TrainingProgram(Document):
	pass

@frappe.whitelist()
def dep_emp_num(department):
	count = frappe.db.sql("""select count(*) from `tabEmployee Employment Detail` where status='Active' and department=%s""", department)[0][0]
	return count
		

@frappe.whitelist(allow_guest=True)
def emp_department0(department):
	return frappe.db.sql("""select e.employee_name from tabEmployee as emp join `tabEmployee Employment Detail` as e on emp.employee_number=e.name where e.status='Active' and e.department=%s""", department,as_dict=True)
		


def emp_department(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select emp.name,emp.employee_name,e.employee from tabEmployee as emp join `tabEmployee Employment Detail` as e on emp.employee_number=e.name where e.status='Active' and e.department=%s""", (filters.get('department')))
