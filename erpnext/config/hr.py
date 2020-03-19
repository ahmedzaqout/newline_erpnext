from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Man power"),
			"items": [
				{
					"type": "doctype",
					"name": "Employee",
					"label": _("Employees Files"),
					"description": _("Employee records."),
				},
				
				{
					"type": "page",
					"name": "hr-structure",
					"label": _("Administrative Structure")
				},
				

				{
					"type": "page",
					"name": "organizational-struc",
					"label": _("Organizational Structure")
				},
				{	"type": "doctype",
					"name": "Holiday List",
					"description": _("Holiday master.")
				},
				
				
				{
					"type": "doctype",
					"name": "Work Shift",
					"description": _("Work Shift")
				},
				{
					"type": "doctype",
					"name": "Finger Print Device Control Panel",
					"label": _("Finger Print Device Control Panel"),
					"description": _("Finger Print Device Control Panel")
				},
				{
					"type": "doctype",
					"name": "Sanctions and Penalties",
					"description": _("Sanctions and Penalties")
				},
				{
					"type": "doctype",
					"name": "Manpower Planning",
					"description": _("Manpower Planning")
				},
				{
					"type": "doctype",
					"name": "Work Shifts Management",
					"description": _("Work Shifts Management")
				},
		
			]
		},
		{
			"label": _("Recruitment and selection"),
			"items": [
				{
					"type": "doctype",
					"name": "Job Description",
					"description": _("Job Description."),
				},
				{
					"type": "doctype",
					"name": "Job Opening",
					"description": _("Opening for a Job."),
				},
				{
					"type": "doctype",
					"name": "Job Applicant",
					"description": _("Applicant for a Job."),
				},

				{
					"type": "doctype",
					"name": "Interview",
					"description": _("Interview for a Job."),
				},
				{
					"type": "doctype",
					"name": "Administrative and Financial Approval",
					"description": _("Administrative and Financial Approval."),
				},
				{
					"type": "doctype",
					"name": "Offer Letter",
					"description": _("Offer candidate a Job."),
				},


			]
		},
	{
			"label": _("Salary System"),
			"items":[
				{
					"type": "page",
					"name": "payroll-report",
					"label": _("Payroll Report")
				},
				{
					"type": "doctype",
					"name": "Earnings Classification",
					"label": _("Earnings Classification"),
					"description": _("Earnings Classification")
				},
				{
					"type": "doctype",
					"name": "Salary Component",
					"label": _("Salary Components"),
					"description": _("Earnings, Deductions and other Salary components")
				},
				
				{
					"type": "doctype",
					"name": "Payroll Entry",
					"label": _("Payroll Entry"),
					"description":_("Generate Salary Slips"),
					"hide_count": True
				},
				{
					"type": "doctype",
					"name": "Salary Structure",
					"description": _("Salary template master.")
				},
				{
					"type": "doctype",
					"name": "Salary Slip",
					"description": _("Monthly salary statement."),
				},
				{
					"type": "doctype",
					"name": "Earnings Deductions Tool",
					"label": _("Earnings Deductions Tool"),
					"description": _("Earnings Deductions Tool")
				},
				

			]
		},

		

		{
			"label": _("Attendance & Leaves"),
			"items": [
				
					{
					"type": "doctype",
					"name": "Employee Attendance Tool",
					"label": _("Employee Attendance Tool"),
					"description":_("Mark Attendance for multiple employees"),
					"hide_count": True
				},
			
				{
					"type": "doctype",
					"name": "Upload Attendance",
					"description":_("Upload attendance from a .csv file"),
					"hide_count": True
				},
				
				{
					"type": "doctype",
					"name": "Leave Allocation",
					"description": _("Allocate leaves for a period.")
				},
				{
					"type": "doctype",
					"name": "Leave Control Panel",
					"label": _("Leave Allocation Tool"),
					"description":_("Allocate leaves for the year."),
					"hide_count": True
				},
				{
					"type": "doctype",
					"name": "Leave Block List",
					"description": _("Block leave applications by department.")
				},
			]
		},

