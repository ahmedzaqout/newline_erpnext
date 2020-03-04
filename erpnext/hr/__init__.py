# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, msgprint
from datetime import datetime, timedelta
from frappe.utils import getdate, time_diff_in_hours,  today, add_months
from frappe.utils.background_jobs import enqueue



def is_overtime_exceeded(employee, date):
	total= 0.0
	timesheets = frappe.db.sql("select sum( td.hours ) as total_hours,t.docstatus,employee,date(from_time) as ddate,type from tabTimesheet as t join `tabTimesheet Detail` as td on t.name=td.parent and t.docstatus=1 and month(from_time) = month(%(date)s) group by employee,type having employee=%(employee)s and type !='compensatory' ", {'employee': employee, 'date': date,}, as_dict=1)
	if timesheets:
		for t in timesheets:
			total += t.total_hours
	
	ovr_max_hrs = frappe.db.get_value("Employee Salary Detail", employee, "overtime_max_hours")

	if total >= float(ovr_max_hrs):
		return True
	else:
		return False
		

def exit_perm(ddate= None):
	if not ddate:
		ddate = datetime.today()
	employees = frappe.get_all("Employee", fields=["name","employee_name"],filters={'status':'Active'})
	for emp in employees:
		dupl_att = frappe.get_value('Attendance',{'employee':emp.name,'attendance_date':getdate(ddate),'docstatus':1},"name")
		dupl_dep = frappe.get_value('Departure',{'employee':emp.name,'departure_date':getdate(ddate),'docstatus':1},"name")
		dupl_ext = frappe.get_value('Exit permission',{'employee':emp.name,'permission_date':getdate(ddate),'type':'Return'},["name","to_date"], as_dict=1)

		if dupl_att and not dupl_dep and dupl_ext:
			dept = frappe.new_doc('Departure')
			dept.update({
				'employee':emp.name,
				'employee_name':emp.employee_name,
				'departure_time':dupl_ext.to_date,
				'departure_date':getdate(ddate),
				'status':'Present',
				'docstatus':1
					})
			dept.insert(ignore_permissions=True)
		
	return True

#Notify manager to add a new job opening at the detected date 
def notify_manpower_jobopening_date():
	today =datetime.today()
	users = frappe.get_all("User", fields=["name","email"],filters={'enabled':1})
	recipients = []
	for usr in users:
		user = frappe.get_doc("User", usr.name)
		if "HR Manager" in [u.role for u in user.get("roles")]:
			recipients.append(usr.email)
	print str(recipients)
	doc = frappe.db.get_all("Manpower Planning Items", { 'company': frappe.defaults.get_user_default("Company") },["job_announcement_date","name"])
	for d in doc:
		print str(d.job_announcement_date)
		if today == d.job_announcement_date:
			email_args = {
				"recipients": recipients,
				"subject": 'Reminder: New Job Openeing- {0}'.format(today),
				"reference_doctype": 'Manpower Planning Items',
				"reference_name": d.name
					}
			enqueue(method=frappe.sendmail, queue='short', timeout=300, async=True, **email_args)
		else:
			msgprint(_("{0}: Employee email not found, hence email not sent").format(d.name))

def hide_expired_job_opening():

	today =datetime.today().strftime("%Y-%m-%d")
	t = datetime.strptime(datetime.today().strftime("%H:%M:%S"),"%H:%M:%S")

	delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)

	jobs = frappe.get_all("Job Opening", fields=["name","expiration_date","expiration_time"],filters={"company":"Nawa","expiration_date" :["<=",today]})
	
	publ_jobs = frappe.get_all("Job Opening", fields=["name","expiration_date"],filters={"publishing_date" :today})
	for d in publ_jobs:
		doc= frappe.get_doc("Job Opening", d.name)
		doc.publish =1
		doc.save(ignore_permissions=True)

	for d in jobs:
		if d.expiration_time:
			print d.expiration_time
			print delta
			if d.expiration_time < delta:
				print "Ss"
				doc= frappe.get_doc("Job Opening", d.name)
				doc.publish =0
				doc.save(ignore_permissions=True)

		
			




