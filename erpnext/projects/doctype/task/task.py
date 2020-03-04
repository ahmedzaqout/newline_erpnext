#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, json

from frappe.utils import getdate, date_diff, add_days, cstr
from frappe import _, throw
from frappe.utils.nestedset import NestedSet

class CircularReferenceError(frappe.ValidationError): pass

class Task(NestedSet):

	def get_feed(self):
		return '{0}'.format(_(self.status))

	def get_project_details(self):
		return {
			"project": self.project
		}

	def get_customer_details(self):
		cust = frappe.db.sql("select customer_name from `tabCustomer` where name=%s", self.customer)
		if cust:
			ret = {'customer_name': cust and cust[0][0] or ''}
			return ret
	def autoname(self):
		self.name = self.subject +"-"+self.project

	def validate(self):	
		self.validate_dates()		
		if len(self.subject) < 15 :
			frappe.throw(_("The task must be at least 15 characters.")) 
		#frappe.msgprint("ss")
		#if self.subject and self.project:
		#	self.name = self.subject +"-"+self.project


	def validate_dates(self):
		if self.act_start_date and self.act_end_date and getdate(self.act_start_date) > getdate(self.act_end_date):
			frappe.throw(_("'Actual Start Date' can not be greater than 'Actual End Date'"))

	def validate_status(self):
		if self.status!=self.get_db_value("status") and self.status == "Closed":
			for d in self.depends_on:
				if frappe.db.get_value("Task", d.task, "status") != "Closed":
					frappe.throw(_("Cannot close task as its dependant task {0} is not closed.").format(d.task))

			from frappe.desk.form.assign_to import clear
			clear(self.doctype, self.name)
		self.update_m()		


	def update_depends_on(self):
		depends_on_tasks = self.depends_on_tasks or ""
		for d in self.depends_on:
			if d.task and not d.task in depends_on_tasks:
				depends_on_tasks += d.task + ","
		self.depends_on_tasks = depends_on_tasks
	def after_rename(self, old, new, merge=False):
		if not merge:
			task_new = frappe.db.get_value("Task", new, ["subject","project"], as_dict=1)

			# exclude project abbr
			new_parts = new.split("-")
			if task_new.project != new_parts[1]:
				ppro=frappe.get_doc("Project",new_parts[1])
				if ppro:
					self.project = new_parts[1]
					self.db_set("project", new_parts[1])
				else:
					frappe.msgprint("'{0}' is not valid project name".format(new_parts[1]))


			# update account number and remove from parts
			if task_new.subject != new_parts[0]:
				self.subject = new_parts[0]
				self.db_set("subject", new_parts[0])
			new_parts = new_parts[1:]

			# update account name
			#name = " - ".join(new_parts)
			#if new_acc.name != name:
			#	self.account_name = account_name
			#	self.db_set("account_name", account_name)


	def update_m(self):
		if self.s_name != self.subject +"-"+self.project:
			self.flags.ignore_links=True
			self.flags.ignore_permissions = True
			self.s_name=self.subject +"-"+self.project



	def on_update(self):
		self.update_m()
		self.update_project()
		self.unassign_todo()


	def unassign_todo(self):
		if self.status == "Closed" or self.status == "Cancelled":
			from frappe.desk.form.assign_to import clear
			clear(self.doctype, self.name)

	def update_total_expense_claim(self):
		self.total_expense_claim = frappe.db.sql("""select sum(total_sanctioned_amount) from `tabExpense Claim`
			where project = %s and task = %s and docstatus=1""",(self.project, self.name))[0][0]

	def update_time_and_costing(self):
		tl = frappe.db.sql("""select min(from_time) as start_date, max(to_time) as end_date,
			sum(billing_amount) as total_billing_amount, sum(costing_amount) as total_costing_amount,
			sum(hours) as time from `tabTimesheet Detail` where task = %s and docstatus=1"""
			,self.name, as_dict=1)[0]
		if self.status == "Open":
			self.status = "Working"
		self.total_costing_amount= tl.total_costing_amount
		self.total_billing_amount= tl.total_billing_amount
		self.actual_time= tl.time
		self.act_start_date= tl.start_date
		self.act_end_date= tl.end_date

	def update_project(self):
		if self.project and not self.flags.from_project:
			frappe.get_doc("Project", self.project).update_project()

	

	def on_trash(self):
		if check_if_child_exists(self.name):
			throw(_("Child Task exists for this Task. You can not delete this Task."))



@frappe.whitelist()
def check_if_child_exists(name):
	return frappe.db.sql("""select name from `tabTask`
		where parent_task = %s""", name)

