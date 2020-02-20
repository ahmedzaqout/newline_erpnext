# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import date_diff

class StateHoliday(Document):
	def validate(self):
		self.total_days = date_diff(self.to_date, self.from_date) + 1
