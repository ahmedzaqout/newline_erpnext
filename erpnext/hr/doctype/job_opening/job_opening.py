# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import os,sys,uuid,multiprocessing, time, socket

from frappe.website.website_generator import WebsiteGenerator
from frappe import _
from frappe.model.naming import make_autoname

class JobOpening(WebsiteGenerator):
	website = frappe._dict(
		template = "templates/generators/job_opening.html",
		condition_field = "publish",
		page_title_field = "job_title",
	)

	def autoname(self):
		self.job_title = self.designation +"-" +self.job_number
		if self.job_title:
			self.name = self.job_title 	
	
	def validate(self):
		self.job_title = self.designation +"-" +self.job_number
		if not self.route:
			site_ip_address= 'http://5.9.141.189'
			port_number= frappe.local.conf.nginx_port
			
			
			self.route = "jobs/"+frappe.scrub(self.job_title).replace('_', '-')
			
			self.route_link = "<a href='"+self.route+"'>"+ (frappe.request.url)[:-1] +":"+ str(port_number) +"/"+ self.route+"</a>"

	def get_context(self, context):
		context.parents = [{'route': 'jobs', 'title': _('All Jobs') }]



def get_list_context(context):
	context.title = _("Jobs")
	context.row_template = "erpnext/templates/includes/jobs/jobs_row_template.html"

	context.introduction = _('Current Job Openings')
	context.get_list = get_job_openings

def get_job_openings(doctype, txt=None, filters=None, limit_start=0, limit_page_length=20, order_by=None):
	fields = ['name', 'status', 'job_title','route']

	filters = filters or {}
	filters.update({
		'status': 'Open'
	})

	if txt:
		filters.update({
			'job_title': ['like', '%{0}%'.format(txt)],
			'description': ['like', '%{0}%'.format(txt)]
		})

	return frappe.get_all(doctype,
		filters,
		fields,
		start=limit_start,
		page_length=limit_page_length,
		order_by=order_by
	)
