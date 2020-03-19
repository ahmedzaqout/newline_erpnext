# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.hr.doctype.job_description.job_description import month_days
from frappe.model.document import Document

class EmployeeEvaluationResult(Document):
	def on_submit(self):
		if self.employee:
			s_d =frappe.get_doc("Employee",self.employee)
		if s_d:
			if float(self.total) >= 95: 
				s_d.basic_salary = s_d.basic_salary + (s_d.basic_salary * 0.03)
			if float(self.total) >= 86 and float(self.total) < 95 : 
				s_d.basic_salary = s_d.basic_salary + (s_d.basic_salary * 0.03 * 0.9 )
			if float(self.total) >= 76 and float(self.total) < 86 : 
				s_d.basic_salary = s_d.basic_salary + (s_d.basic_salary * 0.03 * 0.8 )
			if float(self.total) > 60 and float(self.total) < 76 : 
				s_d.basic_salary = s_d.basic_salary + (s_d.basic_salary * 0.03 * 0.7)

			res = month_days(self.employee)
			total_days_in_month = res[0];
			number_of_days = res[1];

			day_sal = float(s_d.basic_salary) / float(total_days_in_month);
			hour_cost = day_sal /  float(res[2])
			s_d.hour_cost = hour_cost 				
			s_d.day_salary = day_sal; 
			s_d.flags.ignore_permissions=True
			s_d.save()

