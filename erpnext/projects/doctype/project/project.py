# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import flt, getdate, get_url
from frappe import _

from frappe.model.document import Document
from erpnext.controllers.queries import get_filters_cond
from frappe.desk.reportview import get_match_cond
import datetime
from frappe.utils import add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words, getdate
import json

from six import iteritems

class Project(Document):
	def get_feed(self):
		return '{0}: {1}'.format(_(self.status), self.project_name)

	def onload(self):
		"""Load project tasks for quick view"""

		self.set_onload('activity_summary', frappe.db.sql('''select activity_type,
			sum(hours) as total_hours
			from `tabTimesheet Detail` where project=%s and docstatus < 2 group by activity_type
			order by total_hours desc''', self.name, as_dict=True))

		self.update_costing()

	def __setup__(self):
		self.onload()

	

	def get_tasks(self):
		if self.name is None:
			return {}
		else:
			return frappe.get_all("Task", "*", {"project": self.name}, order_by="exp_start_date asc")

	def validate(self):
		self.validate_project_name()
		self.validate_dates()


		#self.send_welcome_email()

	def validate_project_name(self):
		if self.get("__islocal") and frappe.db.exists("Project", self.project_name):
			frappe.throw(_("Project {0} already exists").format(self.project_name))

	def validate_dates(self):
		if self.expected_start_date and self.expected_end_date:
			if getdate(self.expected_end_date) < getdate(self.expected_start_date):
				frappe.throw(_("Expected End Date can not be less than Expected Start Date"))



	
	def update_project(self):
		self.update_percent_complete()
		self.update_costing()
		self.save(ignore_permissions=True)

	def after_insert(self):
		if self.sales_order:
			frappe.db.set_value("Sales Order", self.sales_order, "project", self.name)

	def update_percent_complete(self):
		total = frappe.db.sql("""select count(name) from tabTask where project=%s""", self.name)[0][0]
		if not total and self.percent_complete:
			self.percent_complete = 0
		if (self.percent_complete_method == "Task Completion" and total > 0) or (
			not self.percent_complete_method and total > 0):
			completed = frappe.db.sql("""select count(name) from tabTask where
				project=%s and status in ('Closed', 'Cancelled')""", self.name)[0][0]
			self.percent_complete = flt(flt(completed) / total * 100, 2)

		if (self.percent_complete_method == "Task Progress" and total > 0):
			progress = frappe.db.sql("""select sum(progress) from tabTask where
				project=%s""", self.name)[0][0]
			self.percent_complete = flt(flt(progress) / total, 2)

		if (self.percent_complete_method == "Task Weight" and total > 0):
			weight_sum = frappe.db.sql("""select sum(task_weight) from tabTask where
				project=%s""", self.name)[0][0]
			if weight_sum == 1:
				weighted_progress = frappe.db.sql("""select progress,task_weight from tabTask where
					project=%s""", self.name, as_dict=1)
				pct_complete = 0
				for row in weighted_progress:
					pct_complete += row["progress"] * row["task_weight"]
				self.percent_complete = flt(flt(pct_complete), 2)

	def update_costing(self):
		from_time_sheet = frappe.db.sql("""select
			sum(costing_amount) as costing_amount,
			sum(billing_amount) as billing_amount,
			min(from_time) as start_date,
			max(to_time) as end_date,
			sum(hours) as time
			from `tabTimesheet Detail` where project = %s and docstatus = 1""", self.name, as_dict=1)[0]

		from_expense_claim = frappe.db.sql("""select
			sum(total_sanctioned_amount) as total_sanctioned_amount
			from `tabExpense Claim` where project = %s
			and docstatus = 1""",
										   self.name, as_dict=1)[0]

		self.actual_start_date = from_time_sheet.start_date
		self.actual_end_date = from_time_sheet.end_date

		self.total_costing_amount = from_time_sheet.costing_amount
		self.total_billable_amount = from_time_sheet.billing_amount
		self.actual_time = from_time_sheet.time

		self.total_expense_claim = from_expense_claim.total_sanctioned_amount
		self.update_purchase_costing()
		self.update_sales_amount()
		self.update_billed_amount()

		self.gross_margin = flt(self.total_billed_amount) - (
		flt(self.total_costing_amount) + flt(self.total_expense_claim) + flt(self.total_purchase_cost))

		if self.total_billed_amount:
			self.per_gross_margin = (self.gross_margin / flt(self.total_billed_amount)) * 100

	def update_purchase_costing(self):
		total_purchase_cost = frappe.db.sql("""select sum(base_net_amount)
			from `tabPurchase Invoice Item` where project = %s and docstatus=1""", self.name)

		self.total_purchase_cost = total_purchase_cost and total_purchase_cost[0][0] or 0

	def update_sales_amount(self):
		total_sales_amount = frappe.db.sql("""select sum(base_grand_total)
			from `tabSales Order` where project = %s and docstatus=1""", self.name)

		self.total_sales_amount = total_sales_amount and total_sales_amount[0][0] or 0

	def update_billed_amount(self):
		total_billed_amount = frappe.db.sql("""select sum(base_grand_total)
			from `tabSales Invoice` where project = %s and docstatus=1""", self.name)

		self.total_billed_amount = total_billed_amount and total_billed_amount[0][0] or 0

	def send_welcome_email(self):
		url = get_url("/project/?name={0}".format(self.name))
		messages = (
			_("You have been invited to collaborate on the project: {0}".format(self.name)),
			url,
			_("Join")
		)

		content = """
		<p>{0}.</p>
		<p><a href="{1}">{2}</a></p>
		"""

		#for user in self.users:
		#	if user.welcome_email_sent == 0:
		#		frappe.sendmail(user.user, subject=_("Project Collaboration Invitation"),
		#						content=content.format(*messages))
		#		user.welcome_email_sent = 1

	def on_update(self):
		self.update_dependencies_on_duplicated_project()

	def update_dependencies_on_duplicated_project(self):
		if not self.copied_from:
			self.copied_from = self.name

		if self.name != self.copied_from and self.get('__unsaved'):
			# duplicated project
			dependency_map = {}
			

			for key, value in dependency_map.iteritems():
				task_name = frappe.db.get_value('Task', {"subject": key, "project": self.name})

			for key, value in iteritems(dependency_map):
				task_name = frappe.db.get_value('Task', {"subject": key, "project": self.name })

				task_doc = frappe.get_doc('Task', task_name)

				for dt in value:
					dt_name = frappe.db.get_value('Task', {"subject": dt, "project": self.name})
					task_doc.append('depends_on', {"task": dt_name})
				task_doc.save()


