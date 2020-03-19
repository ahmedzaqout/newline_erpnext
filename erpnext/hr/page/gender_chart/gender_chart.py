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
def get_gender():
	result={}
	gnd=frappe.get_list("Gender",['name'])
	genderList=[]
	values=[]
	for g in gnd:
		genderList.append(g.name)
		em=frappe.get_list("Employee",['name'],filters={"gender":g.name})
		if em:
			values.append(len(em))
		else:
			values.append(0)
	return {
		"labels" : genderList,
		"values" : values
	}

	
