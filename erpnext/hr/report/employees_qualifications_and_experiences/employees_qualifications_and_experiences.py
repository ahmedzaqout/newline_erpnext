# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _

def execute(filters=None):

	conditions, filters = get_conditions(filters)
	columns = get_columns(filters)
	data = salaries(conditions, filters)
	return columns, data


def get_columns(filters):
	columns = [
		 {"label":_("Employee") ,"width":100,"fieldtype": "link","options":"Employee"},
		 {"label":_("Employee Name") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Designation") ,"width":100,"fieldtype": "Data"},
		 {"label":_("Departement") ,"width":100,"fieldtype": "Data"},
		 {"label":_("School/University") ,"width":130,"fieldtype": "Data"},
		 {"label":_("College") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Specialization") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Qualification") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Level") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Year of Passing") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Graduation From") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Class / Percentage") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Is Main") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Major/Optional Subjects") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Ex w H Designation") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Ex w H Salary") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Ex w H Start Date") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Ex w H End Date") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Ex w H Notes") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Ex w H Company") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Ex w H Company Address") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Ex w H Contact Number") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Ex w H Total Experience") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Ex w H Branch") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Int w H Designation") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Int w H Department") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Int w H From Date") ,"width":130,"fieldtype": "Data"},
		 {"label":_("Int w H To Date") ,"width":130,"fieldtype": "Data"},
		 



		 
		 ]
		

	
	
	return columns

def salaries(conditions, filters):
	data=[]
	hours={}
	ss  = frappe.db.sql("""select emp.name as eeemployee ,emp.employee_name ,iwh.employee as iwhemployee,ewh.employee as employee ,emp.designation as des ,emp.management as manag ,ee.*, ewh.* ,iwh.branch ,iwh.from_date as ifrom_date,iwh.to_date as ito_date,iwh.designation as idesignation ,iwh.department as idepartment from `tabEmployee` as emp left Join `tabEmployee Education` as ee on emp.name=ee.parent  left join `tabEmployee External Work History` as ewh on emp.name=ewh.parent left join `tabEmployee Internal Work History` as iwh on emp.name=iwh.parent where emp.docstatus <2 %s 
						order by eeemployee """ %
		conditions, filters, as_dict=1)


	for add in ss:
		data.append([add.eeemployee,add.employee_name,add.des,add.manag,add.school_univ,add.college,add.specialization,add.qualification,add.level,add.year_of_passing,add.graduation_from,add.class_per,add.is_main,add.maj_opt_subj,add.designation,add.salary,add.start_date,add.end_date,add.notes,add.company_name,add.address,add.contact,add.total_experience,add.branch,add.idesignation,add.idepartment,add.ifrom_date,add.ito_date])
	
	return data


def get_conditions(filters):
	conditions = ""

	if filters.get("employee"): conditions += " and emp.name = %(employee)s"
	if filters.get("department"): conditions += " and emp.management = %(department)s"
	if filters.get("designation"): conditions += " and emp.designation = %(designation)s"

	return conditions, filters
