from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Projects"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": "Project",
					"description": _("Project master."),
				},
				{
					"type": "doctype",
					"name": "Task",
					"route": "List/Task",
					"description": _("Project activity / task."),
				},
				{
					"type": "doctype",
					"name": "Project Type",
					"description": _("Define Project type."),
				},
				{
					"type": "report",
					"route": "List/Task/Gantt",
					"doctype": "Task",
					"name": "Gantt Chart",
					"description": _("Gantt chart of all tasks.")
				},
			]
		},
		{
			"label": _("Time Tracking"),
			"items": [
				{
					"type": "doctype",
					"name": "Project Closing",
				},
				{
					"type": "doctype",
					"name": "Employee Task",
					"description": _("Timesheet for tasks."),
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
					"name": "Employee Tasks Report",
					"doctype": "Employee Task"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Employee Tasks Hours",
					"doctype": "Employee Task"
				},
			]
		},
		#{
		#	"label": _("Help"),
		#	"icon": "fa fa-facetime-video",
		#	"items": [
		#		{
		#			"type": "help",
		#			"label": _("Managing Projects"),
		#			"youtube_id": "egxIGwtoKI4"
		#		},
		#	]
		#},
	]
