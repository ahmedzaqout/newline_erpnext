# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import datetime

@frappe.whitelist(allow_guest=True)
def get_att(employee=None):
	d = datetime.date.today()
	mon=d.month
	dayy=d.day
	y=d.year
	start=1
	if dayy<13:
		start=1
	 	end=12
	else:
		start=dayy-12
	 	end=dayy

	print mon
	print start
	print y
	print end


	start_day=datetime.date(y,mon,start)
	end_day=datetime.date(y,mon,end)
	print start_day
	print end_day



	emp_map  = frappe.db.sql("""select  emp.name,emp.employee ,emp.status as statuss,circle,department, att.attendance_date,dept.departure_date, DAYNAME(att.attendance_date) as day,att.attendance_time, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as total_hours ,emp.total_work_hrs,overtime_hours,tsh.start_date ,att.status,start_work, ext.early_diff as early_departure,ext.ext_diff as ext_diff, work_shift, emp.holiday_list,ifnull(round(TIMESTAMPDIFF(MINUTE,start_work,att.attendance_time)/60,2),0) as late_hrs from tabEmployee as emp   
join  tabAttendance as att on att.employee=emp.employee  and att.docstatus = 1
left join  tabDeparture as dept on dept.employee=emp.employee and att.attendance_date=dept.departure_date and dept.docstatus = 1
left join ( select docstatus,employee,start_date,ifnull(round(sum(total_hours),2),0) as overtime_hours from tabTimesheet group by start_date,employee) as tsh on emp.employee=tsh.employee and att.attendance_date=tsh.start_date and tsh.docstatus = 1 
left join (select employee,docstatus, permission_date,sum(early_diff)/60 as early_diff, sum(diff) as ext_diff from (
select employee,docstatus, permission_date,early_diff, 0 as diff from `tabExit permission` where permission_type='Early Departure'
union all 
select employee,docstatus, permission_date,0 as early_diff ,diff_exit as diff from `tabExit permission` where type='Return' and permission_type='Exit with return') as d group by permission_date,employee) as ext 
on emp.employee=ext.employee and att.attendance_date=ext.permission_date and ext.docstatus < 2 
where  emp.employee = %s and  att.attendance_date >= %s and att.attendance_date <= %s order by emp.employee, attendance_date""" 
,(employee,str(start_day), str(end_day)), as_dict=1)
		
	att=[]
	for em in emp_map:
		if em.total_hours:
			total= em.total_hours
		else: 
			total= 0.0
		if em.ext_diff:
			total-=em.ext_diff
		if em.overtime_hours:
			total+=em.overtime_hours
		if total<0:
			total=0

		row={"day":str(em.attendance_date),
		"total_hours": em.total_hours,
		"total_working" : total
		}
		att.append(row)
	print att
	return att;

