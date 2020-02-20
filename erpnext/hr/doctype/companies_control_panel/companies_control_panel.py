# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, _dict
from frappe.model.document import Document
import os,sys,uuid,multiprocessing, time, socket

class CompaniesControlPanel(Document):
	def validate(self):
		from erpnext.hr import update_module_roles
		update_module_roles(self.projects_module)

	def _get_open_port(self):
    		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    		s.bind(("",0))
    		s.listen(1)
    		port = s.getsockname()[1]
    		s.close()
    		return port

	def _generate_random(self,length):
    		if not isinstance(length, int) or length < 8:
        		raise _("temp name_site must have positive length")
    		chars = "abcdefghigklmnopqrstuvwxyz0123456789"
    		from os import urandom
    		return "".join([chars[ord(c) % len(chars)] for c in urandom(length)])


	def create_new_site(self):
		from erpnext.hr.myapi import install_site
		#doc=install_site(self.company_domain,self.company_name,"","",self.country,self.language,"")
		from subprocess import Popen
		email='admin'+self.company_domain #'mesa_safd@hotmail.com'
        	admin_password= self._generate_random(10)
        	user_password= self._generate_random(10)
        	app1="newlinetheme2"
        	app2="bdtheme"
        	site= 'site'+self._generate_random(10)
        	port = self._get_open_port()
		
		err= os.system('../create_site.sh %s %s %s %s %s %s %s %s ' % (str(self.company_name),'erperp' , str(self.company_password) ,str(app1),str(app2),str(port),str(email),str(admin_password) ))
    		#err, out = frappe.utils.execute_in_shell('../create_site.sh %s %s %s %s %s %s %s %s   ' % (str(site),'erperp' , str(user_password) ,str(app1),str(app2),str(port),str(email),str(admin_password)) )
		#frappe.msgprint(str(err))
		self.site_ip_address= '5.9.141.189'
		self.port_number= port

		# site = frappe.new_doc('Site Settings')
		# site.update({
		# 	'company_name':self.company_name,
		# 	'language' :self.language,
		# 	'logo' :self.logo,
		# 	'site_user' : self.create_user(self.company_domain),
		# 	'branches_number' : self.branches_number,
		# 	'main' : 1,
		# 	'main_site':""
		# })
		# #site.flags.ignore_validate = True
		# #site.flags.ignore_links = True
		# site.insert(ignore_permissions=True)
		# parent = site.name
		

		# #company_branch
		# for branch in self.company_branch:
		# 	site = frappe.new_doc('Site')
		# 	site.update({
		# 		'company_name':branch.branch_name,
		# 		'site_user' : self.create_user(branch.branch_domain,branch.branch_name),
		# 		'logo' : branch.logo,
		# 		'main' : 0,
		# 		'main_site':parent
		# 	})
		# 	#site.flags.ignore_validate = True
		# 	#site.flags.ignore_links = True
		# 	site.insert(ignore_permissions=True)


	def create_user(self,domain,name = None):
		domain_str = ""
		if not domain:
			domain_str = "admin@" + name.lower()
		else:
			domain_str = "admin@" + domain.lower()
		
		return domain_str
	
	