def get_timeline_data(doctype, name):
	'''Return timeline for attendance'''
	return dict(frappe.db.sql('''select unix_timestamp(from_time), count(*)
		from `tabTimesheet Detail` where project=%s
			and from_time > date_sub(curdate(), interval 1 year)
			and docstatus < 2
			group by date(from_time)''', name))


def get_project_list(doctype, txt, filters, limit_start, limit_page_length=20, order_by="modified"):
	return frappe.db.sql('''select distinct project.*
		from tabProject project, `tabProject User` project_user
		where
			(project_user.user = %(user)s
			and project_user.parent = project.name)
			or project.owner = %(user)s
			order by project.modified desc
			limit {0}, {1}
		'''.format(limit_start, limit_page_length),
						 {'user': frappe.session.user},
						 as_dict=True,
						 update={'doctype': 'Project'})


def get_list_context(context=None):
	return {
		"show_sidebar": True,
		"show_search": True,
		'no_breadcrumbs': True,
		"title": _("Projects"),
		"get_list": get_project_list,
		"row_template": "templates/includes/projects/project_row.html"
	}

def get_users_for_project(doctype, txt, searchfield, start, page_len, filters):
	conditions = []
	return frappe.db.sql("""select name, concat_ws(' ', first_name, middle_name, last_name)
		from `tabUser`
		where enabled=1
			and name not in ("Guest", "Administrator")
			and ({key} like %(txt)s
				or full_name like %(txt)s)
			{fcond} {mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, full_name), locate(%(_txt)s, full_name), 99999),
			idx desc,
			name, full_name
		limit %(start)s, %(page_len)s""".format(**{
		'key': searchfield,
		'fcond': get_filters_cond(doctype, filters, conditions),
		'mcond': get_match_cond(doctype)
	}), {
							 'txt': "%%%s%%" % txt,
							 '_txt': txt.replace("%", ""),
							 'start': start,
							 'page_len': page_len
						 })


