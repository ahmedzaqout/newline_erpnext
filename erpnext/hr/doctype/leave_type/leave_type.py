# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.model.document import Document
from frappe.model.naming import make_autoname


class LeaveType(Document):
	def autoname(self):
		self.name = self.leave_name