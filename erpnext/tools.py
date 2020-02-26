#!/usr/bin/python
# -*- coding: utf-8 -*-
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

@frappe.whitelist(allow_guest=True)
def add_work(date=None,department=None):
	
	employees=frappe.get_list("Employee",["name","work_shift","image"]);
	if employees:
		for employee in employees:
			em=frappe.get_doc("Employee",employee.name)
			frappe.get_doc({"doctype":"Work Shift History",
					"employee":em.name,
					"work_shift":"دوام كلي صباحي",
					"shift_change_date":"2018-12-31"}).save(ignore_permissions=True)

@frappe.whitelist(allow_guest=True)
def read_personal():
	import csv
	with open('/home/frappe/frappe-bench/apps/erpnext/erpnext/Employee_Personal_Detail.csv', 'r') as csvfile:
		spamreader = csv.reader(csvfile)
		index=0
		for row in spamreader:
			index+=1
			if index > 20:
					if row[15]:
						gover=frappe.get_all("Governorate" , ['name'],filters={"name":row[15].decode("utf-8")})
						if not gover:
							gov =frappe.get_doc({"doctype" : "Governorate","governorate_name":row[15].decode("utf-8")})
							gov.flags.ignore_mandatory = True
							gov.save(ignore_permissions = True)
					
					if row[18]:
						city=frappe.get_all("City" , ['name'],filters={"name":row[18].decode("utf-8")})
						if not city:
							city =frappe.get_doc({"doctype" : "City", "city_name":row[18].decode("utf-8"),"governorate" : row[15].decode("utf-8")})
							city.flags.ignore_mandatory = True
							city.save(ignore_permissions = True)

					if row[21]:
						rel=frappe.get_all("Religion" , ['name'],filters={"name":row[21].decode("utf-8")})
						if not rel:
							rel =frappe.get_doc({"doctype" : "Religion", "religion_name":row[21].decode("utf-8")})
							rel.flags.ignore_mandatory = True
							rel.save(ignore_permissions = True)

					if row[22]:
						gen=frappe.get_all("Gender" , ['name'],filters={"name":row[22].decode("utf-8")})
						if not gen:
							gen =frappe.get_doc({"doctype" : "Gender", "gender":row[22].decode("utf-8")})
							gen.flags.ignore_mandatory = True
							gen.save(ignore_permissions = True)
					if row[23]:
						nat=frappe.get_all("Nationality" , ['name'],filters={"name":row[23].decode("utf-8")})
						if not nat:
							nat =frappe.get_doc({"doctype" : "Nationality", "nationality_name":row[23].decode("utf-8")})
							nat.flags.ignore_mandatory = True
							nat.save(ignore_permissions = True)

	
					ar_fname = row[3].decode("utf-8") if row[3].decode("utf-8")  else " "
					ar_sname = row[4].decode("utf-8") if row[4].decode("utf-8")  else " "
					ar_tname = row[5].decode("utf-8")  if row[5].decode("utf-8")  else " "
					ar_family_name = row[6].decode("utf-8") if row[6].decode("utf-8")  else " "
					employee_name =ar_fname+" "+ar_sname+" "+ar_tname+" "+ar_family_name
					
					if row[0]:
						em=frappe.get_all("Employee" , ['name'],filters={"diwan_number":row[0]})	
		

						if em:

							em_doc=frappe.get_doc("Employee" ,em[0].name)
							em_doc.diwan_number=row[0]
							em_doc.employee_name=employee_name
							em_doc.flags.ignore_mandatory = True
							em_doc.save(ignore_permissions = True)

							aa=frappe.get_doc({
							"doctype":"Employee Personal Detail",
							"employee": em_doc.name,
							"employee_number" :  em_doc.name,
							"ar_fname":row[3].decode("utf-8"),
							"ar_sname" : row[4].decode("utf-8"),
							"ar_tname":row[5].decode("utf-8"),
							"ar_family_name" : row[6].decode("utf-8"),
							"en_fname":row[7],
							"en_sname" : row[8],
							"en_tname" : row[9],
							"en_family_name" : row[10],
							"employee_name" : employee_name,
							"company" : frappe.defaults.get_global_default("company"),
							"fp_id" : row[12],
							"user_id" : row[13],
							"identity_no" : row[14],
							"governorate" : row[15].decode("utf-8"),
							"date_of_birth" : row[16].decode("utf-8"),
							"sub_organization" : row[17],
							"city" : row[18].decode("utf-8"),
							"place_of_birth" : row[19],
							"marital_status" : row[20],
							"religion" : row[21],
							"gender" : row[22].decode("utf-8"),
							"nationality" : row[23].decode("utf-8"),
							"phone_number" : row[24],
							"current_address" : row[31].decode("utf-8")
							})


							aa.flags.ignore_mandatory = True
							aa.save(ignore_permissions = True)
							
							print index
						else:
							em_doc=frappe.get_doc({"doctype":"Employee","diwan_number" : row[0]})
							em_doc.employee_name=employee_name
							em_doc.flags.ignore_mandatory = True
							em_doc.save(ignore_permissions = True)
							frappe.db.sql("update `tabEmployee` set employee_number = '{0}' where name= '{0}'".format(em_doc.name))
							aa=frappe.get_doc({
							"doctype":"Employee Personal Detail",
							"employee": em_doc.name,
							"employee_number" :  em_doc.name,
							"ar_fname":row[3].decode("utf-8"),
							"ar_sname" : row[4].decode("utf-8"),
							"ar_tname":row[5].decode("utf-8"),
							"ar_family_name" : row[6].decode("utf-8"),
							"en_fname":row[7],
							"en_sname" : row[8],
							"en_tname" : row[9],
							"en_family_name" : row[10],
							"employee_name" : employee_name,
							"company" : frappe.defaults.get_global_default("company"),
							"fp_id" : row[12],
							"user_id" : row[13],
							"identity_no" : row[14],
							"governorate" : row[15].decode("utf-8"),
							"date_of_birth" : row[16].decode("utf-8"),
							"sub_organization" : row[17],
							"city" : row[18].decode("utf-8"),
							"place_of_birth" : row[19],
							"marital_status" : row[20],
							"religion" : row[21],
							"gender" : row[22].decode("utf-8"),
							"nationality" : row[23].decode("utf-8"),
							"phone_number" : row[24],
							"current_address" : row[31].decode("utf-8")
							})

							aa.flags.ignore_mandatory = True
							aa.save(ignore_permissions = True)
							
							print index
					else:
						em_doc=frappe.get_doc({"doctype":"Employee","diwan_number" :row[0]})
						em_doc.employee_name=employee_name
						em_doc.flags.ignore_mandatory = True
						em_doc.save(ignore_permissions = True)
						em_doc.save(ignore_permissions = True)
						frappe.db.sql("update `tabEmployee` set employee_number = '{0}' where name= '{0}'".format(em_doc.name))
						aa=frappe.get_doc({
						"doctype":"Employee Personal Detail",
						"employee": em_doc.name,
						"employee_number" :  em_doc.name,
						"ar_fname":row[3].decode("utf-8"),
						"ar_sname" : row[4].decode("utf-8"),
						"ar_tname":row[5].decode("utf-8"),
						"ar_family_name" : row[6].decode("utf-8"),
						"en_fname":row[7],
						"en_sname" : row[8],
						"en_tname" : row[9],
						"en_family_name" : row[10],
						"company" : frappe.defaults.get_global_default("company"),
						"fp_id" : row[12],
						"user_id" : row[13],
						"identity_no" : row[14],
						"governorate" : row[15].decode("utf-8"),
						"date_of_birth" : row[16].decode("utf-8"),
						"sub_organization" : row[17],
						"city" : row[18].decode("utf-8"),
						"place_of_birth" : row[19],
						"marital_status" : row[20],
						"religion" : row[21],
						"gender" : row[22].decode("utf-8"),
						"nationality" : row[23].decode("utf-8"),
						"phone_number" : row[24],
						"current_address" : row[31].decode("utf-8")
						})

						aa.flags.ignore_mandatory = True
						aa.save(ignore_permissions = True)
						
						print index


