# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, json, ast
import frappe.defaults
from frappe.utils import flt


@frappe.whitelist(allow_guest=True)
def get_tree_nodes():
	company =frappe.db.get_value("Global Defaults", None, "default_company")
	if not frappe.db.get_value('Headquarter',company+' - HEQ','name'):
		doc = frappe.new_doc('Headquarter')
		doc.update({
			"headquarter":company,
			"headquarter_en":company,
			"parent":'',
			"is_group": '1',
			"parent_headquarter":'',
			"director":'mm',
			"tree_id":'1'
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	parent=''
	headquarterdata= frappe.db.sql("""select node_name as name , director_name as title ,node_id as id from `tabHR Structure`  where docstatus < 2 and ifnull(node_parent,'') = %s""",(parent), as_dict=1)

	childdata = []
	for i in range(len(headquarterdata)):
		mybranch= frappe.db.sql("""select  name , director_name as title ,tree_id as id from `tabBranch`  where docstatus < 2 and ifnull(`parent_branch`,'') = %s""",(headquarterdata[i].name), as_dict=1)
		#if mybranch:


	jsondata={'name':'root','id':1,'children':childdata}

	return childdata[0]
	


def get_child(query,doctype,fieldname):
	childdata=[]
	for i in range(len(query)):
		query_data= frappe.db.sql("""select name , name as title ,tree_id as id from `tab{doctype}`  where docstatus < 2 and ifnull(`parent_{fieldname}`,'') = %s""".format(doctype=doctype, fieldname=fieldname),(query[i].name), as_dict=1)
		if query_data:
			pid = frappe.get_value(doctype,query[i].name,'tree_id');
			data={'name':query[i].name,'title':query[i].title,'id':query[i].id,'children':query_data}
			childdata.append(data)
			i=i+1
		else:  
			data={'name':query[i].name,'title':query[i].title,'id':query[i].id}
			childdata.append(data)

	return childdata


@frappe.whitelist(allow_guest=True)
def save_tree_nodes(parent,nodeid,nodename,level):
	if level =='0':
		doc = frappe.new_doc('Headquarter')
		doc.update({
			"headquarter":nodename,
			"headquarter_en":nodename,
			"parent":'root',
			"is_group": '1',
			"parent_headquarter":'root',
			"director":'mm',
			"tree_id":nodeid
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	return "done"


@frappe.whitelist(allow_guest=True)
def drag_drop_node(dragged,dropped,level):
	if level == '6':
		frappe.db.sql("""update tabEmployee set department=%s where name=%s""",(dropped,dragged), as_dict=1)
		return "dropped"

def extract_json(data,arr):
	for k in data:
        	if k == 'id':
            		arr.append( data['id'])
        	elif k == 'children':
            		for result in data['children']:
            			arr.append(result['id'])
				extract_json(result['children'],arr)	
	return arr




@frappe.whitelist(allow_guest=True)
def find(key,dictionary):
	for k, v in dictionary.iteritems():
        	if k == key:
            		yield v
        	elif isinstance(v, dict):
            		for result in find(key, v):
                		yield result
        	elif isinstance(v, list):
            		for d in v:
                		for result in find(key, d):
                    			yield result


@frappe.whitelist(allow_guest=True)
def delete_node(node,level):
	if level == '1':
		frappe.db.sql("""delete from `tabHeadquarter` where name = %s""", node)
	if level == '2':
		frappe.db.sql("""delete from `tabBranch` where name = %s""", node)
	if level == '3':
		frappe.db.sql("""delete from `tabManagement` where name = %s""", node)
	if level == '4':
		frappe.db.sql("""delete from `tabCircle` where name = %s""", node)
	if level == '5':
		frappe.db.sql("""delete from `tabDepartment` where name = %s""", node)
	if level == '6':
		frappe.db.sql("""delete from `tabEmployee` where name = %s""", node)
	return level



@frappe.whitelist(allow_guest=True)
def get_emp_user(emp=None):
	if emp:
		return frappe.db.get_value("Employee", emp, "user_id")





@frappe.whitelist(allow_guest=True)
def get_tree_category():
	catg=[]
	if frappe.db.get_single_value("Administrative Structure Categories", "cat_check1"): catg.append('Headquarter')
	else: catg.append('')
	if frappe.db.get_single_value("Administrative Structure Categories", "cat_check2"): catg.append('Branch')
	else:catg.append('')
	if frappe.db.get_single_value("Administrative Structure Categories", "cat_check3"): catg.append('Management')
	else:catg.append('')
	if frappe.db.get_single_value("Administrative Structure Categories", "cat_check4"): catg.append('Circle')
	else:catg.append('')
	if frappe.db.get_single_value("Administrative Structure Categories", "cat_check5"): catg.append('Department')
	else:catg.append('')
	if frappe.db.get_single_value("Administrative Structure Categories", "cat_check6"): catg.append('Sub-Department')
	else:catg.append('')
	if frappe.db.get_single_value("Administrative Structure Categories", "cat_check7"): catg.append('')
	else:catg.append('')
	if frappe.db.get_single_value("Administrative Structure Categories", "cat_check8"): catg.append('')
	else:catg.append('')
	return catg
	



@frappe.whitelist(allow_guest=True)
def get_children1( parent='', **filters):
 	root  = frappe.db.sql("""select node_name as name , director_name as title ,node_id as id from `tabHR Structure`  where docstatus < 2 and ifnull(node_parent,'') = ''""", as_dict=1)
	get_children(root)

@frappe.whitelist(allow_guest=True)
def get_children(qry, parent='', **filters):

	return frappe.db.sql("""select node_name as value, node_name as title,
		1 as expandable
		from `tabHR Structure`
		where docstatus < 2
		and ifnull(`node_parent`,'') = %s
		order by name""",qry[0].name, as_dict=1)



