# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class OtherOrder(Document):
	def autoname(self):
		keys = filter(None, ((self.order_name).strip(), (self.employee).strip()))
		self.name = make_autoname(self.order_name+'_'+self.employee + '/.#####')