{
			"label": _("Training"),
			"items": [ 
				{
					"type": "doctype",
					"name": "Training Need"
				},
				{
					"type": "doctype",
					"name": "Training Program"
				},
				{
					"type": "doctype",
					"name": "Training Event"
				},
				{
					"type": "doctype",
					"name": "Training Result"
				},
				{
					"type": "doctype",
					"name": "Training Feedback"
				},
				{
					"type": "doctype",
					"name": "Unplanning Training"
				},
			]
		},
		{
			"label": _("Evaluation"),
			"items": [ 
				{
					"type": "doctype",
					"name": "Evaluation Form"
				},
				{
					"type": "doctype",
					"name": "Employee Evaluation"
				},

				{
					"type": "doctype",
					"name": "Employee Evaluation Result"
				}
			]
		},


		{
			"label": _("The Orders"),
			"items": [
	{
					"type": "doctype",
					"name": "Attendance",
					"description": _("Attendance record."),
				},
{
					"type": "doctype",
					"name": "Departure",
					"description": _("Departure record."),
				},
				{
					"type": "doctype",
					"name": "Leave Application",
					"description": _("Applications for leave."),
				},
				{
					"type": "doctype",
					"name": "Employee Edit Time",
					"description":_("Employee Edit Time for Employee")
				},
				{
					"type": "doctype",
					"name": "Exit permission",
					"description": _("Exit permissions.")
				},
{
					"type": "doctype",
					"name": "Timesheet",
					"description": _("Timesheet for tasks."),
				},
				
{
					"type": "doctype",
					"name": "Employee Resignation",
					"description": _("Employee Resignation")
				},
{
					"type": "doctype",
					"name": "Employee designation change",
					"description": _("Employee designation change")
				},
				{
					"type": "doctype",
					"name": "Employee Loan Application",
					"description": _("Employee Loan Application")
				},
{
					"type": "doctype",
					"name": "Employee Transfer",
					"description": _("Employee Transfer")
				},

			]
		},
		{
			"label": _("Setup"),
			"icon": "fa fa-cog",
			"items": [
				{
					"type": "doctype",
					"name": "HR Settings",
					"description": _("Settings for HR Module")
				},
				{
					"type": "doctype",
					"name": "Company",
					"description": _("Company (not Customer or Supplier) master.")
				},

	
			]
		},



		{
			"label": _("Constants"),
			"icon": "fa fa-list",
			"items": [
				{
					"type": "doctype",
					"name": "Employment Type",
					"description": _("Employment Type.")
				},
				{
					"type": "doctype",
					"name": "Designation",
					"description": _("Designation.")
				},

				{
					"type": "doctype",
					"name":"Leave Type",
					"description": _("Type of leaves like casual, sick etc."),
				},
			


				{	"type": "doctype",
					"name": "Grade Category",
					"description": _("Employee Grade Category")
				},
{
					"type": "doctype",
					"name": "State Holiday",
					"description": _("State Holiday")
				},
				{
					"type": "doctype",
					"name": "Branch",
					"description": _("Organization branch master.")
				},
				{
					"type": "doctype",
					"name": "Department",
					"description": _("Organization unit (department) master.")
				},
				{
					"type": "doctype",
					"name": "Circle",
					"description": _("Organization Circle.")
				},
				{
					"type": "doctype",
					"name": "Management",
					"description": _("Organization Management master.")
				},

				
				{
					"type": "doctype",
					"name": "Violation Type",
					"description": _("Violation Type")
				},
				{
					"type": "doctype",
					"name": "Penalty",
					"description": _("Penalty")
				},
				{
					"type": "doctype",
					"name": "Letter Head",
					"description": _("Letter Head")
				},
		
				{
					"type": "doctype",
					"name": "Nationality"
				},
				{
					"type": "doctype",
					"name": "Religion"
				},
				{
					"type": "doctype",
					"name": "City"
				},
				{
					"type": "doctype",
					"name": "Country"
				},
				
				{
					"type": "doctype",
					"name": "Governorate"
				},
				{
					"type": "doctype",
					"name": "Bank"
				},{
					"type": "doctype",
					"name": "Bank Branch"
				},

{
					"type": "doctype",
					"name": "University"
				},

				{
					"type": "doctype",
					"name": "College"
				},
				{
					"type": "doctype",
					"name": "Specialization"
				},

				{
					"type": "doctype",
					"name": "Qualification"
				},

				{
					"type": "doctype",
					"name": "Gender"
				},

				{
					"type": "doctype",
					"name": "Address"
				},
				{
					"type": "doctype",
					"name": "Reward Type"
				},
				{
					"type": "doctype",
					"name": "Currency"
				},
				{
					"type": "doctype",
					"name": "Loan Type",
					"description": _("Define various loan types")
				},
				{
					"type": "doctype",
					"name": "Program Activity Details",
					"description": _("Define Employee Orientation Program Activity Details")
				},
				{
					"type": "doctype",
					"name": "Required Record",
					"description": _("Define Required Record")
				},
				{
					"type": "doctype",
					"name": "Effective Communication",
					"description": _("Define Effective Communication")
				},

				
					]
		},
		{
			"label": _("Employee Loan Management"),
			"icon": "icon-list",
			"items": [

				{
					"type": "doctype",
					"name": "Employee Loan"
				},
				{
					"type": "doctype",
					"name": "Loan Type",
					"description": _("Define various loan types")
				},
				
			]
		},


		{
			"label": _("Reports"),
			"icon": "fa fa-list",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employee Functional Report",
					"doctype": "Attendance"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employee Financial Report",
					"doctype": "Employee"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employee Monthly Attendance Sheet",
					"doctype": "Employee"
				},
				
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employees Qualifications and Experiences",
					"doctype": "Employee"
				},
				#{
				#	"type": "report",
				#	"is_query_report": True,
				#	"name": "Employee Overtime Calculation",
				#	"doctype": "Attendance"
				#},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employee Leave Balance",
					"doctype": "Leave Application"
				},
				
				{
					"type": "report",
					"is_query_report": True,
					"name": "Absent Employee Without Leaves",
					"doctype": "Attendance"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employee Birthday",
					"doctype": "Employee"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employees working on a holiday",
					"doctype": "Employee"
				},
				#{
				#	"type": "report",
				#	"name": "Employee Information",
				#	"doctype": "Employee"
				#},
				#{
				#	"type": "report",
				#	"is_query_report": True,
				#	"name": "Salary Register",
				#	"doctype": "Salary Slip"
				#},
				#{
				#	"type": "report",
				#	"is_query_report": True,
				#	"name": "Monthly Attendance Sheet",
				#	"doctype": "Attendance"
				#},
				
				{
					"type": "report",
					"is_query_report": True,
					"name": "Attendance Summary Pal",
					"doctype": "Attendance"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Exit permissions",
					"doctype": "Exit permission"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Absent Employee",
					"doctype": "Attendance"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Salary Report",
					"doctype": "salary_report"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employee Employment Contract",
					"label": _("Employee Employment Details")
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "employee_leave_balance",
					"label": _("Employee Leave Balance")
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employee Panelties",
					"doctype": "Emplyee Warning",
					"label": _("Employee Penalties")
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employee address",
					"label": _("Gender Chart")
				},
				{
					"type": "page",
					"name": "gender-chart",
					"label": _("Gender Chart")
				},

				
				{
					"type": "page",
					"name": "marital-status",
					"label": _("Marital Status Report")
				},
				{
					"type": "page",
					"name": "employee-information",
					"label": _("Employee Information")
				},
				
				{
					"type": "report",
					"is_query_report": True,
					"name": "Loan Report",
					"label": _("Loan Report")
				},
{
					"type": "report",
					"is_query_report": True,
					"name": "Job Applicant Report",
					"label": _("Job Applicant Report")
				},
{
					"type": "report",
					"is_query_report": True,
					"name": "Candidate Job Applicant",
					"label": _("Candidate Job Applicant")
				},
{
					"type": "report",
					"is_query_report": True,
					"name": "Employee Employment Contract",
					"label": _("Employee Employment Contract")
				},
{
					"type": "report",
					"is_query_report": True,
					"name": "New Employees Report",
					"label": _("New Employees Report")
				},
{
					"type": "report",
					"is_query_report": True,
					"name": "Employees that their contracts end",
					"label": _("Employees that their contracts end")
				},
{
					"type": "report",
					"is_query_report": True,
					"name": "Employee Orders Report",
					"label": _("Employee Orders Report")
				},
{
					"type": "report",
					"is_query_report": True,
					"name": "Workshift Report",
					"label": _("Workshift Report")
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employees with Consumed Leaves",
					"label": _("Employees with Consumed Leaves")
				},
{
					"type": "report",
					"is_query_report": True,
					"name": "Allowances",
					"label": _("Allowances")
				},
{
					"type": "report",
					"is_query_report": True,
					"name": "Deductions",
					"label": _("Deductions")
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employee Salary Changes",
					"label": _("Employee Salary Changes")
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Candidate Evaluation Summary",
					"label": _("Candidate Evaluation Summary")
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Leaves from Discount Attendance Hours",
					"label": _("Leaves from Discount Attendance Hours")
				},
				{
					"type": "report",
					"is_query_report": False,
					"doctype" : "Administrative and Financial Approval",
					"name": "Administrative and Financial Approval Applicant",
					"label": _("Administrative and Financial Approval Applicant")
				}




			]
		},
{
			"label": _("Permissions"),
			"icon": "fa fa-lock",
			"items": [
				{
					"type": "page",
					"name": "permission-manager",
					"label": _("Role Permissions Manager"),
					"icon": "fa fa-lock",
					"description": _("Set Permissions on Document Types and Roles")
				},
				
				{
					"type": "doctype",
					"name": "Role Permission for Page and Report",
					"description": _("Set custom roles for page and report")
				},
			{
					"type": "doctype",
					"name": "User",
					"description": _("System and Website Users")
				},
{
					"type": "doctype",
					"name": "Role",
					"description": _("User Roles")
				},

                                {
					"type": "doctype",
					"name": "Permisions",
					"description": _("Permisions")
				}
			]
		}