def get_project(doctype, txt, searchfield, start, page_len, filters):
	from erpnext.controllers.queries import get_match_cond
	return frappe.db.sql(""" select name from `tabProject`
			where %(key)s like "%(txt)s"
				%(mcond)s
			order by name
			limit %(start)s, %(page_len)s """ % {'key': searchfield,
			'txt': "%%%s%%" % frappe.db.escape(txt), 'mcond':get_match_cond(doctype),
			'start': start, 'page_len': page_len})

def get_project(doctype, txt, searchfield, start, page_len, filters):
	from erpnext.controllers.queries import get_match_cond
	return frappe.db.sql(""" select parent from `tabProject User`
			where %(key)s like "%(txt)s"
				%(mcond)s
			order by name
			limit %(start)s, %(page_len)s """ % {'key': searchfield,
			'txt': "%%%s%%" % frappe.db.escape(txt), 'mcond':get_match_cond(doctype),
			'start': start, 'page_len': page_len})



@frappe.whitelist()
def set_multiple_status(names, status):
	names = json.loads(names)
	for name in names:
		task = frappe.get_doc("Task", name)
		task.status = status
		task.save()

def set_tasks_as_overdue():
	frappe.db.sql("""update tabTask set `status`='Overdue'
		where exp_end_date is not null
		and exp_end_date < CURDATE()
		and `status` not in ('Closed', 'Cancelled')""")

@frappe.whitelist()
def get_children(doctype, parent, task=None, project=None, is_root=False):

	filters = [['docstatus', '<', '2']]

	if task:
		filters.append(['parent_task', '=', task])
	elif parent and not is_root:
		# via expand child
		filters.append(['parent_task', '=', parent])
	else:
		filters.append(['ifnull(`parent_task`, "")', '=', ''])

	if project:
		filters.append(['project', '=', project])

	tasks = frappe.get_list(doctype, fields=[
		'name as value',
		'subject as title',
		'is_group as expandable'
	], filters=filters, order_by='name')

	# return tasks
	return tasks

@frappe.whitelist()
def add_node():
	from frappe.desk.treeview import make_tree_args
	args = frappe.form_dict
	args.update({
		"name_field": "subject"
	})
	args = make_tree_args(**args)

	if args.parent_task == 'All Tasks' or args.parent_task == args.project:
		args.parent_task = None

	frappe.get_doc(args).insert()

@frappe.whitelist()
def add_multiple_tasks(data, parent):
	data = json.loads(data)
	new_doc = {'doctype': 'Task', 'parent_task': parent if parent!="All Tasks" else ""}
	new_doc['project'] = frappe.db.get_value('Task', {"name": parent}, 'project') or ""

	for d in data:
		if not d.get("subject"): continue
		new_doc['subject'] = d.get("subject")
		new_task = frappe.get_doc(new_doc)
		new_task.insert()

def on_doctype_update():
	frappe.db.add_index("Task", ["lft", "rgt"])


def get_projects(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select p.name from `tabProject` as p where p.docstatus < 2""")


#doctype, txt, searchfield, start, page_len, filters
def get_merge_task(doctype,txt, searchfield, start, page_len, filters):
	users=frappe.get_list("User",['name'])
	userm=[]
	result=""
	for user in users:
		roles=frappe.get_roles(user.name) 
		if "Projects Manager" in roles:
			userm.append(user.name)
	flag=False
	for use in userm:
		user=frappe.get_doc("User",use)
		if user.employee:
			if not flag:
				result +="( "
				flag=True
			else:
				result +=" , "

			result += "'"+user.employee+ "'"
			tas= frappe.get_list("Task","name",filters={"user":user.employee})
			
	if result != "":
		result +=") "
		stat="p.user in {0} and".format(result)
	else:
		stat="1=2 and "
		
	

	
	return frappe.db.sql("""select p.name from `tabTask` as p  where {0} p.project = '{1}' and p.docstatus < 2""".format(stat,filters.get("project")))


def get_employee(doctype,txt, searchfield, start, page_len, filters):
	conditions = []
	return frappe.db.sql("""select  tabEmployee.name from tabEmployee  join  `tabProject User` as pu on tabEmployee.name = pu.user join `tabProject` as p on p.name=pu.parent where p.name =%s""",filters.get("project"))

@frappe.whitelist()
def merge(task,merge_with):
	task_doc=frappe.get_doc("Task",task)
	
	user=frappe.get_list("User",['name'],filters={'employee':task_doc.user})
	if len(user)>0:
		roles=frappe.get_roles(user[0].name) 
		if "Projects Manager" in roles:
			frappe.throw("You cant merge this task , It's created by Project Manger.")

	frappe.db.sql("""update `tabActivity Detail` as ad set ad.task ='{0}' where ad.task='{1}' """.format(merge_with,task))
	frappe.db.sql("""update `tabTask` as t set t.docstatus =2 ,t.status="Cancelled" where t.name='{0}' """.format(task))
	
	frappe.db.commit() 
	return True
		
		
	
	

