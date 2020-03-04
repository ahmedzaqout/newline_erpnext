# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, json, ast
import frappe.defaults
from frappe.utils import flt


@frappe.whitelist(allow_guest=True)
def connec():
	import sys
	from zklib import zklib

	import time
	from zklib import zkconst

	zk  = zklib.ZKLib("213.6.151.118", 4370)
	ret = zk.connect()
	return "connection:", ret

@frappe.whitelist(allow_guest=True)
def gett():
	import sys
	sys.path.append("zk")
	from zk import ZK, const

	conn = None
	zk = ZK('213.6.151.118', port=4370, timeout=5, password=0, force_udp=False, ommit_ping=False)
	try:
		print ('Connecting to device ...')
		conn = zk.connect()
		#conn.disconnect()
		print ('Disabling device ...')
		conn.disable_device()
		print ('Firmware Version: : {}'.format(conn.get_firmware_version()))
		# print '--- Get User ---'
		users = conn.get_users()
		for user in users:
			privilege = 'User'
			if user.privilege == const.USER_ADMIN:
				privilege = 'Admin'
			return ('- UID #{}'.format(user.uid))
			print ('  Name       : {}'.format(user.name))
			print ('  Privilege  : {}'.format(privilege))
			print ('  Password   : {}'.format(user.password))
			print ('  Group ID   : {}'.format(user.group_id))
			print ('  User  ID   : {}'.format(user.user_id))

		print ("Voice Test ...")
		conn.test_voice()
		print ('Enabling device ...')
		conn.enable_device()
	except Exception as e:
		print ("Process terminate : {}".format(e))
	finally:
		if conn:
			conn.disconnect()


