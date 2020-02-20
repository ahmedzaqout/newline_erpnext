# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ClientModulesSetup(Document):
	def set_site(self):
		site = frappe.get_doc("Site",self.site)
	        if site and not site.client_modules_setup:
			site.update({
				'client_modules_setup':self.site
			})
			site.flags.ignore_validate = True
			site.save(ignore_permissions=True)

