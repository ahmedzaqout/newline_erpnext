# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, re
import frappe.permissions
from frappe import throw, _, scrub
from frappe.model.document import Document
from frappe.utils import getdate, validate_email_add, today, add_years,nowdate
from frappe.model.naming import make_autoname
from erpnext.hr.utils import validate_only_arabic, validate_only_english

class EmployeeUserDisabledError(frappe.ValidationError):
	pass


class EmployeePersonalDetail(Document):

	def validate(self):
		if self.employee_name:
			frappe.set_value("Employee",self.employee,"employee_name", self.employee_name)
		#self.employee = self.name
		if self.user_id:
			#self.validate_for_enabled_user_id()
			self.validate_duplicate_user_id()
		else:
			existing_user_id = frappe.db.get_value("Employee Personal Detail", self.name, "user_id")
			if existing_user_id:
				frappe.permissions.remove_user_permission(
					"Employee Personal Detail", self.name, existing_user_id)

		for i in [self.ar_fname,self.ar_sname,self.ar_tname,self.ar_family_name]:
			validate_only_arabic(i)

		for j in [self.en_fname,self.en_sname,self.en_tname,self.en_family_name]:
			validate_only_english(j)     

		if self.identity_no and not self.identity_no.isdigit():
			throw(_("{0} Bad entry in identity no"),self.identity_no) 

	def validate_duplicate_user_id(self):
		employee = frappe.db.sql_list("""select name from `tabEmployee Personal Detail` where
			user_id=%s and name!=%s""", (self.user_id, self.name))
		if employee:
			throw(_("User {0} is already assigned to Employee {1}").format(
				self.user_id, employee[0]), frappe.DuplicateEntryError)

	def on_update(self):
		if self.employee_name:
			frappe.set_value("Employee",self.employee,"employee_name", self.employee_name)
		if self.user_id:
			frappe.set_value("Employee",self.employee,"user_id", self.user_id)
			#self.update_user()
			#self.update_user_permissions()

	def update_user_permissions(self):
		if frappe.db.get_value("User", self.user_id):
			frappe.permissions.add_user_permission("Employee", self.name, self.user_id)
			frappe.permissions.add_user_permission("Employee Personal Detail", self.name, self.user_id)
			frappe.permissions.set_user_permission_if_allowed("Company", self.company, self.user_id)


	def update_user(self):
		# add employee role if missing
		user = frappe.get_doc("User", self.user_id)
		user.flags.ignore_permissions = True

		if "Employee" not in user.get("roles"):
			user.add_roles("Employee")

		# copy details like Fullname, DOB and Image to User
		if self.employee_name and not (user.first_name and user.last_name):
			employee_name = self.employee_name.split(" ")
			if len(employee_name) >= 3:
				user.last_name = " ".join(employee_name[2:])
				user.middle_name = employee_name[1]
			elif len(employee_name) == 2:
				user.last_name = employee_name[1]

			user.first_name = employee_name[0]

		if self.date_of_birth:
			user.birth_date = self.date_of_birth

		if self.gender:
			user.gender = self.gender

		if self.image:
			if not user.user_image:
				user.user_image = self.image
				try:
					frappe.get_doc({
						"doctype": "File",
						"file_name": self.image,
						"attached_to_doctype": "User",
						"attached_to_name": self.user_id
					}).insert()
				except frappe.DuplicateEntryError:
					# already exists
					pass

	def next(self):
		frappe.msgprint("dd")
		self.validate()

# add_depenents_bonus to employee salary details and *update employee strucre
@frappe.whitelist()
def add_depenents_bonus(employee, sal_comp, child_num=0):
	if sal_comp== 'Bonus Wife': amount = frappe.db.get_value("HR Settings", None, "bonus_wife_ratio") 
	elif sal_comp== 'Bonus Children':
		#child_num= 0.0
		#from erpnext.hr.doctype.employee_salary_detail.employee_salary_detail import employee_child
		#if employee_child(employee): child_num = employee_child(employee).count
		bonus_children_ratio = frappe.db.get_value("HR Settings", None, "bonus_children_ratio")
		amount = bonus_children_ratio * child_num

	if frappe.db.get_value('Salary Component',sal_comp) and frappe.db.get_value('Employee Salary Detail',employee):
		emp_sal = frappe.get_doc('Employee Salary Detail',{'employee': employee})
		if frappe.get_value('Salary Detail',{'salary_component':sal_comp,'parent':emp_sal.name,'parenttype':'Employee Salary Detail','type':'Earning'}):
			sal_det = frappe.get_doc('Salary Detail',{'parent':emp_sal.name,'parenttype':'Employee Salary Detail','type':'Earning'})
			sal_det.update({'salary_component':sal_comp,'amount':amount, 'type': _('Earning')})
			sal_det.save(ignore_permissions=True)
		else:
			emp_sal.append('earnings',{'salary_component':sal_comp,'amount':amount, 'type': _('Earning')})
			emp_sal.save(ignore_permissions=True)
		


@frappe.whitelist()
def get_retirement_date(date_of_birth=None):
	ret = {}
	if date_of_birth:
		try:
			retirement_age = int(frappe.db.get_single_value("HR Settings", "retirement_age") or 60)
			dt = add_years(getdate(date_of_birth),retirement_age)
			ret = {'date_of_retirement': dt.strftime('%Y-%m-%d')}
		except ValueError:
			# invalid date
			ret = {}
	return ret

