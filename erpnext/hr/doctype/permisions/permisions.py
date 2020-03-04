# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Permisions(Document):
	def validate(self):
		hr_users=[]
		hr_managers=[]
		system_man=[]
		hr_users_remove=[]
		hr_managers_remove=[]
		system_man_remove=[]
		for r in self.get('roles'):
			wf=frappe.get_list("Workflow",["name","document_type"],filters={"document_type":r.application})
			if not wf:
				self.create_wf(r.application)

			wf=frappe.get_list("Workflow",["name","document_type"],filters={"document_type":r.application})
			if wf:
				hr_users.append(r.suggestion)
				hr_managers.append(r.recommendation)
				system_man.append(r.approval)

		for m in self.get("approvls2"):
			hr_users_remove.append(m.suggestion)
			hr_managers_remove.append(m.recommendation)
			system_man_remove.append(m.approval)

		hr_managers=self.remove_dublicate(hr_managers)
		hr_managers_remove=self.remove_dublicate(hr_managers_remove)
		hr_users=self.remove_dublicate(hr_users)
		hr_users_remove=self.remove_dublicate(hr_users_remove)
		hr_managers=self.remove_dublicate(hr_managers)
		hr_managers_remove=self.remove_dublicate(hr_managers_remove)

		for rem in hr_users:
			if rem in hr_users_remove:
				hr_users_remove.remove(rem)
			else:
				ems=frappe.get_doc("Employee",rem)
				if ems:
					if ems.user_id:
						users=frappe.get_doc("User",ems.user_id)
						if users:
							users.add_roles("HR User")

					else:
						frappe.throw("There is no user for employee '{0}'".format(rem))



		for rem in hr_managers:
			if rem in hr_managers_remove:
				hr_managers_remove.remove(rem)
			else:
				ems=frappe.get_doc("Employee",rem)
				if ems:
					if ems.user_id:
						users=frappe.get_doc("User",ems.user_id)
						if users:
							users.add_roles("HR Manager")

					else:
						frappe.msgprint("There is no user for employee '{0}'".format(rem))
		for rem in system_man:
			if rem in system_man_remove:
				system_man_remove.remove(rem)
			else:
				ems=frappe.get_doc("Employee",rem)
				if ems:
					if ems.user_id:
						users=frappe.get_doc("User",ems.user_id)
						if users:
							users.add_roles("System Manager")

					else:
						frappe.msgprint("There is no user for employee '{0}'".format(rem))



		for rem in hr_users_remove:
			ems=frappe.get_doc("Employee",rem)
			if ems:
				if ems.user_id:
					users=frappe.get_doc("User",ems.user_id)
					if users:
						users.remove_roles("HR User")

				else:
					frappe.msgprint("There is no user for employee '{0}'".format(rem))
		
		for rem in hr_managers_remove:
			ems=frappe.get_doc("Employee",rem)
			if ems:
				if ems.user_id:
					users=frappe.get_doc("User",ems.user_id)
					if users:
						users.remove_roles("HR Manager")

				else:
					frappe.msgprint("There is no user for employee '{0}'".format(rem))
		
		for rem in system_man_remove:
			ems=frappe.get_doc("Employee",rem)
			if ems:
				if ems.user_id:
					users=frappe.get_doc("User",ems.user_id)
					if users:
						users.remove_roles("System Manager")

				else:
					frappe.msgprint("There is no user for employee '{0}'".format(rem))
		


		self.approvls2=self.get("roles")






	def remove_dublicate(self,lis):
		res=[]
		for item in lis:
			if item not in res:
				res.append(item)
		return res





	def create_wf(self,application):
		states=[{"state" : "Pending Request","doc_status" : 0,"allow_edit":"Employee","idx":1},
		{"state" : "Initial Approval","doc_status" : 0,"allow_edit":"HR User","idx":2},
		{"state" : "Second Approval","doc_status" : 1,"allow_edit":"HR Manager","idx":3},
		{"state" : "Final Approval","doc_status" : 1,"allow_edit":"System Manager","idx":4},
		{"state" : "Initial Rejection","doc_status" : 1,"allow_edit":"HR User","idx":5},
		{"state" : "reject","doc_status" : 1,"allow_edit":"HR Manager","idx":6},
		{"state" : "reject","doc_status" : 1,"allow_edit":"System Manager","idx":7}]

		transitions=[{"state":"Pending Request","action":"Approve","next_state":"Initial Approval","allowed":"HR User"},
		{"state":"Pending Request","action":"Reject","next_state":"Initial Rejection","allowed":"HR User"},
		{"state":"Initial Approval","action":"Approve","next_state":"Second Approval","allowed":"HR Manager"},
		{"state":"Initial Approval","action":"Reject","next_state":"reject","allowed":"HR Manager"},
		{"state":"Second Approval","action":"Approve","next_state":"Final Approval","allowed":"System Manager"},
		{"state":"Second Approval","action":"Reject","next_state":"reject","allowed":"System Manager"}]
		wf=frappe.get_doc({
			"doctype": "Workflow",
			"document_type" : application,
			"workflow_name" : application+" wf",
			"states":states,
			"transitions" : transitions,
			"is_active" : 1
			}).save(ignore_permissions=True)
		