def notify_retirement_employee():
	from erpnext.hr.doctype.employee.employee import get_retirement_date
	today =datetime.today()
	employees = frappe.get_all("Employee Employment Detail", fields=["name","supervisor"],filters={'status':'Active'})
	for emp in employees:
		doc = frappe.db.get_value("Employee Personal Detail", emp.name, ["user_id" ,"date_of_birth"],as_dict=1)
		supervisor = frappe.db.get_value("Employee Personal Detail", emp.supervisor, ["user_id"],as_dict=1)
		if doc and supervisor:
			date_of_retirement = get_retirement_date(doc.date_of_birth)
			print date_of_retirement['date_of_retirement']
			if date_of_retirement['date_of_retirement'] >= today.strftime('%Y-%m-%d'):
				if doc.user_id:
					print doc.user_id
					email_args = {
						"recipients": [doc.user_id , supervisor.user_id],
						"subject": 'Employee Retirement- {0}'.format(today),
						"reference_doctype": 'Employee Employment Detail',
						"reference_name": emp.name
						}
					enqueue(method=frappe.sendmail, queue='short', timeout=300, async=True, **email_args)
				else:
					msgprint(_("{0}: Employee email not found, hence email not sent").format(emp.name))


def notify_trial_employee():
	if frappe.defaults.get_user_default("Company") != 'Nawa':
		print str(False)
		return False

	employees = frappe.get_all("Employee Employment Detail", fields=["date_of_joining","employment_type","name","supervisor"],filters={'status':'Active'})
	for emp in employees:
		supervisor = frappe.db.get_value("Employee Personal Detail", emp.supervisor, ["user_id"],as_dict=1)
		duration = frappe.db.get_value("Employment Type", emp.employment_type, "duration",as_dict=1)	
		if duration and duration.duration >0:
			print str(duration.duration)
			print str(emp.date_of_joining)
			print str(today())
			trial_period = add_months(emp.date_of_joining,duration.duration)
			#today_period = add_months(today,duration)
			print str(trial_period)
			if trial_period <= getdate(today()):
				doc = frappe.db.get_value("Employee Personal Detail", emp.name, ["user_id" ,"date_of_birth"],as_dict=1)
				if doc.user_id:
					print doc.user_id
					email_args = {
						"recipients": [doc.user_id,supervisor.user_id ],
						"subject": 'Employee Trial Ended- {0}'.format(today()),
						"reference_doctype": 'Employee Employment Detail',
						"reference_name": emp.name
						}
					enqueue(method=frappe.sendmail, queue='short', timeout=300, async=True, **email_args)
				else:
					msgprint(_("{0}: Employee email not found, hence email not sent").format(doc.user_id))


# Notify Manager if employee endedd 6 months -Nawa Company- by Maysaa
def notify_6month_employee():
	if frappe.defaults.get_user_default("Company") != 'Nawa':
		print str(False)
		return False

	employees = frappe.get_all("Employee Employment Detail", fields=["date_of_joining","employment_type","name","supervisor"],filters={'status':'Active'})
	for emp in employees:
		supervisor = frappe.db.get_value("Employee Personal Detail", emp.supervisor, ["user_id"],as_dict=1)
		trial_period = add_months(emp.date_of_joining,6)
		if trial_period == getdate(today()):
			print str(trial_period)
			if supervisor and supervisor.user_id:
				email_args = {
					"recipients": [supervisor.user_id ],
					"subject": 'Employee Trial Ended- {0}'.format(today()),
					"reference_doctype": 'Employee Employment Detail',
					"reference_name": emp.name
					}
				enqueue(method=frappe.sendmail, queue='short', timeout=300, async=True, **email_args)
			else:
				msgprint(_("{0}: Employee email not found, hence email not sent").format(""))


				
def notify_for_evaluation():
	m=datetime.now()
 
	if(m.month == 11 and m.day == 20):
		emps = frappe.db.get_list("Employee", ["user_id" ],filters={"company":"Nawa"})
		recipients=[]
		recipientssp=[]
		
		for emp in emps:
			eva =frappe.get_list("Evaluators" ,['name','evaluation_form'] ,filters={"employee" : emp})
			if eva[0].evaluation_form=="Normal":
				if emp.user_id:
					recipients.append(emp.user_id)
			if eva[0].evaluation_form=="Special":
				if emp.user_id:
					recipientssp.append(emp.user_id)
					
		email_args1 = {
			"recipients": recipients,
			"subject": 'Annual Evaluation',
			"reference_doctype": 'Evaluation Form',
			"reference_name": "Normal"
			}
		email_args2 = {
			"recipients": recipientssp,
			"subject": 'Annual Evaluation',
			"reference_doctype": 'Evaluation Form',
			"reference_name": "Special"
			}
		enqueue(method=frappe.sendmail, queue='short', timeout=300, async=True, **email_args1)
		enqueue(method=frappe.sendmail, queue='short', timeout=300, async=True, **email_args2)				


#To be continue by Maysaa		
def delete_cancled_records():
	return True


