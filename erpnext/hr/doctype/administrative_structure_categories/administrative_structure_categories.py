# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class AdministrativeStructureCategories(Document):
	def validate(self):
		if self.levels < '5':
			frappe.throw(_('Levels Must be more than 5'))
		
