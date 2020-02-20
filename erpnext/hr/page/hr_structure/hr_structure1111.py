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
	levels = frappe.db.get_single_value("Administrative Structure Categories", "levels")
	if levels== 5:
		employee_parent
		

	parent=''
	headquarterdata= frappe.db.sql("""select   name , director_name as title ,tree_id as id from tabHeadquarter  where docstatus < 2 and ifnull(parent_headquarter,'') = %s""",(parent), as_dict=1)

	childdata = []
	for i in range(len(headquarterdata)):
		mybranch= frappe.db.sql("""select  name , director_name as title ,tree_id as id from `tabBranch`  where docstatus < 2 and ifnull(`parent_branch`,'') = %s""",(headquarterdata[i].name), as_dict=1)
		if mybranch:
			childdata2=[]

			for j in range(len(mybranch)):
				mymanagement= frappe.db.sql("""select  name , director_name as title ,tree_id as id from `tabManagement`  where docstatus < 2 and ifnull(`parent_management`,'') = %s""",(mybranch[j].name), as_dict=1)
				if mymanagement:
					childdata3=[]
					for c in range(len(mymanagement)):
						mycircle= frappe.db.sql("""select  name , director_name as title ,tree_id as id from `tabCircle`  where docstatus < 2 and ifnull(`parent_circle`,'') = %s""",(mymanagement[c].name), as_dict=1)
						if mycircle:
							childdata4=[]
							for d in range(len(mycircle)):
								mydep= frappe.db.sql("""select  name , director_name as title ,tree_id as id from `tabDepartment` where docstatus < 2 and ifnull(`parent_department`,'') = %s""",(mycircle[d].name), as_dict=1)
								if mydep:
									childdata5=[]
									for sd in range(len(mydep)):
										subdep=frappe.db.sql("""select employee_name as name , name as title ,tree_id as id from `tabSub Department` where docstatus < 2 and ifnull(`sdepartment`,'') = %s""",(mydep[e].name), as_dict=1)
										if subdep:
											childdata6=[]
											for se in range(len(subdep)):
												subbdep=frappe.db.sql("""select employee_name as name , name as title ,tree_id as id from `tabEmployee` where docstatus < 2 and ifnull(`department`,'') = %s""",(subdep[e].name), as_dict=1)
												if subbdep:
													childdata7=[]
													for e in range(len(subbdep)):
														emp=frappe.db.sql("""select employee_name as name , name as title ,tree_id as id from `tabEmployee` where docstatus < 2 and ifnull(`department`,'') = %s""",(subbdep[e].name), as_dict=1)
														if emp:
															data7={'name':subbdep[e].name,'title':subbdep[e].title,'id':subbdep[e].id,'children':emp}
															childdata7.append(data7)
														else:
															data7={'name':subbdep[e].name,'title':subbdep[e].title,'id':subbdep[e].id,'children':emp}
															childdata7.append(data7)

													data6={'name':subdep[e].name,'title':subdep[e].title,'id':subdep[e].id,'children':subbdep}
													childdata6.append(data6)
												else:
													data6={'name':subdep[e].name,'title':subdep[e].title,'id':subdep[e].id,'children':subbdep}
													childdata6.append(data6)
												
											data5={'name':mydep[e].name,'title':mydep[e].title,'id':mydep[e].id,'children':subdep}
											childdata5.append(data5)
										else:
											data5={'name':mydep[e].name,'title':mydep[e].title,'id':mydep[e].id}
											childdata5.append(data5)

									data4={'name':mycircle[d].name,'title':mycircle[d].title,'id':mycircle[d].id,'children':childdata5}
									childdata4.append(data4)
								else:
									data4={'name':mycircle[d].name,'title':mycircle[d].title,'id':mycircle[d].id}
									childdata4.append(data4)
								
							
							data3={'name':mymanagement[c].name,'title':mymanagement[c].title,'id':mymanagement[c].id,'children':childdata4}
							childdata3.append(data3)
							
						else:
							data3={'name':mymanagement[c].name,'title':mymanagement[c].title,'id':mymanagement[c].id}
							childdata3.append(data3)
					

				
					data2={'name':mybranch[j].name,'title':mybranch[j].title,'id':mybranch[j].id,'children':childdata3}
					childdata2.append(data2)
				else:
					
					data2={'name':mybranch[j].name,'title':mybranch[j].title,'id':mybranch[j].id}
					childdata2.append(data2)
					
			data={'name':headquarterdata[i].name,'title':headquarterdata[i].title,'id':headquarterdata[i].id,'children':childdata2}
			childdata.append(data)

				
		else:
			data={'name':headquarterdata[i].name,'title':headquarterdata[i].title,'id':headquarterdata[i].id}
			childdata.append(data)
	

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
	#data = ast.literal_eval(tree)
	#ids = list(find('id',data))
	#levels = list(find('level',data))
	#parent_id = frappe.get_value('Headquarter',parent,'tree_id');
	if level =='0':
		#save_node(doc,name,parent)
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

	if level =='1':
		doc = frappe.new_doc('Branch')
		doc.update({
			"branch":nodename,
			"branch_en":nodename,
			"parent":parent,
			"is_group": '1',
			"parent_branch":parent,
			"director":'mm',
			"tree_id":nodeid
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	if level =='2':
		doc = frappe.new_doc('Management')
		doc.update({
			"management":nodename,
			"management_en":nodename,
			"parent":parent,
			"is_group": '1',
			"parent_management":parent,
			"director":'mm',
			"tree_id":nodeid
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	if level =='3':
		doc = frappe.new_doc('Circle')
		doc.update({
			"circle":nodename,
			"circle_en":nodename,
			"parent":'root',
			"is_group": '1',
			"parent_circle":parent,
			"director":'mm',
			"tree_id":nodeid
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	if level =='4':
		doc = frappe.new_doc('Department')
		doc.update({
			"department_name":nodename,
			"department_name_en":nodename,
			"parent":parent,
			"is_group": '1',
			"parent_department":parent,
			"director":'mm',
			"tree_id":nodeid
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	if level =='5':
		doc = frappe.new_doc('Employee')
		doc.update({
			"employee_name":nodename,
			"name":nodename,
			"department":parent,
			"supervisor":'mm',
			"tree_id":nodeid
		})
		doc.flags.ignore_links = True
		doc.flags.ignore_mandatory = True
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
	if frappe.db.get_single_value("Administrative Structure Categories", "link_3"): catg.append('Headquarter')
	else: catg.append('')
	if frappe.db.get_single_value("Administrative Structure Categories", "link_4"): catg.append('Branch')
	else:catg.append('')
	if frappe.db.get_single_value("Administrative Structure Categories", "link_5"): catg.append('Management')
	else:catg.append('')
	if frappe.db.get_single_value("Administrative Structure Categories", "link_6"): catg.append('Circle')
	else:catg.append('')
	if frappe.db.get_single_value("Administrative Structure Categories", "link_7"): catg.append('Department')
	else:catg.append('')
	if frappe.db.get_single_value("Administrative Structure Categories", "link_8"): catg.append('Sub-Department')
	else:catg.append('')
	if frappe.db.get_single_value("Administrative Structure Categories", "link_9"): catg.append('')
	else:catg.append('')
	if frappe.db.get_single_value("Administrative Structure Categories", "link_10"): catg.append('')
	else:catg.append('')
	return catg
	
