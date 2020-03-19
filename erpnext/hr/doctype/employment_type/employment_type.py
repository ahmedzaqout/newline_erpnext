# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _

from frappe.model.document import Document

class EmploymentType(Document):
	def validate(self):
		self.validate_status()

	def validate_status(self):
		if self.status == 'Not Active':
			if frappe.db.get_value('Employee', {'employment_type': self.name},'name'):	
				frappe.throw(_("Can not disactivated! There is an employee connected with this"));
