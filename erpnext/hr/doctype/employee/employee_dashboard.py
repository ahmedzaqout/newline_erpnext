from frappe import _

def get_data():
	return {
		'heatmap': True,
		'heatmap_message': _('This is based on the attendance of this Employee'),
		'fieldname': 'employee',
		'transactions': [
			{
				'label': _(''),
				'items': ['Attendance']
			}
		#	{
		#		'label': _('Self Service'),
		#		'items': ['Attendance','Departure', 'Leave Application','Exit permission','Employee Edit Time','Expense Claim','Employee Transfer', 'Timesheet']
		#	},
		#	{
		#		'label': _('Salary'),
		#		'items': ['Salary Structure', 'Salary Slip']
		#	},
		#	{
		#		'label': _('Training Events/Results'),
		#		'items': ['Training Event', 'Training Result']
		#	},
		#	{
		#		'label': _('Evaluation'),
		#		'items': ['Appraisal']
		#	}
		]
	}