,
{
			"label": _("Manpower Planning"),
			"icon": "fa fa-lock",
			"items": [
				
                                {
					"type": "doctype",
					"name": "Manpower Planning",
					"description": _("Manpower Planning")
				}
			]
		}

,
{
			"label": _("Work Shifts Management"),
			"icon": "fa fa-lock",
			"items": [
				
                                {
					"type": "doctype",
					"name": "Work Shifts Management",
					"description": _("Work Shifts Management")
				}
			]
		}

,
{
			"label": _("Work Shift"),
			"icon": "fa fa-lock",
			"items": [
				
                                {
					"type": "doctype",
					"name": "Work Shift",
					"description": _("Work Shift")
				}
			]
		}

,
{
			"label": _("Company Structure"),
			"icon": "fa fa-lock",
			"items": [
				
				{
					"type": "page",
					"name": "hr-structure",
					"label": _("Administrative Structure")
				},
				

				{
					"type": "page",
					"name": "organizational-struc",
					"label": _("Organizational Structure")
				}
			]
		}
,
{
			"label": _("Control Panel"),
			"icon": "fa fa-lock",
			"items": [
				
				{
					"type": "page",
					"name": "control-panel",
					"label": _("Control Panel")
				}
			]
		}
,
		{
			"label": _("SMS"),
			"icon": "fa fa-wrench",
			"items": [
				{
					"type": "doctype",
					"name": "SMS Center",
					"description":_("Send mass SMS to your contacts"),
				},
				{
					"type": "doctype",
					"name": "SMS Log",
					"description":_("Logs for maintaining sms delivery status"),
				},
				{
					"type": "doctype",
					"name": "SMS Settings",
					"description": _("Setup SMS gateway settings")
				},
			]
		},
{
			"label": _("Finger Print Device Control Panel"),
			"icon": "fa fa-wrench",
			"items": [
				{
					"type": "doctype",
					"name": "Finger Print Device Control Panel",
					"description":_("Finger Print Device Control Panel"),
				}
			]
		}

