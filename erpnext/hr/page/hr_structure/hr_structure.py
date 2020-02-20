# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, json, ast
import frappe.defaults
from frappe.utils import flt
from frappe import throw, _

@frappe.whitelist(allow_guest=True)
def get_tree_nodes():
	company =frappe.db.get_value("Global Defaults", None, "default_company")
	if not frappe.db.get_value('Headquarter',company+' - HEQ','name'):
		doc = frappe.new_doc('Headquarter')
		doc.update({
			"headquarter":company,
			#"headquarter_en":company,
			"parent":'',
			"is_group": '1',
			"parent_headquarter":'',
			"director":'',
			"tree_id":'1'
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	levels = frappe.db.get_single_value("Administrative Structure Categories", "levels")

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
									##
									childdata5=[]
									for sd in range(len(mydep)):
										#####
										subdep=frappe.db.sql("""select  name , director_name as title ,tree_id as id from `tabSub Department` where docstatus < 2 and ifnull(`parent_sub_department`,'') = %s""",(mydep[sd].name), as_dict=1)
																						
										if subdep and levels == '6' or  subdep and levels == '7':
											childdata6=[]
											for se in range(len(subdep)):
												subbdep=frappe.db.sql("""select name , director_name as title ,tree_id as id from `tabSub Association` where docstatus < 2 and ifnull(`parent_sub_association`,'') = %s""",(subdep[se].name), as_dict=1)
												childdata7=[]
												if subbdep and levels == '7':
													if levels == '7':
														childdata7= get_emp_children(subbdep)			
													
													data6={'name':subdep[se].name,'title':subdep[se].title,'id':subdep[se].id,'children':childdata7,'className': 'dep'}
													childdata6.append(data6)
												else:
													if levels == '6':
														childdata6= get_emp_children(subdep)
													else:
														data6={'name':subdep[se].name,'title':subdep[se].title,'id':subdep[se].id,'className': 'dep'}
														childdata6.append(data6)
												
											data5={'name':mydep[sd].name,'title':mydep[sd].title,'id':mydep[sd].id,'children':childdata6,'className': 'dep'}
											childdata5.append(data5)
										else:
											if levels == '5':
												childdata5= get_emp_children(mydep)
											
											else:
												data5={'name':mydep[sd].name,'title':mydep[sd].title,'id':mydep[sd].id,'className': 'dep'}
												childdata5.append(data5)
									
									
									data4={'name':mycircle[d].name,'title':mycircle[d].title,'id':mycircle[d].id,'children':childdata5, 'className': 'circl'}
									childdata4.append(data4)
								else:
									data4={'name':mycircle[d].name,'title':mycircle[d].title,'id':mycircle[d].id, 'className': 'circl'}
									childdata4.append(data4)
								
							
							data3={'name':mymanagement[c].name,'title':mymanagement[c].title,'id':mymanagement[c].id,'children':childdata4, 'className': 'mang'}
							childdata3.append(data3)
							
						else:
							data3={'name':mymanagement[c].name,'title':mymanagement[c].title,'id':mymanagement[c].id, 'className': 'mang'}
							childdata3.append(data3)
					

				
					data2={'name':mybranch[j].name,'title':mybranch[j].title,'id':mybranch[j].id,'children':childdata3, 'className': 'branch'}
					childdata2.append(data2)
				else:
					
					data2={'name':mybranch[j].name,'title':mybranch[j].title,'id':mybranch[j].id, 'className': 'branch'}
					childdata2.append(data2)
					
			data={'name':headquarterdata[i].name,'title':headquarterdata[i].title,'id':headquarterdata[i].id,'children':childdata2, 'className': 'head'}
			childdata.append(data)

				
		else:
			data={'name':headquarterdata[i].name,'title':headquarterdata[i].title,'id':headquarterdata[i].id, 'className': 'head'}
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
def save_tree_nodes(parent,nodeid,nodename,level,director):
	#data = ast.literal_eval(tree)
	#ids = list(find('id',data))
	#levels = list(find('level',data))
	#parent_id = frappe.get_value('Headquarter',parent,'tree_id');
	levels = frappe.db.get_single_value("Administrative Structure Categories", "levels")

	if level =='0':
		#save_node(doc,name,parent)
		doc = frappe.new_doc('Headquarter')
		doc.update({
			"headquarter":nodename,
			#"headquarter_en":nodename,
			"parent":'root',
			"is_group": '1',
			"parent_headquarter":'root',
			"director":director,
			"tree_id":nodeid
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	if level =='1':
		doc = frappe.new_doc('Branch')
		doc.update({
			"branch":nodename,
			#"branch_en":nodename,
			"parent":parent,
			"is_group": '1',
			"parent_branch":parent,
			"director":director,
			"tree_id":nodeid
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	if level =='2':
		doc = frappe.new_doc('Management')
		doc.update({
			"management":nodename,
			#"management_en":nodename,
			"parent":parent,
			"is_group": '1',
			"parent_management":parent,
			"director":director,
			"tree_id":nodeid
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	if level =='3':
		doc = frappe.new_doc('Circle')
		doc.update({
			"circle":nodename,
			#"circle_en":nodename,
			"parent":'root',
			"is_group": '1',
			"parent_circle":parent,
			"director":director,
			"tree_id":nodeid
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)

	if level =='4':
		doc = frappe.new_doc('Department')
		doc.update({
			"department_name":nodename,
			#"department_name_en":nodename,
			"parent":parent,
			"is_group": '1',
			"parent_department":parent,
			"director":director,
			"tree_id":nodeid
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)


	if level =='5' and levels == '6': #sub
		doc = frappe.new_doc('Sub Department')
		doc.update({
			"sub_department":nodename,
			#"sub_department_en":nodename,
			"parent":parent,
			"is_group": '1',
			"parent_sub_department":parent,
			"director":director,
			"tree_id":nodeid
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)


	if level =='6' and levels== '7': #sub
		doc = frappe.new_doc('Sub Association')
		doc.update({
			"sub_association":nodename,
			#"sub_association_en":nodename,
			"parent":parent,
			"is_group": '1',
			"parent_sub_association":parent,
			"director":director,
			"tree_id":nodeid
		})
		doc.flags.ignore_links = True
		doc.save(ignore_permissions=True)


	if (level =='5' and levels == '5'):
		sub_parent='Department' 
	elif (level =='6' and levels == '6'):
		sub_parent='Sub Department' 
	elif (level =='7' and levels == '7'):
		sub_parent='Sub Association' 
	

	if (level =='5' and levels == '5') or (level =='6' and levels == '6') or (level =='7' and levels == '7'):
		supervisor, supervisor_name = "",""
		if frappe.db.get_value(sub_parent, {'name':parent}, ["director","director_name"]):
			supervisor, supervisor_name = frappe.db.get_value(sub_parent, {'name':parent}, ["director","director_name"])
		if supervisor=="": frappe.throw(_("Please enter the Director of this node"))

		doc = frappe.new_doc('Employee')
		doc.update({
			"employee_name":nodename,
			"name":nodename,
			"tree_id":nodeid
		})
		doc.flags.ignore_links = True
		doc.flags.ignore_mandatory = True
		doc.save(ignore_permissions=True)

		doc_emp = frappe.new_doc('Employee Employment Detail')
		doc_emp.update({
			"employee_name":nodename,
			"name":doc.employee,
			"employee":doc.employee,
			"sub_dep":sub_parent,
			"department":parent,
			"supervisor":supervisor,
			"supervisor_name":supervisor_name
		})
		doc_emp.flags.ignore_links = True
		doc_emp.flags.ignore_mandatory = True
		doc_emp.save(ignore_permissions=True)

		if supervisor:
			supervisor_doc = frappe.get_doc('Employee Employment Detail',supervisor)
			supervisor_doc.append('responsible_of_staff',{
				'employee':doc.employee,
				'employee_name':nodename
				})
			supervisor_doc.save(ignore_permissions=True)



	return level+" done "+ levels


@frappe.whitelist(allow_guest=True)
def drag_drop_node(dragged,dropped,level):
	levels = frappe.db.get_single_value("Administrative Structure Categories", "levels")
	#if level == '6':
	sub_parent ='Department' 
	if (level =='5' and levels == '5'):
		sub_parent='Department' 
	elif (level =='6' and levels == '6'):
		sub_parent='Sub Department' 
	elif (level =='7' and levels == '7'):
		sub_parent='Sub Association' 

	supervisor, supervisor_name = "",""
	if frappe.db.get_value(sub_parent, {'name':dropped}, ["director","director_name"]):
		supervisor, supervisor_name = frappe.db.get_value(sub_parent, {'name':dropped}, ["director","director_name"])

	frappe.db.sql("""update `tabEmployee Employment Detail` set sub_dep=%s,supervisor=%s,supervisor_name=%s, department=%s where name=%s""",(supervisor,supervisor_name,sub_parent,dropped,dragged), as_dict=1)
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
	from erpnext.hr.page.hr_structure.hr_structure import get_tree_levels
	levels = get_tree_levels()
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
	if levels=='6' and level == '6':
		frappe.db.sql("""delete from `tabDepartment` where name = %s""", node)
	if levels=='7' and  level == '6':
		frappe.db.sql("""delete from `tabSub Department` where name = %s""", node)
	if levels=='7' and  level == '7':
		frappe.db.sql("""delete from `tabSub Association` where name = %s""", node)

	if levels=='5' and level == '6':
		frappe.db.sql("""update `tabEmployee Employment Detail` set status='Left' where name = %s""", node)
		frappe.db.sql("""update `tabEmployee` set status='Left' where name = %s""", node)
	if levels=='6' and level == '7':
		frappe.db.sql("""update `tabEmployee Employment Detail` set status='Left' where name = %s""", node)
		frappe.db.sql("""update `tabEmployee` set status='Left' where name = %s""", node)
	if levels=='7' and level == '8':
		frappe.db.sql("""update `tabEmployee Employment Detail` set status='Left' where name = %s""", node)
		frappe.db.sql("""update `tabEmployee` set status='Left' where name = %s""", node)
	return level



@frappe.whitelist(allow_guest=True)
def get_emp_user(emp=None):
	if emp:
		return frappe.db.get_value("Employee Personal Detail", emp, "user_id")





	

@frappe.whitelist(allow_guest=True)
def get_emp_children(empqry):
	childdata7= []
	for e in range(len(empqry)):
		emp=frappe.db.sql("""select e.employee_name as name , emp.name as title ,tree_id as id from tabEmployee as e join `tabEmployee Employment Detail` as emp on emp.name= e.name where emp.status='Active' and emp.docstatus < 2  and ifnull(emp.department,'') = %s""",(empqry[e].name), as_dict=1)
		if emp:
			data7={'name':empqry[e].name,'title':empqry[e].title,'id':empqry[e].id,'children':emp ,'className': 'emp'}
			childdata7.append(data7)
		else:
			data7={'name':empqry[e].name,'title':empqry[e].title,'id':empqry[e].id,'children':emp , 'className': 'emp'}
			childdata7.append(data7)

	return childdata7

@frappe.whitelist(allow_guest=True)
def get_tree_levels():
	levels = frappe.db.get_single_value("Administrative Structure Categories", "levels")
	return levels