@frappe.whitelist()
def get_cost_center_name(project):
	return frappe.db.get_value("Project", project, "cost_center")

@frappe.whitelist()
def hourly_reminder():
	project = frappe.db.sql("""SELECT `tabProject`.name FROM `tabProject` WHERE `tabProject`.frequency = "Hourly" and (CURTIME() BETWEEN `tabProject`.from and `tabProject`.to) AND `tabProject`.collect_progress = 1 ORDER BY `tabProject`.name;""")
	create_project_update(project)

@frappe.whitelist()
def twice_daily_reminder():
	project = frappe.db.sql("""SELECT `tabProject User`.user FROM `tabProject User` INNER JOIN `tabProject` ON `tabProject`.project_name = `tabProject User`.parent WHERE (`tabProject`.frequency = "Twice Daily") AND ((`tabProject`.first_email BETWEEN DATE_ADD(curtime(), INTERVAL -15 MINUTE) AND DATE_ADD(curtime(), INTERVAL 15 MINUTE)) OR (`tabProject`.second_email BETWEEN DATE_ADD(curtime(), INTERVAL -15 MINUTE) AND DATE_ADD(curtime(), INTERVAL 15 MINUTE))) AND `tabProject`.collect_progress = 1;""")
	create_project_update(project)

@frappe.whitelist()
def daily_reminder():
	project = frappe.db.sql("""SELECT `tabProject User`.user FROM `tabProject User` INNER JOIN `tabProject` ON `tabProject`.project_name = `tabProject User`.parent WHERE (`tabProject`.frequency = "Daily") AND (`tabProject`.daily_time_to_send BETWEEN DATE_ADD(curtime(), INTERVAL -15 MINUTE) AND DATE_ADD(curtime(), INTERVAL 15 MINUTE)) AND `tabProject`.collect_progress = 1;""")
	create_project_update(project)

@frappe.whitelist()
def weekly():
	today = datetime.datetime.now().strftime("%A")
	project = frappe.db.sql("""SELECT `tabProject User`.user FROM `tabProject User` INNER JOIN `tabProject` ON `tabProject`.project_name = `tabProject User`.parent WHERE (`tabProject`.frequency = "Weekly") AND (`tabProject`.day_to_send = %s) AND (`tabProject`.weekly_time_to_send BETWEEN DATE_ADD(curtime(), INTERVAL -15 MINUTE) AND DATE_ADD(curtime(), INTERVAL 15 MINUTE)) AND `tabProject`.collect_progress = 1""", today)
	create_project_update(project)

@frappe.whitelist()
def times_check(from1, to, first_email, second_email, daily_time_to_send, weekly_time_to_send):
    from1 = datetime.datetime.strptime(from1, "%H:%M:%S")
    from1 = from1.strftime("%H:00:00")
    to = datetime.datetime.strptime(to, "%H:%M:%S")
    to = to.strftime("%H:00:00")
    first_email = datetime.datetime.strptime(first_email, "%H:%M:%S")
    first_email = first_email.strftime("%H:00:00")
    second_email = datetime.datetime.strptime(second_email, "%H:%M:%S")
    second_email = second_email.strftime("%H:00:00")
    daily_time_to_send = datetime.datetime.strptime(daily_time_to_send, "%H:%M:%S")
    daily_time_to_send = daily_time_to_send.strftime("%H:00:00")
    weekly_time_to_send = datetime.datetime.strptime(weekly_time_to_send, "%H:%M:%S")
    weekly_time_to_send = weekly_time_to_send.strftime("%H:00:00")
    return {"from1": from1, "to": to, "first_email": first_email, "second_email": second_email,"daily_time_to_send": daily_time_to_send, "weekly_time_to_send": weekly_time_to_send}


