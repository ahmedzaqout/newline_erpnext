import json, os

from frappe.desk.page.setup_wizard.setup_wizard import setup_complete
from erpnext.setup.setup_wizard import setup_wizard

def complete():
	with open(os.path.join(os.path.dirname(__file__),
		'data', 'data.json'), 'r') as f:
		data = json.loads(f.read())

	setup_wizard.setup_complete(data)
	#setup_complete(data)



