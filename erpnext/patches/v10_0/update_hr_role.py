# Copyright (c) 2017, Frappe and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute():
	frappe.reload_doctype('Role')
	frappe.reload_doctype('User')
	roles = frappe.get_all("Role", fields=["name"])
	for role in roles:
		if role.name not in (_('Guest'), _('Administrator'), _('System Manager'), _('HR System Manager'), _('All'),_('Employee'), _('HR Manager'), _('HR User'),_('Projects User'),_('Projects Manager'),'Guest', 'Administrator', 'System Manager', 'HR System Manager', 'All','Employee', 'HR Manager', 'HR User','Projects User','Projects Manager' ):
			#if frappe.db.exists('Role', role_name) and role_name != role.name:
			frappe.set_value('Role', role.name, 'disabled', 1)
			frappe.set_value('Role', role.name, 'hr_role', 0)



