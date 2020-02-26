# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, throw
from frappe.utils import flt, time_diff_in_hours, get_datetime, getdate, cint,get_time

class EmployeeTask(Document):
	def validate(self):
		for m in self.get("time_logs"):
			if not m.specialization:
				frappe.throw(_("Please specify your specialization for project '{0}'" .format(m.project)))
			man=frappe.db.sql("""select task_mandatory from `tabProject`where name = %s""", m.project)
			if man[0][0]==1:
				if not m.task and not m.task_not_in_the_system:
					frappe.throw(_("you have to specify task for project '{0}'".format(m.project)))
						
			if m.task:
				if not  frappe.db.sql("""select * from  `tabTask Details` as td   join `tabTask` as t  on td.parent=t.name  where t.name =%s and td.employee=%s""",(m.task,self.employee)):
					task1=frappe.get_doc("Task",m.task)
					if task1:
						r=frappe.get_doc({"doctype":"Task Details",
						"employee":self.employee,
						"employee_name" : self.employee_name,
						"expected_time_in_hours":m.hours,
						"parent" : task1.name,
						"parenttype" : "Task",
						"parentfield" : "task_details"
						}).insert(ignore_permissions=True)

					


			if not m.task and m.task_not_in_the_system:
					import decimal
					qq= frappe.db.sql("""select t.subject,t.name from  `tabTask` as t where t.project =%s""",m.project)
					flag=False					
					if qq:
						for q in qq:
							if q[0] == m.task_not_in_the_system:
								task=frappe.get_doc("Task",q[1])
								if not  frappe.db.sql("""select * from  `tabTask Details` as td   join `tabTask` as t  on td.parent=t.name  where t.name =%s and td.employee=%s""",(q[1],self.employee)):
									m.task=q[1]
									flag=True
								elif task:
									ho=float(m.hours);
									r=frappe.get_doc({"doctype":"Task Details",
									"employee":self.employee,
									"employee_name" : self.employee_name,
									"expected_time_in_hours":m.hours,
									"parent" : task.name,
									"parenttype" : "Task",
									"parentfield" : "task_details"
									}).insert(ignore_permissions=True)
									m.task = task.name
									
									task.time_expected=(float(task.time_expected)+ho)
									task.flags.ignore_permissions = True
									task.save()
									flag=True

					if not flag:
						user=frappe.get_doc("User",frappe.session.user)
						employee=user.employee
						emp=None
						employee_name=None
						if employee:
							emp=frappe.get_doc("Employee Personal Detail", {"employee_number":user.employee} ,"employee_name") 
							employee_name=emp.employee_name
						r=frappe.get_doc({"doctype":"Task",
							"subject":m.task_not_in_the_system,
							"project" : m.project,
							"time_expected" : m.hours,
							"user" : employee,
							"employee_name" : employee_name,
							"name" : m.task_not_in_the_system +"-"+m.project}
							).insert(ignore_permissions = True)
						d=frappe.get_doc({"doctype":"Task Details",
									"employee":self.employee,
									"employee_name" : self.employee_name,
									"expected_time_in_hours":m.hours,
									"parent" : r.name,
									"parenttype" : "Task",
									"parentfield":"task_details"}
									).insert(ignore_permissions=True)
						m.task = r.name
			
									
			
				
		

def task_query(doctype, txt, searchfield, start, page_len, filters):
	conditions = [] 



	res1=frappe.db.sql("""select distinct(p.name) from `tabTask Details` as td join `tabTask` as p on  td.parent=p.name where td.employee= '{0}' and p.project = '{1}' and p.docstatus < 2""".format(filters.get("employee"),filters.get("project")))


	return res1

def emp_project_query(doctype, txt, searchfield, start, page_len, filters):
	conditions = []
	return frappe.db.sql("""select distinct(p.name) from `tabProject User` as pu  join `tabProject` as p on pu.parent=p.name 
		where pu.user =%s and p.docstatus < 2""",filters.get("employee"))

def get_specialization(doctype, txt, searchfield, start, page_len, filters):
	conditions = []
	return frappe.db.sql("""select distinct(pu.specialization) from  `tabProject User` as pu  join `tabProject` as p on pu.parent=p.name 
		where p.docstatus < 2 and pu.user = %(employee)s and p.name = %(project)s """,{"employee":filters.get("employee"),"project":filters.get("project")})



def test():
	
	to_customer = frappe.get_doc("Customer",
                dict( customer_name=("like", "%@{0}".format(customer_id) ) )  )

@frappe.whitelist()
def check_mand(employee , project):
	return frappe.db.sql("""select distinct(pu.specialization) from  `tabProject User` as pu  join `tabProject` as p on pu.parent=p.name where pu.user = %(employee)s and p.name = %(project)s """,{"employee":employee,"project":project})

	