#get numbers of employee in a work shift
@frappe.whitelist()
def employee_shift(work_shift):
	count = 0
	employees = frappe.get_all("Employee Employment Detail", fields=["name","work_shift"],filters={'status':'Active'})
	for emp in employees:
		ws = emp.work_shift
		if ws and frappe.as_unicode(work_shift.strip()) == frappe.as_unicode(emp.work_shift.strip()):
			count += 1
	return count


@frappe.whitelist(allow_guest=True)
def add_PNW_SComponent():
	salary_component = frappe.new_doc("Salary Component")
	salary_component.update({
		"name": 'Premium nature work',
		"salary_component": _('Premium nature work'),
		"salary_component_abbr": 'PNW'
	})
	salary_component.insert()
	return "done"



@frappe.whitelist()
def get_compensatory(employee=None, start_date=None, end_date=None):
	compensatory_total_hours = 0.0
	timesheets = frappe.db.sql("select sum( td.hours ) as total_hours,t.docstatus,employee,date(from_time) as ddate,type from tabTimesheet as t join `tabTimesheet Detail` as td on t.name=td.parent and t.docstatus=1 and date(from_time) BETWEEN %(start_date)s AND DATE_ADD(%(end_date)s,INTERVAL 1 day)  group by employee,type having employee=%(employee)s and type ='compensatory' ", {'employee': employee, 'start_date': start_date, 'end_date': end_date}, as_dict=1)
	if timesheets:
		for t in timesheets:
			compensatory_total_hours += t.total_hours
	return compensatory_total_hours

@frappe.whitelist()
def get_overtime_hrs(employee=None, start_date=None, end_date=None):
	overtime_total_hours = 0.0
	overtime_count = 0.0
	timesheets = frappe.db.sql("select sum( td.hours ) as total_hours,t.docstatus,employee,date(from_time) as ddate,type from tabTimesheet as t join `tabTimesheet Detail` as td on t.name=td.parent and t.docstatus=1 and date(from_time) BETWEEN %(start_date)s AND DATE_ADD(%(end_date)s,INTERVAL 1 day)  group by employee,type having employee=%(employee)s and type !='compensatory' ", {'employee': employee, 'start_date': start_date, 'end_date': end_date}, as_dict=1)
	if timesheets :
		for t in timesheets:
			if t.total_hours >0:
				overtime_total_hours += t.total_hours
				overtime_count +=1
	return overtime_total_hours, overtime_count

@frappe.whitelist()
def get_permissions(employee=None, start_date=None, end_date=None):
	per_total_hours= 0.0
	perm = frappe.db.sql("select employee,docstatus ,permission_date ,ifnull(diff_exit,0) as diff from `tabExit permission` where type='Return' and permission_type='Exit with return' and employee = %(employee)s and date(permission_date) BETWEEN %(start_date)s AND DATE_ADD(%(end_date)s,INTERVAL 1 day) and docstatus = 1", {'employee': employee, 'start_date': start_date, 'end_date': end_date}, as_dict=1)
	if perm:
		for p in perm:
			exit_hrs = frappe.db.sql("select format(((TIME_TO_SEC('%s'))/3600),0)" %p.diff)[0][0]
			per_total_hours += float(exit_hrs)
	return per_total_hours


@frappe.whitelist()
def clear_employee_holidays(employee,shift_change_date):
	if shift_change_date:
		frappe.db.sql("update tabAttendance set docstatus=2 where employee=%s and status='On Holiday' and attendance_date >= %s",(employee,shift_change_date))
		frappe.db.sql("update tabDeparture set docstatus=2 where employee=%s and status='On Holiday' and departure_date >= %s",(employee,shift_change_date))
	

@frappe.whitelist()
def get_emp_work_shift(employee, day):
	emp_wshift = frappe.db.get_value("Employee Employment Detail", employee , "work_shift")
	if emp_wshift:
		employee_start_time = frappe.db.get_value("Work Shift Details", {"parent":emp_wshift,"day":day}, "start_work")
		employee_end_time = frappe.db.get_value("Work Shift Details", {"parent":emp_wshift,"day":day}, "end_work")
		shift_hrs = time_diff_in_hours(employee_end_time, employee_start_time)
		return shift_hrs

@frappe.whitelist()
def employee_numbers():
	count =0
	for emp_num in frappe.get_all("Employee", fields=["employee_number"]):
		count+=1
	return count


