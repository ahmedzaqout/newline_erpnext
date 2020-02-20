# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
def get_notification_config_hr():
	notifications =  { "for_doctype":{}}
	for doc in frappe.get_all('DocType',
		fields= ["name"], filters = { "name": ("not in", ('Attendance','Departure','Data Import','Salary Slip')), 'is_submittable': 1,"module":'HR'}):
		notifications["for_doctype"][doc.name] = {"docstatus": 0}
	return notifications
	

def get_notification_config():
	notifications =  { "for_doctype":
		{
			"Issue": {"status": "Open"},
			"Warranty Claim": {"status": "Open"},
			#"Task": {"status": ("in", ("Open", "Overdue"))},
			#"Project": {"status": "Open"},
			"Item": {"total_projected_qty": ("<", 0)},
			"Lead": {"status": "Open"},
			"Contact": {"status": "Open"},
			"Opportunity": {"status": "Open"},
			"Quotation": {"docstatus": 0},
			"Sales Order": {
				"status": ("not in", ("Completed", "Closed")),
				"docstatus": ("<", 2)
			},
			"Journal Entry": {"docstatus": 0},
			"Sales Invoice": {
				"outstanding_amount": (">", 0),
				"docstatus": ("<", 2)
			},
			"Purchase Invoice": {
				"outstanding_amount": (">", 0),
				"docstatus": ("<", 2)
			},
			"Payment Entry": {"docstatus": 0},
			"Leave Application": {"status": "Open"},
			#"Expense Claim": {"approval_status": "Draft"},
			"Job Applicant": {"status": "Open"},
			"Offer Letter": {
				"status": "Accepted",
				"docstatus": ("<", 2)
			},
			"Delivery Note": {
				"status": ("not in", ("Completed", "Closed")),
				"docstatus": ("<", 2)
			},
			"Stock Entry": {"docstatus": 0},
			"Material Request": {
				"docstatus": ("<", 2),
				"status": ("not in", ("Stopped",)),
				"per_ordered": ("<", 100)
			},
			"Request for Quotation": { "docstatus": 0 },
			"Supplier Quotation": {"docstatus": 0},
			"Purchase Order": {
				"status": ("not in", ("Completed", "Closed")),
				"docstatus": ("<", 2)
			},
			"Purchase Receipt": {
				"status": ("not in", ("Completed", "Closed")),
				"docstatus": ("<", 2)
			},
			"Production Order": { "status": ("in", ("Draft", "Not Started", "In Process")) },
			"BOM": {"docstatus": 0},

			"Timesheet": {"status": "Draft"},

			"Lab Test": {"docstatus": 0},
			"Sample Collection": {"docstatus": 0},
			"Patient Appointment": {"status": "Open"},
			"Consultation": {"docstatus": 0},
			"Employee": "erpnext.startup.notifications.notify_new_employee"
		},

		"targets": {
			"Company": {
				"filters" : { "monthly_sales_target": ( ">", 0 ) },
				"target_field" : "monthly_sales_target",
				"value_field" : "total_monthly_sales"
			}
		}
	}

	doctype = [d for d in notifications.get('for_doctype')]
	for doc in frappe.get_all('DocType',
		fields= ["name"], filters = {"name": ("not in", doctype),"name": ("not in", ('Attendance','Departure','Data Import','Salary Slip')), 'is_submittable': 1,"module":'HR'}):
		notifications["for_doctype"][doc.name] = {"docstatus": 0}

	return notifications


#### NAWA ####
def notify_new_employee(as_list=False):
	return frappe.db.sql("""\
		SELECT count(*)
		FROM `tabEmployee`
		WHERE month(creation) = month(CURDATE())
		and year(creation) = year(CURDATE())
		and company='Nawa'
		""")[0][0]




