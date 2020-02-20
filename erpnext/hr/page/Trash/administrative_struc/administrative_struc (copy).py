# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import frappe.defaults
from frappe.utils import flt
from erpnext.accounts.utils import get_balance_on
from erpnext.accounts.report.financial_statements import sort_root_accounts


@frappe.whitelist()
def add_node(level,code,branch,branch_en,parent_branch,is_group,department_name,parent_department,department_name_en):
	ctype = frappe.form_dict.get('ctype')

	if level=='1':
		doc = frappe.new_doc('Headquarter')
		doc.update({
			'headquarter_en': branch_en,
			'headquarter':branch, 
			'parent_headquarter':parent_branch,
			"parent":parent_branch,
			"is_group": is_group
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	elif level=='2':
		doc = frappe.new_doc('Branch')
		doc.update({
			'code': code,
			'branch_en': branch_en,
			'branch':branch, 
			'parent_branch':parent_branch,
			"parent":parent_branch,
			"is_group": is_group
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	else:
		doc = frappe.new_doc('Department')
		doc.update({
			'code': code,
			"department_name":department_name,
			"department_name_en":department_name_en,
			"parent":parent_department,
			"is_group": is_group ,
			"parent_department":parent_department 
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

        


@frappe.whitelist()
def get_children():
	ctype = frappe.local.form_dict.get('ctype')
	parent_field = 'parent_department'
	parent = frappe.form_dict.get("parent") or ""
	return frappe.db.sql("""select name as value,is_group as expandable ,code from tabBranch where docstatus < 2 and ifnull(parent_branch,'') = %s  union all  select name as value,is_group as expandable, code from tabDepartment  where docstatus < 2 and ifnull(parent_department,'') = %s""",(parent,parent), as_dict=1)


@frappe.whitelist()
def get_branch_num(branch):
	return frappe.db.get_value("Branch", branch, "branch_number")
           
     

        

@frappe.whitelist()
def get_branch_name(name):
	
	query = """select branch,parent_branch from `tabBranch` where name = %(name)s """
	
	data={
	"name":name
		}
	
	branch_name = frappe.db.sql(query,data)[0]

	if branch_name:
		return branch_name


# *************************************Maysaa updates13072017**************************
@frappe.whitelist()
def get_account_level(cur_parent):
	parent_department = 'parent_department'

	level = 1
	while cur_parent:
		parent_acc =frappe.db.sql("""select {parent_department} from `tabDepartment` where name =%s """.format(parent_department=parent_department),(cur_parent));
		if parent_acc:
			level = level + 1
			cur_parent=parent_acc[0][0]
		else:
			return level

	print str(level)+"@@@@@@@@@@@@@@@@"+str(cur_parent)
	return level


			

