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
def get_addreses():
	result={}
	lab=[]
	cities=frappe.get_list("City",['name'])
	for city in cities:
		lab.append(city.name);
	values=[]
	for i  in range(len(lab)):
		em=frappe.get_list("Employee Contact Details",['name'],filters={"city":lab[i]})
		if em:
			values.append(len(em))
		else:
			values.append(0)
	return {
		"labels" : lab,
		"values" : values
	}

	