#Call this function in order to generate the Project Update for a specific project
def create_project_update(project):
	data = []
	date_today = datetime.date.today()
	time_now = frappe.utils.now_datetime().strftime('%H:%M:%S')
	for projects in project:
		project_update_dict = {
			"doctype" : "Project Update",
			"project" : projects[0],
			"date": date_today,
			"time": time_now,
			"naming_series": "UPDATE-.project.-.YY.MM.DD.-"
		}
		project_update = frappe.get_doc(project_update_dict)
		project_update.insert()
		#you can edit your local_host
		local_host = "http://localhost:8003"
		project_update_url = "<a class = 'btn btn-primary' href=%s target='_blank'>" % (local_host +"/desk#Form/Project%20Update/" + (project_update.name)) + ("CREATE PROJECT UPDATE" + "</a>")
		data.append(project_update_url)

		email = frappe.db.sql("""SELECT user from `tabProject User` WHERE parent = %s;""", project[0])
		for emails in email:
			frappe.sendmail(
				recipients=emails,
				subject=frappe._(projects[0]),
				header=[frappe._("Please Update your Project Status"), 'blue'],
				message= project_update_url
			)
	return data

@frappe.whitelist()
def create_kanban_board_if_not_exists(project):
	from frappe.desk.doctype.kanban_board.kanban_board import quick_kanban_board

	if not frappe.db.exists('Kanban Board', project):
		quick_kanban_board('Task', project, 'status')

	return True

@frappe.whitelist()
def get_days(start,end):
	diff=date_diff(end,start)

	company=frappe.db.get_value("Global Defaults", None, "default_company")
	holiday_list = frappe.db.get_value("Company", company, "default_holiday_list")

	if not holiday_list:
		frappe.throw(_('Please set a default Holiday List for the Company {1}').format(company))

	holidays = frappe.db.sql_list('''select holiday_date from `tabHoliday`
		where
			parent=%(holiday_list)s
			and holiday_date >= %(start_date)s
			and holiday_date <= %(end_date)s''', {
				"holiday_list": holiday_list,
				"start_date": start,
				"end_date": end
			})

	holidays = [cstr(i) for i in holidays]
	
	dd=(diff - len(holidays)) +1
	if dd > 0:
		return {"period":dd,
			"ho":len(holidays)}
	else:
		return {"period":0,
			"ho":len(holidays)}


@frappe.whitelist()
def get_end(start,period):

	company=frappe.db.get_value("Global Defaults", None, "default_company")
	holiday_list = frappe.db.get_value("Company", company, "default_holiday_list")
	if not start:
		frappe.throw(_('You have to choose the start date'))
	if not holiday_list:
		frappe.throw(_('Please set a default Holiday List for the Company {1}').format(employee, company))

	holidays = frappe.db.sql_list('''select holiday_date from `tabHoliday`
		where
			parent=%(holiday_list)s
			and holiday_date >= %(start_date)s''', {
				"holiday_list": holiday_list,
				"start_date": start
			})

	holidays = [cstr(i) for i in holidays]
	end_date=start
	i=1
	while i < period:
		date_1 = datetime.datetime.strptime(start, "%Y-%M-%d")
		end_date=frappe.datetime.add_days(date_1, 1);
		start=end_date.strftime("%Y-%m-%d")
		if start not in holidays:
			i=i+1;




	return {"end":end_date.strftime("%Y-%m-%d")} 
	
@frappe.whitelist()
def update_tasks(project):
	time_sheet = frappe.db.sql("""select r.employee ,r.employee_name , td.project, td.task,r.date,td.hours  from `tabActivity Detail` as td left join  `tabEmployee Task` as r on r.name = td.parent where r.docstatus <2 and td.project = %(project)s order by r.date """,{"project": project}, as_list=1)


	data=[]
	total=0.0
	m=frappe.db.sql("""delete from `tabProject Task` where parenttype= "Project" and parent = %(project)s """,{"project": project})
	for i in range(len(time_sheet)): 
		r=frappe.get_doc({"doctype":"Project Task",
		"employee":time_sheet[i][0],
		"employee_name" : time_sheet[i][1],
		"task" : time_sheet[i][3],
		"date" :time_sheet[i][4],
		"hours":time_sheet[i][5],
		"parent" : project,
		"parenttype" : "Project",
		"parentfield" : "tasks",
		"idx" : i+1
		}).insert(ignore_permissions=True)
		data.append(r)
		total+=float(time_sheet[i][5])
		
	return {'total':total,
		'data' : data}



	
