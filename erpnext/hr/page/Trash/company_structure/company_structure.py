# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, json, ast
import frappe.defaults
from frappe.utils import flt


@frappe.whitelist(allow_guest=True)
def get_tree_nodes():
	return "ss"
	


@frappe.whitelist(allow_guest=True)
def save_tree_nodes(parent,nodeid,nodename,level):
	return "done"





@frappe.whitelist(allow_guest=True)
def get_tree_category():
	catg=[]
	return catg
	




@frappe.whitelist(allow_guest=True)
def rec_get_child():
	return "dd"