@frappe.whitelist(allow_guest=True)
def read_employment():
	import csv
	with open('/home/frappe/frappe-bench/apps/erpnext/erpnext/Employee_Employment_Detail.csv', 'r') as csvfile:
		spamreader = csv.reader(csvfile)
		index=0
		for row in spamreader:
			index+=1
			if index > 20:
					if row[5]:
						gover=frappe.get_all("Employment Type" , ['name'],filters={"name":row[5].decode("utf-8")})
						if not gover:
							gov =frappe.get_doc({"doctype" : "Employment Type","employee_type_name":row[5].decode("utf-8")})
							gov.flags.ignore_mandatory = True
							gov.save(ignore_permissions = True)
					
					if row[6]:
						city=frappe.get_all("Work Shift" , ['name'],filters={"name":row[6].decode("utf-8")})
						if not city:
							city =frappe.get_doc({"doctype" : "Work Shift", "work_shift":row[6].decode("utf-8")})
							city.flags.ignore_mandatory = True
							city.save(ignore_permissions = True)

					if row[9]:
						rel=frappe.get_all("Department" , ['name'],filters={"name":row[9].decode("utf-8")})
						if not rel:
							rel =frappe.get_doc({"doctype" : "Department", "department_name":row[9].decode("utf-8")})
							rel.flags.ignore_mandatory = True
							rel.save(ignore_permissions = True)

					if row[10]:
						gen=frappe.get_all("Designation" , ['name'],filters={"name":row[10].decode("utf-8")})
						if not gen:
							gen =frappe.get_doc({"doctype" : "Designation", "designation_name":row[10].decode("utf-8")})
							gen.flags.ignore_mandatory = True
							gen.save(ignore_permissions = True)
					if row[21]:
						nat=frappe.get_all("Branch" , ['name'],filters={"name":row[21].decode("utf-8")+" - BRA"})
						if not nat:
							nat =frappe.get_doc({"doctype" : "Branch", "branch":row[21].decode("utf-8")})
							nat.flags.ignore_mandatory = True
							nat.save(ignore_permissions = True)

					if row[22]:
						mana=frappe.get_all("Management" , ['name'],filters={"name":row[22].decode("utf-8")+" - MGT"})
						if not mana:
							mana =frappe.get_doc({"doctype":"Management", "management":row[22].decode("utf-8")})
							mana.flags.ignore_mandatory = True
							mana.save(ignore_permissions = True)
							print mana.name
	
					if row[23]:
						ci=frappe.get_all("Circle" , ['name'],filters={"name":row[23].decode("utf-8")})
						if not ci:
							cir =frappe.get_doc({"doctype" : "Circle", "circle":row[23].decode("utf-8")})
							cir.flags.ignore_mandatory = True
							cir.save(ignore_permissions = True)
					
					if row[0]:
						print row[0]
						em=frappe.get_all("Employee" , ['name'],filters={"diwan_number" :row[0]})
						maa=""
						bar=""
						if row[22]:
							maa=row[22].decode("utf-8")+" - MGT"
						if row[21]:
							bar=row[21].decode("utf-8")+" - BRA"

						if em:
							if not frappe.get_all("Employee Employment Detail" , ['name'],filters={"name" :em[0].name}):
								em_doc=frappe.get_doc("Employee" ,em[0].name)
								aa=frappe.get_doc({
								"doctype":"Employee Employment Detail",
								"employee": em_doc.name,
								"designation":row[10].decode("utf-8"),
								"status" : "Active",
								"date_of_joining":row[12].decode("utf-8"),
								"scheduled_confirmation_date" : row[4].decode("utf-8"),
								"employment_type":row[5].decode("utf-8"),
								"contract_end_date" : row[13].decode("utf-8"),
								"work_shift" : row[6].decode("utf-8"),
								"company" : frappe.defaults.get_global_default("company"),
								"holiday_list" : row[7].decode("utf-8"),
								"branch" : bar,
								"management" : maa,
								"circle" : row[23].decode("utf-8"),
								"sub_dep" : "Department",
								"department" : row[9].decode("utf-8"),



								})

								aa.flags.ignore_mandatory = True
								aa.save(ignore_permissions = True)
								
								print aa.name