,
{
			"label": _("Company Tree"),
			"icon": "fa fa-lock",
			"items": [
				
				{
					"type": "doctype",
					"name": "company",
					"route": "Tree/Company",
					"description": _("Company Tree"),
					"label": _("Company Tree")
				}
			]
		},
		{
			"label": _("Recruitment and selection Nawa"), 
			"items": [
				{
					"type": "doctype",
					"name": "Job Description",
					"description": _("Job Description."),
				},
				{
					"type": "doctype",
					"name": "Planned Job"
				},
				{
					"type": "doctype",
					"name": "Unplanned Job"
				},

				{
					"type": "doctype",
					"name": "Job Opening",
					"description": _("Opening for a Job."),
				},
				{
					"type": "doctype",
					"name": "Job Applicant",
					"description": _("Applicant for a Job."),
				},

				{
					"type": "doctype",
					"name": "Interview",
					"description": _("Interview for a Job."),
				},
				{
					"type": "doctype",
					"name": "Administrative and Financial Approval",
					"description": _("Administrative and Financial Approval."),
				},
				{
					"type": "doctype",
					"name": "Offer Letter",
					"description": _("Offer candidate a Job."),
				},
				{
					"type": "doctype",
					"name": "Job  Employee Audit"
				},
				{
					"type": "doctype",
					"name": "Employee Orientation Program"
				},
				{
					"type": "doctype",
					"name": "Trial Period Evaluation"
				}


			]
		}
	]
