// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.views.calendar["Work Shifts Management"] = {
	field_map: {
		"start": "start_hour",
		"end": "end_hour",
		"id": "name",
		"title": "employee",
		"name":"employee_name",
		"allDay": "allDay",
		"progress": "progress"
	},

	gantt: true,
	gantt_view_mode: 'Quarter Day',
	//scale: "hours",
	//gantt_scale: "hours",
	//order_by: "start_hour",
	//gantt_view_mode: 'Quarter Day',
	//view_mode: 'Quarter Day',

	filters: [
		{
			"fieldtype": "Link",
			"fieldname": "department",
			"options": "Department",
			"label": __("Department"),
			 on_change: function() {
				console.log("test");

			}
		},
		{
			"fieldtype": "Link",
			"fieldname": "absent_employee",
			"options": "Employee",
			"label": __("Absent Employee"),
			"get_query": function() {
				return {
					query: "erpnext.hr.doctype.work_shifts_management.work_shifts_management.get_absent_employee"
				}
			}
		},
		{
			"fieldname":"day",
			"label": __("Day"),
			"fieldtype": "Select",
			"options": "Sunday\nMonday\nTuesday\nWednesday\nThursday\nFriday\nSaturday",
			"default":  ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Saturday"][new Date().getDay()],
		},
	],
	get_events_method: "frappe.desk.calendar.get_events"
}
