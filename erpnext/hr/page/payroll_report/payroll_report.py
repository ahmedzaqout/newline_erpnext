# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, json, ast
import frappe.defaults
from frappe.utils import flt

@frappe.whitelist(allow_guest=True)
def save_payroll(grade,salary,category):
	salary = json.loads(salary)

	if frappe.get_value('Grade Category',grade,"name"):
		update_payroll(grade,salary)
	else:
		doc = frappe.new_doc('Grade Category')
		doc.update({
			'grade_category':grade,
			'grade_category_en':grade,
			'category':category
			})
		doc.insert(ignore_permissions=True)
		i=1
		g_doc = frappe.get_doc('Grade Category',grade)
		for sal in salary:
			g_doc.append('grade_category_detail', {
				'experience_year':str(i),
				'basic_salary':sal })
			g_doc.save(ignore_permissions=True)
			i=i+1
	
	return "Saved"




@frappe.whitelist(allow_guest=True)
def update_payroll(grade,salary):
	i=1
	g_doc = frappe.get_doc('Grade Category',grade)
	for sal in salary:
		frappe.db.sql("""update `tabGrade Category Detail` set basic_salary=%s where parent=%s and experience_year=%s""",(sal,grade,str(i)))
		#g_doc.update('grade_category_detail',{
		#	'experience_year':str(i),
		#	'basic_salary':sal
		#	 })
		#g_doc.save(ignore_permissions=True)
		i=i+1
	return "updated"


@frappe.whitelist(allow_guest=True)
def payroll_increase_ratio():
	return frappe.db.get_value("HR Settings", None, ["payroll_increase_ratio","payroll_increase_ratio1","payroll_discount_ratio"])



@frappe.whitelist(allow_guest=True)
def get_grades(grade):
	return frappe.get_all("Grade Category Detail", fields=["basic_salary","experience_year","parent"],filters={'parent':grade},order_by='experience_year')


@frappe.whitelist(allow_guest=True)
def ann_inc_experience_years():
	employees = frappe.get_all("Employee", fields=["name","employee_name"],filters={'status':'Active'})
	for emp in employees:
		experience_years = frappe.db.get_value("Employee Salary Detail", emp.name, "experience_years")
		if experience_years:
			exp_years = int(experience_years) + 1
			print str(exp_years)
			frappe.db.sql("""update `tabEmployee Salary Detail` set experience_years = %s where employee=%s""", (exp_years,emp) )
		


@frappe.whitelist(allow_guest=True)
def annually_increase_payroll():
	from datetime import datetime
	from dateutil import relativedelta
	from frappe.utils import now_datetime, getdate
	today = datetime.today()
	now = getdate(now_datetime())
	employees = frappe.get_all("Employee", fields=["name","employee_name"],filters={'status':'Active'})
	for emp in employees:
		date_of_joining = frappe.db.get_value("Employee Employment Detail", emp.name, "date_of_joining")
		if date_of_joining:
			date1 = datetime.strptime(str(now), '%Y-%m-%d')
			date2 = datetime.strptime(str(getdate(date_of_joining)), '%Y-%m-%d')
			r = relativedelta.relativedelta(date2, date1)	
			years= r.years
			if years >= 5:
				frappe.db.sql("""update `tabEmployee Employment Detail` set grade = %s where employee=%s""", (grade,emp) )
		
		


@frappe.whitelist(allow_guest=True)
def test(salary):
	grad_arr = ['A1','A2','A3','A4','A','B','C','1','2','3','4','5','6','7','8','9','10']
	#for i in range(30):
	#	exp_num.append(i)

	for grad in grad_arr:
		if frappe.get_value('Grade Category',grad,"name"):
			update_payroll(salary)
		else:
			doc = frappe.new_doc('Grade Category')
			doc.update({
				'grade_category':grad,
				'grade_category_en':grad
				})
			doc.insert(ignore_permissions=True)

			g_doc = frappe.get_doc('Grade Category',grad)
			for sal in range(len(salary)):
				i=1
				g_doc.append('grade_category_detail', {
						'experience_year':i,
						'basic_salary':sal })
				g_doc.save(ignore_permissions=True)
				i=i+1
	return "test"

