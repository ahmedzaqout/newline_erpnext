# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class EmployeeInsurance(Document):
	pass

@frappe.whitelist()
def get_insurance_deduction():
	return frappe.db.get_single_value("HR Settings", "insurance_deduction")

@frappe.whitelist()
def get_insurance_allowance():
	return frappe.db.get_single_value("HR Settings", "insurance_allowance")