@frappe.whitelist()
def get_job_description_data(job_number, doctype='Job Description'):
	des = None 
	job_des = frappe.db.sql("""select * from `tab{0}` where name='{1}' """.format(doctype,job_number), as_dict=1)

	#job_des = frappe.db.get_value(doctype, job_number, ["special_bilities","professiona_ex","designation","department","branch"] ,as_dict=1)
	if doctype == "Planned Job" or doctype == "Unplanned Job" :
		if job_des :
			des = frappe.db.sql("""select * from `tabJob Description` where name="%s" """,job_des[0]['job_number'], as_dict=1)
			if des: des=des[0]
	if job_des: job_des = job_des[0]
	dut_res= frappe.db.get_list("Duties and Responsibilities", {"parent":job_number,"parenttype":doctype}, ["duties_and_responsibilities","performance_indicators"] )
	
	job_performance= frappe.db.get_list("Functional Specification Items", {"parent":job_number,"parenttype":doctype}, ["duties_and_responsibilities","knowledge_required","required_skills"] )

	fun_item= frappe.db.get_list("Job Performance Requirements", {"parent":job_number,"parenttype":doctype}, ["domain","description"] )

	return job_des, dut_res, fun_item ,des ,job_performance


@frappe.whitelist()
def get_job_applicant_data(job_applicant):
	return frappe.db.get_value("Job Applicant", job_applicant, "job_title" ,as_dict=1)

@frappe.whitelist()
def get_job_opening_data(job_applicant):
	job_title = frappe.db.get_value("Job Applicant", job_applicant, "job_title" ,as_dict=1)
	planned =None
	job_planned_desc  = None 
	earningss = []
	deductionss = []

	if job_title:
		job_op = frappe.db.get_value("Job Opening", job_title.job_title, ["designation","department","job_number","linked_doctype","job_type"] ,as_dict=1)
		if job_op:
			job_desc = frappe.db.get_value("Job Description", job_op.job_number, ["name","grade","basic_salary","category","salary_period","working_hours_per_day","hour_cost","monthly_work_hours","experience_year","special_bilities","professiona_ex"] ,as_dict=1)
			earnings= frappe.db.get_list("Salary Detail", {"parent":job_op.job_number,"type":"Earning"}, ["salary_component","amount"] )
			deductions= frappe.db.get_list("Salary Detail", {"parent":job_op.job_number,"type":"Deduction"}, ["salary_component","amount"] )
			
			if job_op.job_type:
				planned = frappe.db.get_value(job_op.job_type, job_op.job_number, ["name","job_number"] ,as_dict=1)
				if planned:
					job_planned_desc = frappe.db.get_value("Job Description", planned.job_number, ["name","grade","basic_salary","category","salary_period","working_hours_per_day","hour_cost","monthly_work_hours","experience_year","special_bilities","professiona_ex"] ,as_dict=1)
					earningss= frappe.db.get_list("Salary Detail", {"parent":planned.job_number,"parentfield":"earnings"}, ["salary_component","amount"] )
					deductionss= frappe.db.get_list("Salary Detail", {"parent":planned.job_number,"parentfield":"deductions"}, ["salary_component","amount"] )
		
				

		return job_op, job_desc, earnings, deductions, job_title , job_op.job_type ,planned  , job_planned_desc , earningss , deductionss

@frappe.whitelist()
def get_applicant_data(job_applicant):
	job_title = frappe.db.get_value("Job Applicant", job_applicant, "job_title" ,as_dict=1)
	if job_title:
		job_op = frappe.db.get_value("Job Opening", job_title.job_title, ["designation","department","job_number"] ,as_dict=1)
		return job_op, job_title

@frappe.whitelist()
def get_job_number_query():
	return frappe.db.sql("""select name from `tabJob Description` UNION ALL select name from  `tabPlanned Job` UNION ALL select name from  `tabUnplanned Job` """)

#def allocate_leave():
#	from erpnext.hr.doctype.leave_control_panel.leave_control_panel import allocate_leave
#	allocate_leave()

def get_company_module_roles(module):
	role = frappe.db.get_value('Companies Control Panel',frappe.defaults.get_user_default("Company"),module)
	return role

@frappe.whitelist()
def update_module_roles(projects_module):
	projects_module_roles = ""
	frappe.reload_doctype('Role')
	frappe.reload_doctype('User')
	arr = ['Guest', 'Administrator', 'System Manager', 'HR System Manager', 'All','Employee', 'HR Manager', 'HR User']
	roles = frappe.get_all("Role", fields=["name"])

	if get_company_module_roles('projects_module') == 1 or projects_module == 1:
		arr.append('Projects User')
		arr.append('Projects Manager')

	for role in roles:
		if role.name not in tuple(arr):
			frappe.set_value('Role', role.name, 'disabled', 1)
		else:
			frappe.set_value('Role', role.name, 'disabled', 0)
			print str(role.name)



