# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.utils import cint, getdate, formatdate
from frappe import throw, _
from frappe.model.document import Document
from erpnext.hr.doctype.attendance.attendance import update_att_holiday
import datetime, calendar, time
from calendar import monthrange

class OverlapError(frappe.ValidationError): pass

class HolidayList(Document):
	def validate(self):
		self.validate_days()
		#onholiday() 

	def on_update(self):
		self.count_table()
		#self.update_att() 

	def get_weekly_off_dates(self):
		self.validate_values()
		date_list = self.get_weekly_off_date_list(self.from_date, self.to_date)
		last_idx = max([cint(d.idx) for d in self.get("holidays")] or [0,])
		for i, d in enumerate(date_list):
			ch = self.append('holidays', {})
			ch.description = self.weekly_off
			ch.holiday_date = d
			ch.idx = last_idx + i + 1

###############################
	def get_state_holiday_dates(self):
		if not self.state_holiday:
			throw(_("Please select State Holiday"))
		date_list = self.get_state_holiday_date_list(self.state_holiday)
		last_idx = max([cint(d.idx) for d in self.get("holidays")] or [0,])
		for i, d in enumerate(date_list):
			ch = self.append('holidays', {})
			ch.description = self.state_holiday
			ch.holiday_date = d
			ch.idx = last_idx + i + 1
			self.update_att(d)	
		self.count_table()
			

	def update_att(self,day):
		employees = frappe.get_all("Employee", fields=["name","employee_name"],filters={'status':'Active'})
		for emp in employees:
			d = calendar.day_name[getdate(day).weekday()];
			update_att_holiday(emp.name,emp.employee_name,d,day)
		self.save()
#############################

	def validate_values(self):
		if not self.weekly_off:
			throw(_("Please select weekly off day"))


	def validate_days(self):
		if self.from_date > self.to_date:
			throw(_("To Date cannot be before From Date"))

		for day in self.get("holidays"):
			if not (getdate(self.from_date) <= getdate(day.holiday_date) <= getdate(self.to_date)):
				frappe.throw(_("The holiday on {0} is not between From Date and To Date").format(formatdate(day.holiday_date)))


	def get_weekly_off_date_list(self, start_date, end_date):
		start_date, end_date = getdate(start_date), getdate(end_date)

		from dateutil import relativedelta
		from datetime import timedelta
		import calendar

		date_list = []
		existing_date_list = []
		weekday = getattr(calendar, (self.weekly_off).upper())
		reference_date = start_date + relativedelta.relativedelta(weekday=weekday)

		existing_date_list = [getdate(holiday.holiday_date) for holiday in self.get("holidays")]

		while reference_date <= end_date:
			if reference_date not in existing_date_list:
				date_list.append(reference_date)
			reference_date += timedelta(days=7)
		return date_list
#################################
	def get_state_holiday_date_list(self, state_holiday):
		start_date, end_date = frappe.db.get_value("State Holiday", state_holiday, ["from_date", "to_date"])
		start_date, end_date = getdate(start_date), getdate(end_date)
		if not end_date:
			end_date = getdate(start_date)

		from dateutil import relativedelta
		from datetime import timedelta
		import calendar

		date_list = []
		existing_date_list = []
		#weekday = getattr(calendar, (self.state_holiday).upper())
		reference_date = start_date #+ relativedelta.relativedelta(weekday=weekday)

		existing_date_list = [getdate(holiday.holiday_date) for holiday in self.get("holidays")]

		while reference_date <= end_date:
			if reference_date not in existing_date_list:
				date_list.append(reference_date)
			reference_date += timedelta(days=1)
		self.count_table()
		return date_list
###################################
	def clear_table(self):
		self.set('holidays', [])

	def count_table(self):
		counter = 0
		for i in self.holidays:
			counter +=1
		self.total_days=counter

@frappe.whitelist()
def get_events(start, end, filters=None):
	"""Returns events for Gantt / Calendar view rendering.

	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	if filters:
		filters = json.loads(filters)
	else:
		filters = []

	if start:
		filters.append(['Holiday', 'holiday_date', '>', getdate(start)])
	if end:
		filters.append(['Holiday', 'holiday_date', '<', getdate(end)])

	return frappe.get_list('Holiday List',
		fields=['name', '`tabHoliday`.holiday_date', '`tabHoliday`.description'],
		filters = filters,
		update={"allDay": 1})