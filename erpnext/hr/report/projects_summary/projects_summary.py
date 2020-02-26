# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _
import datetime, calendar, time 
from calendar import monthrange
from datetime import date



def execute(filters=None):
	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	data = get_Data(conditions, filters)
	return columns, data

def get_columns(filters):
	columns = [
		 {"label":_("Project") ,"width":80,"fieldtype": "Data"},
		 {"label":_("Period") ,"width":120,"fieldtype": "Data"},
		 {"label":_("Start Date") ,"width":160,"fieldtype": "Date"},
		 {"label":_("End Date") ,"width":80,"fieldtype": "Date"},
		 {"label":_("Latness") ,"width":90,"fieldtype": "Float"},
		 {"label":_("Team Members") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Specialization") ,"width":90,"fieldtype": "Data"},
		 {"label":_("Member Time") ,"width":100,"fieldtype": "Float"},
		 {"label":_("Member All Time") ,"width":100,"fieldtype": "Float"},
		 {"label":_("Closed") ,"width":110,"fieldtype": "Data"},
		 {"label":_("Total Hours") ,"width":70,"fieldtype": "Float"},
		 {"label":_("Total Hours After Maintainance") ,"width":70,"fieldtype": "Float"}
	]
	return columns
def get_conditions(filters):

	conditions = ""
	if filters.get("project"): conditions += " and name = %(project)s"
	
	return conditions, filters

def get_Data(conditions, filters):
	data=[]
	projects  = frappe.db.sql("""select  name,status,work_days,maintenance_start_date, maintenance_end_date  from `tabProject` where 1=1 %s order by name """% conditions, filters, as_dict=1)
	#frappe.msgprint(str(emp_map))
	for pro in projects:
		first_last= frappe.db.sql("""select min(et.date) as first ,max(et.date) as last,ifnull( GREATEST(round(TIMESTAMPDIFF(MINUTE,min(et.date),max(et.date))/60,2),0),0)  as real_work from `tabActivity Detail` as ad left join `tabEmployee Task` as et on ad.parent= et.name  where et.docstatus <2 and ad.project = %(project)s  and et.date < %(main)s """ ,{"project" :pro.name ,"main": pro.maintenance_start_date}, as_dict=1)
		
		first_last_after= frappe.db.sql("""select min(et.date) as first ,max(et.date) as last,ifnull( GREATEST(round(TIMESTAMPDIFF(MINUTE,min(et.date),max(et.date))/60,2),0),0)  as real_work from `tabActivity Detail` as ad left join `tabEmployee Task` as et on ad.parent= et.name  where et.docstatus <2 and ad.project = %(project)s and et.date >= %(main)s """ ,{"project" :pro.name,"main": pro.maintenance_start_date}, as_dict=1)
		row=[pro.name,pro.work_days]
		first=None
		last=None
		if first_last:
			if first_last[0]['first']:
				first=first_last[0]['first'].strftime("%Y-%m-%d")
				row.append(first)
			else:
				row.append("")
			if first_last[0]['last']:
				last=first_last[0]['last'].strftime("%Y-%m-%d")
				row.append(last)
			else:
				row.append("")

		if first_last:
			latt =0
			if pro.work_days > 0:
				latt = (first_last[0].real_work/24) - get_holiday(last,first) -pro.work_days 

			if latt < 0:
				latt=0
			row.append(latt)
		else:
			row.append(0)
		users=frappe.get_list("Project User",["user","s_time","employee_name", "specialization","s_time" ],filters={"parent" : pro.name})
		totreal=0
		totreal_no_main=0
		ext_rows=[]
		flag=False
		if users:
			totreal=0
			totalexp=0
			totdiff=0
			i = 0

			for user in users:
				use=frappe.get_list("Project User",["user","employee_name","s_time" ],filters={"user" : user['user'],"parent" : pro.name})			
				tot=0	
				tot_no_main =0
				if len(use)<2:
					dss  = frappe.db.sql("""select ad.hours,et.employee, et.employee_name from `tabActivity Detail` as ad left join `tabEmployee Task` as et on ad.parent= et.name  where et.docstatus <2 and ad.project = %(project)s  and et.employee=%(employee)s and et.date < %(main)s  order by et.employee """ ,{"project" :pro.name ,"employee": user['user'],"main": pro.maintenance_start_date}, as_dict=1)


					first_last_em= frappe.db.sql("""select min(et.date) as first ,max(et.date) as last,ifnull( GREATEST(round(TIMESTAMPDIFF(MINUTE,min(et.date),max(et.date))/60,2),0),0)  as real_work from `tabActivity Detail` as ad left join `tabEmployee Task` as et on ad.parent= et.name  where et.docstatus <2 and ad.project = %(project)s  and et.date < %(main)s and et.employee=%(employee)s """ ,{"project" :pro.name ,"main": pro.maintenance_start_date,"employee": user['user']}, as_dict=1)

					dss_no_main  = frappe.db.sql("""select ad.hours,et.employee, et.employee_name from `tabActivity Detail` as ad left join `tabEmployee Task` as et on ad.parent= et.name  where et.docstatus <2 and ad.project = %(project)s  and et.employee=%(employee)s  order by et.employee """ ,{"project" :pro.name ,"employee": user['user']}, as_dict=1)


					first_last_em_no_main= frappe.db.sql("""select min(et.date) as first ,max(et.date) as last,ifnull( GREATEST(round(TIMESTAMPDIFF(MINUTE,min(et.date),max(et.date))/60,2),0),0)  as real_work from `tabActivity Detail` as ad left join `tabEmployee Task` as et on ad.parent= et.name  where et.docstatus <2 and ad.project = %(project)s   and et.employee=%(employee)s """ ,{"project" :pro.name ,"employee": user['user']}, as_dict=1)

					for a in dss:							
						tot+= float(a['hours']) 
					
					for a in dss_no_main:							
						tot_no_main+= float(a['hours']) 
				else:

					ss  = frappe.db.sql("""select ad.hours,et.employee, et.employee_name from `tabActivity Detail` as ad left join `tabEmployee Task` as et on ad.parent= et.name  where et.docstatus <2 and ad.project = %(project)s  and et.employee=%(employee)s and ad.specialization = %(specialization)s and et.date < %(main)s order by et.employee """ ,{"project" :pro.name ,"employee": user['user'],"specialization":user['specialization'],"main": pro.maintenance_start_date}, as_dict=1)
					
					first_last_em= frappe.db.sql("""select min(et.date) as first ,max(et.date) as last,ifnull( GREATEST(round(TIMESTAMPDIFF(MINUTE,min(et.date),max(et.date))/60,2),0),0)  as real_work from `tabActivity Detail` as ad left join `tabEmployee Task` as et on ad.parent= et.name  where et.docstatus <2 and ad.project = %(project)s  and et.date < %(main)s and et.employee=%(employee)s and ad.specialization = %(specialization)s """ ,{"project" :pro.name ,"main": pro.maintenance_start_date,"employee": user['user'],"specialization":user['specialization']}, as_dict=1)

					ss_no_main  = frappe.db.sql("""select ad.hours,et.employee, et.employee_name from `tabActivity Detail` as ad left join `tabEmployee Task` as et on ad.parent= et.name  where et.docstatus <2 and ad.project = %(project)s  and et.employee=%(employee)s and ad.specialization = %(specialization)s order by et.employee """ ,{"project" :pro.name ,"employee": user['user'],"specialization":user['specialization']}, as_dict=1)
					
					first_last_em_no_main  = frappe.db.sql("""select min(et.date) as first ,max(et.date) as last,ifnull( GREATEST(round(TIMESTAMPDIFF(MINUTE,min(et.date),max(et.date))/60,2),0),0)  as real_work from `tabActivity Detail` as ad left join `tabEmployee Task` as et on ad.parent= et.name  where et.docstatus <2 and ad.project = %(project)s  and et.employee=%(employee)s and ad.specialization = %(specialization)s """ ,{"project" :pro.name ,"employee": user['user'],"specialization":user['specialization']}, as_dict=1)

					
					
					for a in ss:							
						tot+= float(a['hours']) 
					for a in ss_no_main:							
						tot_no_main+= float(a['hours']) 

				
				emp_first=""
				emp_last=""

				if first_last_em:
					if first_last_em[0]['first']:
						emp_first=first_last_em[0]['first'].strftime("%Y-%m-%d")
					
					if first_last_em[0]['last']:
						emp_last=first_last_em[0]['last'].strftime("%Y-%m-%d")
					
							
				lat_emp= 0
				if tot >user['s_time']:
					lat_emp= tot -	user['s_time']
				if filters.get("employee"):
					if user['user'] == filters.get("employee"):
						ext_rows.append(["",user['s_time'] ,emp_first,emp_last,lat_emp,user['employee_name'],user['specialization'],tot,tot_no_main,""])
						flag=True
					else:
						
						continue;
						
				else:		
						ext_rows.append(["",user['s_time'] ,emp_first,emp_last,lat_emp,user['employee_name'],user['specialization'],tot,tot_no_main,""])
				i +=1
				totreal+=tot
				totreal_no_main +=tot_no_main
		row.append("")
		row.append("")
		row.append("")
		row.append("")
		status="Open"
		if first_last[0]['last']:
			if (first_last[0]['last']-date.today()).days > 30:
				status="Closed"
			else:
				status="Open"
		
		row.append(status)


		row.append(totreal)
		row.append(totreal_no_main)
		if filters.get("employee"):
			if flag:
				data.append(row)
				data=data + ext_rows
		else:				
			data.append(row)
			data=data + ext_rows

				
		
	return data
def get_holiday(from_date, to_date):
	company=frappe.db.get_value("Global Defaults", None, "default_company")
	holiday_list = frappe.db.get_value("Company", company ,["default_holiday_list"],
		as_dict=True)

	holidays = frappe.db.sql("""select count(distinct holiday_date) from `tabHoliday` h1, `tabHoliday List` h2
		where h1.parent = h2.name and h1.holiday_date between %s and %s
		and h2.name = %s""", (from_date, to_date, holiday_list.default_holiday_list))[0][0]

	return holidays


