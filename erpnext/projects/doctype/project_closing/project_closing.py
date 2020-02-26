# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
from frappe.utils import flt, cstr, cint


class ProjectClosing(Document):
		def autoname(self):
     			if not self.name:
    				self.name = "Closing-"+ self.project

@frappe.whitelist()
def get_schedule(project):
	las= frappe.db.sql("""select min(et.date) as first from `tabActivity Detail` as ad left join `tabEmployee Task` as et on ad.parent= et.name  where et.docstatus <2 and ad.project = %(project)s""" ,{"project" :project }, as_dict=1)
	lass=None
	if las:
		if las[0]['first']:
			lass=las[0]['first'].strftime("%Y-%m-%d")

	mill= frappe.db.sql("""select et.date as date ,ad.task ,et.employee , et.employee_name from `tabActivity Detail` as ad left join `tabEmployee Task` as et on ad.parent= et.name  where et.docstatus <2 and ad.project = %(project)s and ad.task like %(pattern)s order by et.date""" ,{"project" :project ,"pattern" : "%رفع نسخة للعميل%"}, as_dict=1)


	millstone=[]
	for m in mill:
		millstone.append([m['date'].strftime("%Y-%m-%d"),m['employee'],m['employee_name']])
		

	


	users=frappe.get_list("Project User",["user","employee_name", "specialization","s_time" ],filters={"parent" : project})
	data=[]
	if users:
		totreal=0
		totalexp=0
		totdiff=0
		for user in users:
			ss  = frappe.db.sql("""select ad.hours,et.employee from `tabActivity Detail` as ad left join `tabEmployee Task` as et on ad.parent= et.name  where et.docstatus <2 and ad.project = %(project)s  and et.employee=%(employee)s and ad.specialization = %(specialization)s
		order by et.employee """ ,{"project" :project ,"employee": user['user'],"specialization":user['specialization']}, as_dict=1)
			tot=0			
			for a in ss:			
				tot+= a['hours'] 
			if user['s_time']  <=0:
				exp=1
			else:
				exp= user['s_time'] 			
			dif=tot-user['s_time']
			perc=dif/exp *100
			totreal+=tot
			totalexp+=user['s_time']
							
			data.append([user['user'],user['employee_name'],user['specialization'], str(user['s_time']),str(tot),str(dif), str(flt(perc,2))])

		totdif=totreal - totalexp
		totaper=totdif/totalexp *100
		totaldata={"totalreal":totreal,
		"totalexp":str(totalexp),
		"totdiff":str(totdif),
		"totper" :str(flt(totaper,2))}
	if lass:
		return {"data":data,"totaldata":totaldata,"first":lass,"millstone":millstone}
	else:
		return {"data":data,"totaldata":totaldata,"first":"","millstone":millstone}
	
