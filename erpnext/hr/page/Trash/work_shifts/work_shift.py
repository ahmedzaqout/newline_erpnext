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
import json
import time




@frappe.whitelist(allow_guest=True)
def get_employess(date=None,department=None):
	result={}
	date=datetime.date.today()
	dow=datetime.date.today().weekday()
	

	if dow==6:
		dayy="Sunday"
	if dow==0:
		dayy="Monday"
	if dow==1:
		dayy="Tuesday"
	if dow==2:
		dayy="Wednesday"
	if dow==3:
		dayy="Thursday"
	if dow==4:
		dayy="Friday"
	if dow==5:
		dayy="Saturday"
	print "***********"
	print "************"
	print date
	flagg=False
	departments=frappe.get_list("Department",["name","department_name_en"])
	branches=frappe.get_list("Branch",["name","branch"])
	designations=frappe.get_list("Designation",["name","designation_name"])

	if department:
		employees=frappe.get_list("Employee",["name"]);
	else:
		employees=frappe.get_list("Employee",["name"]);
		
	if employees:
		for employee in employees:
			print employee.name
			emp=frappe.db.sql("""select emp.name,emp.employee_number, emp.image,det.department,det.work_hrs,det.work_shift ,
				det.private_work_shift,per.ar_fname,det.designation,
				per.employee_name from tabEmployee as emp join `tabEmployee Employment Detail` as det on emp.employee_number = det.employee 
				join `tabEmployee Personal Detail` as per 
				 on emp.employee_number = per.employee where emp.name='{0}'""".format(employee.name),as_dict=1)
			
			if emp:
				em=emp[0]
				childs=None
				if em:

					if em.work_shift:
						if em.work_shift:
							ws=frappe.get_doc("Work Shift",em.work_shift)
						if em.private_work_shift:
							pws=frappe.get_doc("Private Work Shift",em.private_work_shift)
							if pws:
								childs=frappe.get_list("Private Work Shift Details",["name","start_work","end_work","to_date" ,"from_date"],filters={"parent":["=",pws.name],"day":["=",dayy]})
								if childs:
									flag=False
									for ch in childs:
										
										if ch.to_date >=date and ch.from_date <= date:
											childs=frappe.get_list("Private Work Shift Details",["name","start_work","end_work","to_date" ,"from_date"],filters={"name":ch.name})
											flag=True
									if not flag:
										childs=None

									print childs
						if not childs:
							if ws:
								childs=frappe.get_list("Work Shift Details",["start_work","end_work"],filters={"parent":ws.name,"parenttype":"Work Shift","day":dayy
								})
		 			
		 			if not em.ar_fname and not childs:
		 				continue;
					if childs:
						result[em.name]=[em.ar_fname,em.image,abs(childs[0].start_work.total_seconds() / 3600), abs(childs[0].end_work-childs[0].start_work).total_seconds() / 3600, "childs[0].is_work_day", abs(childs[0].end_work.total_seconds() / 3600), "childs[0].is_sleeping_day",ws.color,em.name,em.department,em.branch,em.designation]
			    		flagg=True
			    	else:
						result[em.name]=[em.ar_fname,em.image,0, 0, 0, 0,0 ,None,em.name,em.department,em.branch,em.designation]			
						flagg=True
					
	abs1=frappe.get_list("Attendance",["employee"],filters={"attendance_date":date,"status":"Absent"})
	absence=[]
	if abs1:
		for mm in abs1:
			

			em=frappe.get_doc("Employee",mm.employee)

			if em:
				if em.ar_fname:
					absence.append([em.ar_fname,em.employee_name,em.image,em.department,em.branch,em.designation])
	if len(absence)==0:
		absence=None
	if not flagg:
		result=None
	return {
		"employee":result,
		"departments":departments,
		"branches":branches,
		"designations":designations,
		"absence" : absence
		}

@frappe.whitelist(allow_guest=True)
def save_shifts(shifts=None,date=None):
	res=[]
	pws=None
	ws=None
	d = json.loads(shifts)

	if date:
		date=datetime.date.today()
		dow=datetime.date.today().weekday()
		# dow=datetime.datetime(str(date)).weekday()
	else:
		date=datetime.date.today()
		dow=datetime.date.today().weekday()
	if dow==6:
			dayy="Sunday"
	if dow==0:
		dayy="Monday"
	if dow==1:
		dayy="Tuesday"
	if dow==2:
		dayy="Wednesday"
	if dow==3:
		dayy="Thursday"
	if dow==4:
		dayy="Friday"
	if dow==5:
		dayy="Saturday"


	for shift in d:
		if len(str(shift['start']))>1:
			time=str(shift['start'])+":00:00"
		else:
			time="0"+str(shift['start'])+":00:00"

		if len(str(int(shift['period'])+int(shift['start'])))>1:
			end=str(int(shift['period'])+int(shift['start']))+":00:00"
		else:
			end="0"+str(int(shift['period'])+int(shift['start']))+":00:00"

		res.append(time)
		res.append(end)
		emp=frappe.db.sql("""select emp.name,emp.employee_number, emp.image,det.department,det.work_hrs,det.work_shift ,
				det.private_work_shift,per.ar_fname,det.designation,
				per.employee_name from tabEmployee as emp join `tabEmployee Employment Detail` as det on emp.employee_number = det.employee 
				join `tabEmployee Personal Detail` as per 
				 on emp.employee_number = per.employee where emp.name='{0}'""".format(shift['name']),as_dict=1)
			
		if emp:
			em=emp[0]
			childs=None
			if em.private_work_shift:
				pws=frappe.get_doc("Private Work Shift",em.private_work_shift)

			childs=None
			if pws:
				childs=frappe.get_list("Private Work Shift Details",["name","start_work","end_work"],filters={"parent":pws.name,"from_date":str(date),"to_date":str(date)})

			if childs:
				if childs[0].start_work ==time and childs[0].end_work == end :
					print "********"
					continue;
				else:
					ss=frappe.get_doc("Private Work Shift Details",childs[0].name)
					ss.start_work ==time
					ss.end_work ==end 
					ss.save(ignore_permissions=True)
					print "444444444444444"
					continue;
			if pws:
				pp=frappe.get_doc("Private Work Shift",pws.name)
				r=pp.work_shift_details
				r.append({
					"day" : dayy,
					"from_date":str(date),
					"to_date":str(date),
					"start_work" : time,
					"end_work" : end,
					})

				pp.work_shift_details=r
				pp.save(ignore_permissions=True)


			else:
				mm=frappe.get_doc({
					"doctype" : "Private Work Shift",
					"work_shift":em.name + str(date),
					"work_shift_details":[{
						"day" : dayy,
						"from_date":str(date),
						"to_date":str(date),
						"start_work" : time,
						"end_work" : end

					}]
					
					})
				

				mm.insert(ignore_permissions=True)
				dd=frappe.get_doc("Private Work Shift",em.name + str(date))
				det=frappe.get_doc("Employee Employment Detail",em.name)
				if dd:
					if det:
						det.private_work_shift=dd.name
						det.save(ignore_permissions=True)
				

	return res 



