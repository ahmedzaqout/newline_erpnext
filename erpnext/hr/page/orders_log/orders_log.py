# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, json, ast
import frappe.defaults
from frappe.utils import flt
import datetime, calendar, time
from frappe.utils import getdate, nowdate,get_time, time_diff,time_diff_in_seconds,get_datetime,cint, time_diff_in_hours



@frappe.whitelist(allow_guest=True)
def get_data(user):
	edit_time_orders ,timesheet,permission_orders, leave_orders = [], [], [], [];
	employee_id= frappe.db.get_value('Employee', {'user_id':user},'employee')
	if employee_id:
		edit_time_orders= frappe.db.sql("select attendance_date,attendance_time,departure_time,docstatus from `tabEmployee Edit Time` where employee=%s and docstatus <2 order by attendance_date desc limit 50" ,employee_id, as_dict=1)

		timesheet = frappe.db.sql("select end_date,start_date,(select DISTINCT target_name from tabTranslation where source_name=type) as type,docstatus,total_hours from `tabTimesheet` where employee=%s and docstatus <2 order by start_date desc limit 50" ,employee_id, as_dict=1)

		permission_orders = frappe.db.sql("select permission_date,(select DISTINCT target_name from tabTranslation where source_name=permission_type) as permission_type,from_date ,to_date,docstatus from `tabExit permission` where employee=%s and docstatus <2 order by permission_date desc limit 50" ,employee_id, as_dict=1)
		
		leave_orders = frappe.db.sql("select * from `tabLeave Application` where employee=%s and docstatus <2 order by from_date desc limit 50" ,employee_id, as_dict=1)

	data = [edit_time_orders,timesheet,permission_orders, leave_orders]
	return data

