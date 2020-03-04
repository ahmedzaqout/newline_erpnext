# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class EmployeeEvaluation(Document):
	def validate(self):
		evalu=frappe.get_list('Employee Evaluation','name',filters={"employee":self.employee,"evaluation_form":self.evaluation_form,"docstatus":["<",2],"owner" :self.owner})
		# if evalu and len(evalu)>0 and evalu[0].name != self.name :
		# 	frappe.throw(_("You already evaluate the employee '{0}' for the evaluation form '{1}'".format(self.employee,self.evaluation_form)))


	def on_submit(self):
		evalu=frappe.get_list('Employee Evaluation Result','name',filters={"employee":self.employee,"evaluation_form":self.evaluation_form,"docstatus":["<",2]})
		eva_result = None;
		evalu_count=len(frappe.get_list('Evaluator Employee','name',filters={"parent":self.employee,"docstatus":["<",2]}))

		total=1;
		if evalu and len(evalu)>0:
			eva_result=frappe.get_doc('Employee Evaluation Result',evalu[0].name)
			total=total + (int)(eva_result.total_elevator_number) 
			if evalu_count <= total:
				eva_result.status ="Completed"
			if total > 8 :
				if total == 9:
					personal =self.get('personal')
					technical = self.get('technical')
					performance = self.get('performance')
					pp=[]
					tec = []
					perf= []
					count_q=0;
					count_re=0;
					for per in personal:
						pp.append({"evaluation_item" : per.evaluation_item ,"employee1" :per.rate})
						count_q+=1
						count_re+= int(per.rate)
					for per in technical:
						tec.append({"evaluation_item" : per.evaluation_item ,"employee1" :per.rate})
						count_q+=1
						count_re+=int(per.rate)
					for per in performance:
						perf.append({"evaluation_item" : per.evaluation_item ,"employee1" :per.rate})
						count_q+=1
						count_re+=int(per.rate)

					eva_result.set("personal2" ,pp)
					eva_result.set("performance2" ,perf)
					eva_result.set("technical2" , tec)
					total2 =0
					if count_q > 0:
						total2 = (( count_re * 20 / count_q  ) + float(eva_result.total))/2.0
					eva_result.total_elevator_number = total

					eva_result.save(ignore_permissions=True)
				else:

					t2 = total - 8
					personal =self.get('personal')
					technical = self.get('technical')
					performance = self.get('performance')
					pp=[]
					tec = []
					perf= []
					count_q=0;
					count_re=0;
					for per in personal:
						a=frappe.get_all("Evaluation Result Item" , ["name"],filters={"parent" : eva_result.name , "parenttype" : "Employee Evaluation Result" ,"evaluation_item" : per.evaluation_item ,"parentfield" : 'personal2'})
						if len(a)>0:
							item = frappe.get_doc("Evaluation Result Item" , a[0].name)
							mmm={"evaluation_item" : per.evaluation_item ,
								"employee1"  :item.employee1,
								"employee2"  :item.employee2,
								"employee3"  :item.employee3,
								"employee4"  :item.employee4,
								"employee5"  :item.employee5,
								"employee6"  :item.employee6,
								"employee7"  :item.employee7,
								"employee8"  :item.employee8,

								}
							mmm["employee"+ str(t2)]=per.rate


							pp.append(mmm)


							count_q+=1
							count_re+= int(per.rate)
					for per in technical:
						a=frappe.get_all("Evaluation Result Item" , ["name"],filters={"parent" : eva_result.name , "parenttype" : "Employee Evaluation Result" ,"evaluation_item" : per.evaluation_item ,"parentfield" : 'technical2' })
						if len(a)>0:
							item = frappe.get_doc("Evaluation Result Item" , a[0].name)
							mmm={"evaluation_item" : per.evaluation_item ,
								"employee1"  :item.employee1,
								"employee2"  :item.employee2,
								"employee3"  :item.employee3,
								"employee4"  :item.employee4,
								"employee5"  :item.employee5,
								"employee6"  :item.employee6,
								"employee7"  :item.employee7,
								"employee8"  :item.employee8,

								}
							mmm["employee"+ str(t2)]=per.rate


							tec.append(mmm)

							count_q+=1
							count_re+= int(per.rate)
					for per in performance:
						a=frappe.get_all("Evaluation Result Item" , ["name"],filters={"parent" : eva_result.name , "parenttype" : "Employee Evaluation Result" ,"evaluation_item" : per.evaluation_item ,"parentfield" : 'performance2'})
						if len(a)>0:
							item = frappe.get_doc("Evaluation Result Item" , a[0].name)
							mmm={"evaluation_item" : per.evaluation_item ,
								"employee1"  :item.employee1,
								"employee2"  :item.employee2,
								"employee3"  :item.employee3,
								"employee4"  :item.employee4,
								"employee5"  :item.employee5,
								"employee6"  :item.employee6,
								"employee7"  :item.employee7,
								"employee8"  :item.employee8,

								}
							mmm["employee"+ str(t2)]=per.rate


							perf.append(mmm)
							count_q+=1
							count_re+= int(per.rate)
					total2 =0
					if count_q > 0:
						total2 = (( count_re * 20 / count_q  ) + float(eva_result.total))/2.0
					eva_result.total = total2
					eva_result.total_elevator_number = total
					eva_result.set("personal2" ,pp)
					eva_result.set("performance2" ,perf)
					eva_result.set("technical2" , tec)
					eva_result.save(ignore_permissions=True)

			else:
				personal =self.get('personal')
				technical = self.get('technical')
				performance = self.get('performance')
				pp=[]
				tec = []
				perf= []
				count_q=0;
				count_re=0;
				for per in personal:
					a=frappe.get_all("Evaluation Result Item" , ["name"],filters={"parent" : eva_result.name , "parenttype" : "Employee Evaluation Result" ,"evaluation_item" : per.evaluation_item,"parentfield" : 'personal'  })
					if len(a)>0:
						item = frappe.get_doc("Evaluation Result Item" , a[0].name)
						mmm={"evaluation_item" : per.evaluation_item ,
							"employee1"  :item.employee1,
							"employee2"  :item.employee2,
							"employee3"  :item.employee3,
							"employee4"  :item.employee4,
							"employee5"  :item.employee5,
							"employee6"  :item.employee6,
							"employee7"  :item.employee7,
							"employee8"  :item.employee8,

							}
						mmm["employee"+ str(total)]=per.rate


						pp.append(mmm)


						count_q+=1
						if per.rate:
							count_re+= int(per.rate)
				for per in technical:
					a=frappe.get_all("Evaluation Result Item" , ["name"],filters={"parent" : eva_result.name , "parenttype" : "Employee Evaluation Result" ,"evaluation_item" : per.evaluation_item,"parentfield" : 'technical' })
					if len(a)>0:
						item = frappe.get_doc("Evaluation Result Item" , a[0].name)
						mmm={"evaluation_item" : per.evaluation_item ,
							"employee1"  :item.employee1,
							"employee2"  :item.employee2,
							"employee3"  :item.employee3,
							"employee4"  :item.employee4,
							"employee5"  :item.employee5,
							"employee6"  :item.employee6,
							"employee7"  :item.employee7,
							"employee8"  :item.employee8,

							}
						mmm["employee"+ str(total)]=per.rate


						tec.append(mmm)

						count_q+=1
						if per.rate:
							count_re+= int(per.rate)
				for per in performance:
					a=frappe.get_all("Evaluation Result Item" , ["name"],filters={"parent" : eva_result.name , "parenttype" : "Employee Evaluation Result" ,"evaluation_item" : per.evaluation_item ,"parentfield" : 'performance'})
					if len(a)>0:
						item = frappe.get_doc("Evaluation Result Item" , a[0].name)
						mmm={"evaluation_item" : per.evaluation_item ,
							"employee1"  :item.employee1,
							"employee2"  :item.employee2,
							"employee3"  :item.employee3,
							"employee4"  :item.employee4,
							"employee5"  :item.employee5,
							"employee6"  :item.employee6,
							"employee7"  :item.employee7,
							"employee8"  :item.employee8,

							}
						mmm["employee"+ str(total)]=per.rate


						perf.append(mmm)
						count_q+=1
						if per.rate:
							count_re+= int(per.rate)
				total2 =0
				if count_q > 0:
					total2 = (( count_re * 20 / count_q  ) + float(eva_result.total))/2.0
				eva_result.total = total2
				eva_result.total_elevator_number = total
				eva_result.set("personal" ,pp)
				eva_result.set("performance" ,perf)
				eva_result.set("technical" , tec)
				eva_result.save(ignore_permissions=True)

		else:
			form = frappe.get_doc('Evaluation Form',self.evaluation_form)
			per = frappe.get_all("Evaluation Section" ,["evaluation_item"],filters={'parent' : form.name ,"parentfield" : 'personal',"parenttype": "Evaluation Form"} )
			performance = frappe.get_all("Evaluation Section" ,["evaluation_item"],filters={'parent' : form.name ,"parentfield" : 'performance',"parenttype": "Evaluation Form"} )
			technical = frappe.get_all("Evaluation Section" ,["evaluation_item"],filters={'parent' : form.name ,"parentfield" : 'technical',"parenttype": "Evaluation Form"} )
			
			total = 1
			eva_result = frappe.get_doc({"doctype":"Employee Evaluation Result",
										"employee":self.employee,
										"employee_name" :self.employee_name,
										"department" :self.department,
										"designation" : self.designation,
										"direct_director" : self.direct_director,
										"work_place" : self.work_place,
										"total_elevator_number" : 1,
										"evaluation_form":self.evaluation_form,
										
										}).insert(ignore_permissions=True)
			personal =self.get('personal')
			technical = self.get('technical')
			performance = self.get('performance')
			pp=[]
			tec = []
			perf= []
			count_q=0;
			count_re=0;
			for per in personal:
				pp.append({"evaluation_item" : per.evaluation_item ,"employee"+ str(total) :per.rate})
				count_q+=1
				if per.rate:
					count_re+= int(per.rate)
			for per in technical:
				tec.append({"evaluation_item" : per.evaluation_item ,"employee"+ str(total) :per.rate})
				count_q+=1
				if per.rate:
					count_re+= int(per.rate)
			for per in performance:
				perf.append({"evaluation_item" : per.evaluation_item ,"employee"+ str(total) :per.rate})
				count_q+=1
				if per.rate:
					count_re+= int(per.rate)

			eva_result.set("personal" ,pp)
			eva_result.set("performance" ,perf)
			eva_result.set("technical" , tec)
			total = ( count_re * 20 / count_q  ) 
			eva_result.total = total
			if evalu_count <= total:
				eva_result.status ="Completed"
			eva_result.save(ignore_permissions=True)