@frappe.whitelist(allow_guest=True)
def read_salary():
	import csv
	with open('/home/frappe/frappe-bench/apps/erpnext/erpnext/Employee_Salary_Detail.csv', 'r') as csvfile:
		spamreader = csv.reader(csvfile)
		index=0
		for row in spamreader:
			index+=1
			if index > 20:
					if row[13]:
						gover=frappe.get_all("Bank" , ['name'],filters={"name":row[13].decode("utf-8")})
						if not gover:
							gov =frappe.get_doc({"doctype" : "Bank","bank":row[13].decode("utf-8")})
							gov.flags.ignore_mandatory = True
							gov.save(ignore_permissions = True)
					
					if row[14]:
						city=frappe.get_all("Bank Branch" , ['name'],filters={"name":row[14].decode("utf-8")})
						if not city:
							city =frappe.get_doc({"doctype" : "Bank Branch", "bank_branch":row[14].decode("utf-8"), "bank" : row[13].decode("utf-8")})
							city.flags.ignore_mandatory = True
							city.save(ignore_permissions = True)

					
					
					if row[0]:
						print row[0]
						em=frappe.get_all("Employee" , ['name'],filters={"diwan_number" :row[0]})
		

						if em:
							em_doc=frappe.get_doc("Employee" ,em[0].name)
							aa=frappe.get_doc({
							"doctype":"Employee Salary Detail",
							"employee": em_doc.name,
							"basic_salary":row[3],
							"payroll_frequency" : row[4],
							"grade":row[6],
							"experience_years" : row[7],
							"day_salary":row[9],
							"hour_cost" : row[10],
							"over_hrs" : row[11],
							"company" : frappe.defaults.get_global_default("company"),
							"bank_name" : row[13].decode("utf-8"),
							"bank_branch" : row[14].decode("utf-8"),
							"bank_ac_no" : row[15].decode("utf-8"),
							
							})

							aa.flags.ignore_mandatory = True
							aa.save(ignore_permissions = True)
							
							print aa.name
						
						



