# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe , re
from frappe import _,throw
from frappe.utils import getdate,now,get_datetime

def set_employee_name(doc):
	if doc.employee and not doc.employee_name:
		doc.employee_name = frappe.db.get_value("Employee", doc.employee, "employee_name")


@frappe.whitelist()
def notify_manpower_planning_date():
	import datetime
	now = datetime.date.today()
	manpower_planning_date = frappe.db.get_single_value("HR Settings", "manpower_planning_date")
	if  now.day == get_datetime(manpower_planning_date).day and now.month == get_datetime(manpower_planning_date).month :	

		company =frappe.db.get_value("Global Defaults", None, "default_company")
		manager = frappe.db.get_value("Headquarter", company+' - HEQ', "director")
		manager_email = frappe.db.get_value("Employee Personal Detail", manager, "user_id")
		contact = manager_email #'maysaaelsafadi@gmail.com'
		if not isinstance(contact, list):
			#contact = frappe.get_doc('User', contact).email or contact
			sender      	    = dict()
			sender['email']     = frappe.get_doc('User', frappe.session.user).email
			sender['full_name'] = frappe.utils.get_fullname(sender['email'])
	
			try:
				frappe.sendmail(
					recipients = contact,
					sender = sender['email'],
					subject = _('Manpower Planning Expiry Date'),
					message = _('Manpower Planning Expiry Date'),
				)
				frappe.msgprint(_("Email sent to {0}").format(contact))
			except frappe.OutgoingEmailError:
				pass 
@frappe.whitelist()
def validate_only_arabic(ar_field):
	rule = re.compile(ur'(^[ء-ي  -]+$)')
	myFields = {ar_field}
	for fi in myFields:
		if fi:
			if not rule.search(fi):
				frappe.throw(_("{0} Bad Entry in Arabic name").format(fi))

@frappe.whitelist()
def validate_only_english(en_field):
	rule = re.compile(ur'(^[A-Za-z \- -dat]+$)')
	myFields = {"en_field" : en_field}
	for key,value in myFields.items():
		if value:
			if not rule.search(value):
				frappe.throw(_("{0} Bad Entry in English name").format(value))



