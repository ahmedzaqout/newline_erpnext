# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class ShiftTime(Document):
	def validate(self):
		if self.start_time > self.end_time and not self.next_day:
			frappe.throw(_("Start time cant be greater than end time unless its in the next day"))
