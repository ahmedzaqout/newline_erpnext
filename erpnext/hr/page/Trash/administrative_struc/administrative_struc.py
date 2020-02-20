# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import frappe.defaults
from frappe.utils import flt


@frappe.whitelist()
def add_node(entry_type,name,name_en,parent,is_group,director,company):
	ctype = frappe.form_dict.get('ctype')

	if entry_type=='Headquarter':
		doc = frappe.new_doc('Headquarter')
		doc.update({
			'headquarter_en': name_en,
			'headquarter':name, 
			'parent_headquarter':parent,
			"parent":parent,
			"is_group": is_group,
			"director":director,
			"company":company
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	elif entry_type=='Branch':
		doc = frappe.new_doc('Branch')
		doc.update({
			'branch_en': name_en,
			'branch':name, 
			'parent_branch':parent,
			"parent":parent,
			"is_group": is_group,
			"director":director,
			"company":company
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	elif entry_type=='Management':
		doc = frappe.new_doc('Management')
		doc.update({
			"management":name,
			"management_en":name_en,
			"parent":parent,
			"is_group": is_group ,
			"parent_management":parent ,
			"director":director,
			"company":company
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	elif entry_type=='Circle':
		doc = frappe.new_doc('Circle')
		doc.update({
			"circle":name,
			"circle_en":name_en,
			"parent":parent,
			"is_group": is_group ,
			"parent_circle":parent ,
			"director":director,
			"company":company
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)


	elif entry_type=='Department':
		doc = frappe.new_doc('Department')
		doc.update({
			"department_name":name,
			"department_name_en":name_en,
			"parent":parent,
			"is_group": is_group ,
			"parent_department":parent,
			"director":director
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)


        


@frappe.whitelist()
def get_children():
	ctype = frappe.local.form_dict.get('ctype')
	parent = frappe.form_dict.get("parent") or ""
	return frappe.db.sql("""select name as value, is_group as expandable,1 as level from tabHeadquarter where docstatus < 2 and ifnull(parent_headquarter,'') = %s union all select name as value,is_group as expandable, 2 as level from tabBranch where docstatus < 2  and ifnull(parent_branch,'') = %s   union all select name as value,is_group as expandable, 3 as level from tabManagement  where docstatus < 2  and ifnull(parent_management,'') = %s union all select name as value,is_group as expandable, 4 as level from tabCircle  where docstatus < 2 and ifnull(parent_circle,'') = %s union all select name as value,is_group as expandable, 5 as level from tabDepartment  where docstatus < 2 and ifnull(parent_department,'') = %s""",(parent,parent,parent,parent,parent), as_dict=1)

@frappe.whitelist()
def get_account_level(cur_parent):
	pass

