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
def get_details():
	result={}
	ss  = frappe.db.sql("""select emp.name ,emp.image,emp.employee_name, ed.* from `tabEmployee` as emp join `tabEmployee Employment Detail` as ed  on emp.name=ed.employee left Join `tabEmployee Contact Details` as cd on 					emp.name=cd.employee left join `tabEmployee Personal Detail` as pd on  					emp.name=pd.employee where emp.docstatus <2  order by emp.employee """ , as_dict=1)
	values=[]
	for i in ss:
		row={"image":i.image,"employee":i.employee,"employee_name":i.employee_name,"department":i.department,"designation":i.designation,"company":i.company}
		values.append(row);

	return {
		"values" : values
	}

	