@frappe.whitelist()
def get_form_items(source_name):
	form = frappe.get_doc('Evaluation Form',source_name)
	# per= form.get('personal');
	per = frappe.get_all("Evaluation Section" ,["evaluation_item"],filters={'parent' : form.name ,"parentfield" : 'personal',"parenttype": "Evaluation Form"} )
	performance = frappe.get_all("Evaluation Section" ,["evaluation_item"],filters={'parent' : form.name ,"parentfield" : 'performance',"parenttype": "Evaluation Form"} )
	technical = frappe.get_all("Evaluation Section" ,["evaluation_item"],filters={'parent' : form.name ,"parentfield" : 'technical',"parenttype": "Evaluation Form"} )

	return {
		"personal" : per,
		"performance" : performance,
		"technical" : technical,
	}

@frappe.whitelist()
def get_employees(doctype, txt, searchfield, start, page_len, filters):
	user=frappe.session.user
	result=[]
	if user == "Administrator":
		ll= frappe.get_list("Employee",['name'])
		for m in ll :
			result.append([m.name])
		return result
			
		
	emp=frappe.get_list("Employee" ,['name'] ,filters={"user_id" : user})
	if emp:
		emp=emp[0].name
		every=frappe.get_list("Evaluator Employee" ,['parent'] ,filters={"employee" : emp})
		for on in every:
			eva=frappe.get_doc("Evaluators",on.parent)
			result.append([eva.employee])
	return result

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user
	if user =="Administrator":
		return ""
	if "HR User" in frappe.get_roles(user) or "HR Manager" in frappe.get_roles(user) or "System Manager" in frappe.get_roles(user) or "HR System Manager" in frappe.get_roles(user):
		return ""
	return """(`tabEmployee Evaluation`.user='%(user)s' or `tabEmployee Evaluation`.owner='%(user)s')""" % {
			"user": frappe.db.escape(user)
		}


	
	

