# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from datetime import datetime
import traceback
import argparse
import time
import datetime
import codecs
from builtins import input
from frappe.utils import getdate,get_time, time_diff,time_diff_in_seconds,time_diff_in_hours,cstr,now,get_url
import sys
import os
import signal
import json
sys.path.append("zk")
#sys.path.insert(1,os.path.abspath("./pyzk"))

from zk import ZK, const
from zk.user import User
from zk.finger import Finger
from zk.attendance import Attendance
from zk.exception import ZKErrorResponse, ZKNetworkError


class FingerPrintDeviceControlPanel(Document):
	pass


class BasicException(Exception):
    pass


@frappe.whitelist()
def test_connection(ip_address=None, port=None):
	#frappe.publish_realtime('msgprint', 'Starting long job...')
	devices= get_devices()
	for device in devices:
		print device.ip
		print device.port
		if device.ip  and device.port:
			ip_address =device.ip
			port = device.port
			conn = None
			zk = ZK(ip_address, port=int(port), timeout=5, password=0, force_udp=False, ommit_ping=False)
			print ip_address
			print port
			try:
		    	    	conn = zk.connect()
				return {"conn":"success"}

			except Exception, e:
				print "error";
			finally:
				if conn:
					conn.disconnect()



@frappe.whitelist()
def disconnect_connection(ip_address=None, port=None):
	ip_address='213.6.151.118'
	port =4370
	conn = None
	zk = ZK(ip_address, port=int(port), timeout=5, password=0, force_udp=False, ommit_ping=False)
	try:
		print ('Disconnecting device ...')
    	    	conn = zk.connect()
		conn.disconnect()
		conn.poweroff()
		conn.restart()

		return conn

	except Exception, e:
		print "Process terminate : {}".format(e)
		return 'error'
	finally:
		if conn:
			conn.disconnect()


@frappe.whitelist()
def get_users():
	conn = test_connection('213.6.151.118',4370)
	print str(conn)
	try:
    		# print '--- Get User ---'
	        users = conn.get_users()
		print users
	        for user in users:
		        privilege = 'User'
		        if user.privilege == const.USER_ADMIN:
	            		privilege = 'Admin'
		        print ('- UID #{}'.format(user.uid))
		        print ('  Name       : {}'.format(user.name))
		        print ('  Privilege  : {}'.format(privilege))
		        print ('  Password   : {}'.format(user.password))
		        print ('  Group ID   : {}'.format(user.group_id))
		        print ('  User  ID   : {}'.format(user.user_id))

	    		print ("Voice Test ...")
		    	conn.test_voice()


	except Exception, e:
		print "Process terminate : {}".format(e)
		return 'error'


@frappe.whitelist()
def zk_exec():
	att_file = open('../attendance_log/att_logs.txt','a')
	att_file.write('Starting...'+str(now())+'\n')
	att_file.close

	data={}
	chmod7=False
	if not internet_on:
		send_alert_email()
		return False

	def add_attendance(user_id,time,atype):
		try:	
			site_name = cstr(frappe.local.site)
			#print  site_name
			filename = '../attendance_log/ATT'+site_name+str(getdate(time))+'.txt'
			#print "user_id: "+str(user_id)

			data={'user_id':user_id,'time':time,'atype':atype}
			if not os.path.exists(filename):
				filename = '../attendance_log/ATT.txt'
				print "True"
				chmod7=True

			att_file = open(filename,'a')
			#if chmod7: os.chmod(filename, 0777)
			att_file.write(str(data)+'\n')
			att_file.close
			#print str(att_file)
			return data
		except frappe.LinkValidationError:
			return False

	def signal_handler(signal, frame):
		sys.exit(0)

	def zk_isconnected():
		connected = frappe.db.get_single_value("Finger Print Device Control Panel", "connected")
		print "connected: "+str(connected)
		if connected==1 :
			print "Already connected: "+str(connected)
			return True
	
	def zk_disconnect():
		frappe.db.set_value("Finger Print Device Control Panel", "Finger Print Device Control Panel", "connected",0)
		frappe.db.commit()

	def zk_connect():
		connected =frappe.db.set_value("Finger Print Device Control Panel", "Finger Print Device Control Panel", "connected",1)
		frappe.db.sql(" update  `tabSingles` set value=1  where doctype='Finger Print Device Control Panel' and field='connected'")
		frappe.db.commit()
		print "set connect: "+str(connected)

	############################################################################################################
	conn = None
	reconnect = False
	#if device_status(True,False,False): 
	#	return "Already connected"

	ip_address = frappe.db.get_single_value("Finger Print Device Control Panel", "ip_address") or '213.6.151.118'
	port = frappe.db.get_single_value("Finger Print Device Control Panel", "port") or 4370 
	start_time = frappe.db.get_single_value("Finger Print Device Control Panel", "start_time") 
	end_time = frappe.db.get_single_value("Finger Print Device Control Panel", "end_time") 
	#conn_dellay = frappe.db.sql("select format(( TIME_TO_SEC('%s')- TIME_TO_SEC('%s') ),0)" %(str(end_time), str(start_time) ) )

	zk = ZK(ip_address, port=int(port), timeout=5, password=0, force_udp=False, ommit_ping=False)
	try:
		print ('Connecting to device ...')
		######logs
		att_file = open('../attendance_log/att_logs.txt','a')
		att_file.write('Connecting to device ...'+'\n')
		att_file.close
		######

    	    	conn = zk.connect()
		#conn.restart()
		if not conn:
			print 'discon'
			conn.restart()
			conn.power_off()

		print ('Disabling device ...')
    		dis = conn.disable_device()
		#print 'dis' + str(dis)
    		print ('Firmware Version: : {}'.format(conn.get_firmware_version()))
		##############--- Live Capture! (press ctrl+C to break) ---###########
		print ('')
		print ('--- Live Capture! (press ctrl+C to break) ---')
		counter = 0
		#device_status(False,False,True)
		#reconnect =True
		#conn.end_live_capture = True

		######logs
		att_file = open('../attendance_log/att_logs.txt','a')
		att_file.write('Live Capture ...'+'\n')
		att_file.close
		######
		for att in conn.live_capture():# using a generator!

    			if att is None:
        			#counter += 1 #enable to implemet a poorman timeout
        			print ("timeout {}".format(counter))
				######logs
				att_file = open('../attendance_log/att_logs.txt','a')
				att_file.write("timeout {}".format(counter)+'\n')
				att_file.close
				######
    			else:
				print ("ATT {:>6}: uid:{:>3}, user_id:{:>8} t: {}, s:{} p:{}".format(counter, att.uid, att.user_id, att.timestamp, att.status, att.punch))
				######logs
				att_file = open('../attendance_log/att_logs.txt','a')
				att_file.write("ATT {:>6}: uid:{:>3}, user_id:{:>8} t: {}, s:{} p:{}".format(counter, att.uid, att.user_id, att.timestamp, att.status, att.punch)+'\n')
				att_file.close
				######

				
				data= add_attendance(att.user_id, att.timestamp,att.punch)
       				#conn.end_live_capture = True
				#print str(call_att)
				if data:
					print "returned data: "+str(data)
					#signal.signal(signal.SIGINT, signal_handler)#
					#break
					#zk_exec()


    			if counter >= 200:
       				conn.end_live_capture = True
		print('')
		print('--- capture End!---')
		print ('')
	    	print ('Enabling device ...')
	    	conn.enable_device()
		print str(data)
	except Exception as e:
		print ("Process terminate : {}".format(e))
		######logs
		att_file = open('../attendance_log/att_logs.txt','a')
		att_file.write("Process terminate : {}".format(e)+str(now())+'\n')
		att_file.close
		######

		if reconnect: zk_exec()
		#device_status(False,True,False)
		if str(e) == '[Errno 104] Connection reset by peer' or "can't reach device" in str(e):
			send_alert_email()
			if conn: conn.restart()
			#zk_exec()
		print "In Error: "+str(data)
	finally:
    		if conn:
        		conn.disconnect()
			#device_status(False,True,False)
        		print ('ok bye!')



@frappe.whitelist()
def add_attendances():
	try:	
		import os.path
		
		#test = open('../test.txt','a')
		#os.chmod('../test.txt', 0777)
		#test.write('mmmmm')
		site_name = cstr(frappe.local.site)
		filename = '../attendance_log/ATT'+site_name+str(getdate(now()))+'.txt'
	#	filename = '../att.txt'
		print filename
		if not os.path.exists(filename):
			filename = '../attendance_log/ATT.txt'
			print "does not exist"
			#return False 

		att_file = open(filename,'r')
		#with open(filename,'r') as att_file:
		#print (att_file.read())
		for line in att_file.readlines():
			if len(line.strip()) ==0:
				continue
			dic= eval(line)
			for d in dic:
				if d =='user_id': user_id= dic[d]
				if d =='time': time= dic[d]
				if d =='atype': atype= dic[d]
				#print str(d) + ': ' + str(dic[d])


			emp = frappe.db.get_value("Employee Personal Detail",{"fp_id": user_id}, ["name","employee_name"],as_dict=1)
			if emp:
				#check_duplicat(user_id,time,atype)
				if atype == 0: #att
					if not frappe.get_value('Attendance',{'employee':emp.name,'attendance_date':getdate(time)},"name"):
						att = frappe.new_doc('Attendance')
						att.update({
							'employee':emp.name,
							'employee_name':emp.employee_name,
							'attendance_time':get_time(time),
							'attendance_date':getdate(time),
							'status':'Present',
							'docstatus':1
								})
						att.flags.ignore_validate = True
						att.insert(ignore_permissions=True)

				elif atype == 1: #departure
					if not frappe.get_value('Departure',{'employee':emp.name,'departure_date':getdate(time)},"name"):
						dept = frappe.new_doc('Departure')
						dept.update({
							'employee':emp.name,
							'employee_name':emp.employee_name,
							'departure_time':get_time(time),
							'departure_date':getdate(time),
							'status':'Present',
							'docstatus':1
								})
						dept.flags.ignore_validate = True
						dept.insert(ignore_permissions=True)

				elif atype == 5: #exit
					if not frappe.get_value('Exit permission',{'employee':emp.name,'permission_date':getdate(time)},"name"):
						exit = frappe.new_doc('Exit permission')
						exit.update({
							'employee':emp.name,
							'employee_name':emp.employee_name,
							'from_date':get_time(time),
							'permission_date':getdate(time),
							'permission_type':'Exit with return',
							'type':'Exit'
								})
						exit.flags.ignore_validate = True
						exit.insert(ignore_permissions=True)

				elif atype == 4: #return
					if not frappe.get_value('Exit permission',{'employee':emp.name,'permission_date':getdate(time)},"name"):
						ret = frappe.new_doc('Exit permission')
						ret.update({
							'employee':emp.name,
							'employee_name':emp.employee_name,
							'to_date':get_time(time),
							'permission_date':getdate(time),
							'permission_type':'Exit with return',
							'type':'Return'
								})
						ret.flags.ignore_validate = True
						ret.insert(ignore_permissions=True)

		return "success"
	except frappe.LinkValidationError:
		return False


@frappe.whitelist()
def check_duplicat(user_id,time,atype):
	pass


@frappe.whitelist()
def send_alert_email():
	try:
		url = get_url("Form/Finger Print Device Control Panel")
		#messages = (_("Your Finger Print Device have a connection problem,reset it Plz "),url,_("Visit"))

	#frappe.sendmail("mesa_safd@hotmail.com", subject=_("Can not reach Finger Print Device!"),content=content.format(*messages))
		frappe.sendmail(
			recipients= "maysaaelsafadi@gmail.com",
			sender="mesa_safd@hotmail.com",
			subject=_("Can not reach Finger Print Device!"),
			message=_("Your Finger Print Device have a connection problem. Plz, reset it")
		)
		return _("Email sent")
	except frappe.OutgoingEmailError:
		pass


@frappe.whitelist()
def device_status(isconnected=None,disconnect=None, connect=None):
	writ =-1
	if isconnected:
		print "isconnected" 
		#read = open('../zk_connection.txt','r')
		with open('../zk_connection.txt','r') as read:
			if str(read.readline()) == '1':
				print 'rr '+str(read.readline())
				return True

		#for line in read.readline():
		#	print line
		#	if line == '1':
		#		return True

	if connect: writ= 1
	if disconnect: writ= 0
	print 'writ '+str(writ)
	
	if writ != -1:
		print str(writ)
		#conn_file = open('../zk_connection.txt','w')
		with open('../zk_connection.txt','w') as conn_file:
		#os.chmod('../zk_connection.txt', 0o777)
			conn_file.write(str(writ))
			conn_file.close

		

@frappe.whitelist()
def update_connection():
	read = open('../zk_connection.txt','r')
	for i in read.readline() :
		if i == '1':
			connected =frappe.db.set_value("Finger Print Device Control Panel", "Finger Print Device Control Panel", "connected",1)
		if i == '0':
			connected =frappe.db.set_value("Finger Print Device Control Panel", "Finger Print Device Control Panel", "connected",0)


def internet_on():
	import urllib2
	try:
		urllib2.urlopen('http://216.58.192.142', timeout=1)
		return True
	except urllib2.URLError as err: 
		return False




####################### NEW ###############################
def connect_zk():
	ip_address = frappe.db.get_single_value("Finger Print Device Control Panel", "ip_address") or '213.6.151.118'
	port = frappe.db.get_single_value("Finger Print Device Control Panel", "port") or 4370 
	start_time = frappe.db.get_single_value("Finger Print Device Control Panel", "start_time") 
	end_time = frappe.db.get_single_value("Finger Print Device Control Panel", "end_time") 
	#conn_dellay = frappe.db.sql("select format(( TIME_TO_SEC('%s')- TIME_TO_SEC('%s') ),0)" %(str(end_time), str(start_time) ) )
	zk = ZK(ip_address, port=int(port), timeout=5, password=0, force_udp=False, ommit_ping=False)
	return zk

def get_devices():
	ip_address = frappe.get_all("Finger Print Device", ['ip','port'],filters={"parenttype" : "Finger Print Device Control Panel","parentfield":"finger_print_devices"})
	#zk = ZK(ip_address, port=int(port), timeout=5, password=0, force_udp=False, ommit_ping=False)
	return ip_address


@frappe.whitelist()
def zk_upload_attendance(month=None):
    	now = datetime.datetime.today().replace(microsecond=0)

	now_hour = now.strftime('%H')
	print str(now_hour)
	#if (not month) and ((now_hour !='20') and (now_hour !='06') and (now_hour !='14') and (now_hour !='09') and (now_hour != 16)):
	#	print "False"
	#	return False

	if month:
		month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].index(month) + 1
	else: month= now.month

	conn = None
	zk = connect_zk()
	try:
	    print('Connecting to device ...')
	    conn = zk.connect()
	    #print('SDK build=1      : %s' % conn.set_sdk_build_1()) # why?
	    print ('Disabling device ...')
	    conn.disable_device()
	    #fmt = conn.get_extend_fmt()
	    #fmt = conn.get_user_extend_fmt()
	    #net = conn.get_network_params()
	    #print ('IP:{} mask:{} gateway:{}'.format(net['ip'],net['mask'], net['gateway']))
	    zk_time = conn.get_time()
	    dif = abs(zk_time - now).total_seconds()
	    print ('Time             : {}'.format(zk_time))
	    if dif > 120:
	        print("WRN: TIME IS NOT SYNC!!!!!! (local: %s) use command -u to update" % now)
	   # print ('Firmware Version : {}'.format(conn.get_firmware_version()))
	    #print ('Platform         : %s' % conn.get_platform())
	    #print ('DeviceName       : %s' % conn.get_device_name())
	    #print ('Pin Width        : %i' % conn.get_pin_width())
	    #print ('Serial Number    : %s' % conn.get_serialnumber())
	    #print ('MAC: %s' % conn.get_mac())
	    #print ('')
	    print ('--- sizes & capacity ---')
	    conn.read_sizes()
	    print (conn)
	    print ('')

	    #print ('--- Get User ---')
	    #inicio = time.time()
	    #users = conn.get_users()
	    #final = time.time()
	    #print ('    took {:.3f}[s]'.format(final - inicio))
	    max_uid = 0
	    prev = None
	    #if not True:
	     #   for user in users:
	      #      privilege = 'User'
	       #     if user.uid > max_uid:
	        #        max_uid = user.uid
	         #   privilege = 'User' if user.privilege == const.USER_DEFAULT else 'Admin-%s' % user.privilege
	          #  print ('-> UID #{:<5} Name     : {:<27} Privilege : {}'.format(user.uid, user.name, privilege))
	           # print ('              Group ID : {:<8} User ID : {:<8} Password  : {:<8} Card : {}'.format(user.group_id, user.user_id, user.password, user.card))
	            #print (len (user.repack73()), user.repack73().encode('hex'))
	            #print ('')
####################################
	    print ("Read Records...")
            inicio = time.time()
            attendance = conn.get_attendance()
            final = time.time()
            print ('    took {:.3f}[s]'.format(final - inicio))
            i = 0
            for att in attendance:


               # print ("user_id:{:>8} t: {}, p:{}".format(att.user_id, att.timestamp, att.punch))
		try:

			#if str(getdate(att.timestamp)) == '2019-02-12': 
			if (att.timestamp).month == month: 
				update_att(att.user_id,att.punch, att.timestamp)
              			i += 1
				print ("ATT {:>6}: uid:{:>3}, user_id:{:>8} t: {}, s:{} p:{}".format(i, att, att.user_id, att.timestamp, att.status, att.punch))

		except Exception as e:
			print ('Attendance script error')
			pass

            print ('    took {:.3f}[s]'.format(final - inicio))
	    print ('')
	    print ('--- sizes & capacity ---')
	    conn.read_sizes()
	    print (conn)
	    
	    print ('')
	    return {"success":i}
	except BasicException as e:
	    print (e)
	    print ('')
	except Exception as e:
	    print ("Process terminate : {}".format(e))
	    print ("Error: %s" % sys.exc_info()[0])
	    print ('-'*60)
	    traceback.print_exc(file=sys.stdout)
	    print ('-'*60)
	finally:
	    if conn:
	        print ('Enabling device ...')
	        conn.enable_device()
	        conn.disconnect()
	        print ('ok bye!')
	        print ('')
	   	return {"success":i}


@frappe.whitelist()
def upload_attendance(month=None,toClear=False):
    	now = datetime.datetime.today().replace(microsecond=0)

	now_hour = now.strftime('%H')
	print str(now_hour)
	#if (not month) and ((now_hour !='20') and (now_hour !='06') and (now_hour !='14') and (now_hour !='09') and (now_hour != 16)):
	#	print "False"
	#	return False

	if month:
		month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].index(month) + 1
	else: month= now.month

	conn = None
	devices= get_devices()
	for device in devices:
		print device.ip
		print device.port
		if device.ip  and device.port:
			ip_address = device.ip 
			port=device.port
			print "port"
			print device.ip                                                                                               
			
			zk = ZK(ip_address, port=int(port), timeout=5, password=0, force_udp=False, ommit_ping=False)
			try:
			    print('Connecting to device ...')
			    conn = zk.connect()
			    print ('Disabling device ...')
			    conn.disable_device()
			    zk_time = conn.get_time()
			    newtime = datetime.datetime.today() +datetime.timedelta(hours = 2) 
			    conn.set_time(newtime)
			    print newtime
			    dif = abs(zk_time - now).total_seconds()
			    print ('Time             : {}'.format(zk_time))
			    if dif > 120:
				print("WRN: TIME IS NOT SYNC!!!!!! (local: %s) use command -u to update" % now)
			   
			    print ('--- sizes & capacity ---')
			    conn.read_sizes()
			    print (conn)
			    print ('')

			    #print ('--- Get User ---')
			    #inicio = time.time()
			    #users = conn.get_users()
			    #final = time.time()
			    #print ('    took {:.3f}[s]'.format(final - inicio))
			    max_uid = 0
			    prev = None
			    #if not True:
			     #   for user in users:
			      #      privilege = 'User'
			       #     if user.uid > max_uid:
				#        max_uid = user.uid
				 #   privilege = 'User' if user.privilege == const.USER_DEFAULT else 'Admin-%s' % user.privilege
				  #  print ('-> UID #{:<5} Name     : {:<27} Privilege : {}'.format(user.uid, user.name, privilege))
				   # print ('              Group ID : {:<8} User ID : {:<8} Password  : {:<8} Card : {}'.format(user.group_id, user.user_id, user.password, user.card))
				    #print (len (user.repack73()), user.repack73().encode('hex'))
				    #print ('')
		####################################
			    print ("Read Records...")
			    inicio = time.time()
			    attendance = conn.get_attendance()
			    final = time.time()
			    print ('    took {:.3f}[s]'.format(final - inicio))
			    i = 0
			    for att in attendance:
				i += 1

			       # print ("user_id:{:>8} t: {}, p:{}".format(att.user_id, att.timestamp, att.punch))
				try:

					#if str(getdate(att.timestamp)) == '2019-02-12': 
					if (att.timestamp).month == month: 
						update_att(att.user_id,att.punch, att.timestamp)
						print ("ATT {:>6}: uid:{:>3}, user_id:{:>8} t: {}, s:{} p:{}".format(i, att.uid, att.user_id, att.timestamp, att.status, att.punch))
						if toClear == False:
							send_device_data_to_database(str(att.uid),att.user_id ,att.timestamp ,att.status,att.punch)

						print "port"
						print device.ip

				except  Exception as e:
					print ('Attendance script error')
					pass

			    print ('    took {:.3f}[s]'.format(final - inicio))
			    print ('')
			    print ('--- sizes & capacity ---')
			    conn.read_sizes()
			    print (conn)
			    
			    print ('')
			except BasicException as e:
			    print (e)
			    print ('')
			except Exception as e:
			    print ("Process terminate : {}".format(e))
			    print ("Error: %s" % sys.exc_info()[0])
			    print ('-'*60)
			    traceback.print_exc(file=sys.stdout)
			    print ('-'*60)
			finally:
			    if conn:
				print ('Enabling device ...')
				conn.enable_device()
				conn.disconnect()
				print ('ok bye!')
				print ('')
				#return "success"



def update_att(user_id,atype,time):
	#print "user_id:"+str(user_id)+" ,atype: "+str(atype)+" ,time: "+str(time)
	emp = frappe.db.get_value("Employee Personal Detail",{"fp_id": user_id}, ["name","employee_name"],as_dict=1)
	if emp:
		if atype == 0: #att
			attendance = frappe.get_value('Attendance',{'employee':emp.name,'attendance_date':getdate(time),'status':'Absent'},"name")
			if attendance:
				frappe.db.sql("delete from tabAttendance where name=%s",attendance)
				"deleted: "+str(attendance)
			att_doc =frappe.get_value('Attendance',{'employee':emp.name,'attendance_date':getdate(time),'docstatus':1,'attendance_time':get_time(time)},"name")
			dupplicated_att =frappe.get_value('Attendance',{'employee':emp.name,'attendance_date':getdate(time),'docstatus':1},"name")
			if not att_doc and not dupplicated_att :
				att = frappe.new_doc('Attendance')
				att.update({
					'employee':emp.name,
					'employee_name':emp.employee_name,
					'attendance_time':get_time(time),
					'attendance_date':getdate(time),
					'status':'Present',
					'docstatus':1
						})
				att.insert(ignore_permissions=True)
	

		elif atype == 1: #departure
			departure = frappe.get_value('Departure',{'employee':emp.name,'departure_date':getdate(time), 'status':'Absent'},"name")
			if departure:
				frappe.db.sql("delete from tabDeparture where name=%s",departure)

			dupplicated_dep= frappe.get_value('Departure',{'employee':emp.name,'departure_date':getdate(time),'docstatus':1},"name")

			if not dupplicated_dep and not frappe.get_value('Departure',{'employee':emp.name,'departure_date':getdate(time),'docstatus':1, 'departure_time':get_time(time)},"name"):
				dept = frappe.new_doc('Departure')
				dept.update({
					'employee':emp.name,
					'employee_name':emp.employee_name,
					'departure_time':get_time(time),
					'departure_date':getdate(time),
					'status':'Present',
					'docstatus':1
						})
				dept.insert(ignore_permissions=True)


		elif atype == 5: #exit
			if not frappe.get_value('Exit permission',{'employee':emp.name,'permission_date':getdate(time),'type':'Exit','from_date':get_time(time)},"name"):
				exit = frappe.new_doc('Exit permission')
				exit.update({
					'employee':emp.name,
					'employee_name':emp.employee_name,
					'from_date':get_time(time),
					'permission_date':getdate(time),
					'permission_type':'Exit with return',
					'type':'Exit'
						})
				exit.insert(ignore_permissions=True)
				#exit.submit()

		elif atype == 4: #return
			if frappe.get_value('Exit permission',{'employee':emp.name,'permission_date':getdate(time),'type':'Exit'},"name") and not frappe.get_value('Exit permission',{'employee':emp.name,'permission_date':getdate(time),'type':'Return','to_date':get_time(time)},"name") :
				ret = frappe.new_doc('Exit permission')
				ret.update({
					'employee':emp.name,
					'employee_name':emp.employee_name,
					'to_date':get_time(time),
					'permission_date':getdate(time),
					'permission_type':'Exit with return',
					'type':'Return'
					#'docstatus': 1,
					#'workflow_state':'Final Approval'
						})
				ret.insert(ignore_permissions=True)
				ret.submit()

		frappe.db.commit()
		frappe.clear_cache()



@frappe.whitelist()
def backup_attendance():
	zk = connect_zk()
	try:
		conn = zk.connect()

 	    	print ("Read Records...")
            	attendance = conn.get_attendance()
            	i = 0
            	for att in attendance:
                	i += 1
			att_file = open('../att_logs.txt','a')
			att_file.write(("ATT {:>6}: uid:{:>3}, user_id:{:>8} t: {}, s:{} p:{}".format(i, att.uid, att.user_id, att.timestamp, att.status, att.punch))+'\n')
			att_file.close

	    	conn.disable_device()
		conn.clear_attendance()

	except Exception as e:
    		print ("Process terminate : {}".format(e))
    		print ("Error: %s" % sys.exc_info()[0])
   		print ('-'*60)
   		traceback.print_exc(file=sys.stdout)
    		print ('-'*60)
	finally:
    		if conn:
        		print ('Enabling device ...')
        		conn.enable_device()
        		conn.disconnect()
        		print ('ok bye!')
        		print ('')


@frappe.whitelist()
def backuprest_attendance():
	def erase_device(conn, serialnumber, clear_attendance=False):
	    """input serial number to corroborate."""
	    print ('WARNING! the next step will erase the current device content.')
	    conn.disable_device()
	    print ('Erasing device...')
	    conn.clear_data()
	    if clear_attendance:
	        print ('Clearing attendance too!')
	        conn.clear_attendance()
	    conn.read_sizes()
	    print (conn)

	zk = connect_zk()
	try:
		print('Connecting to device ...')
		conn = zk.connect()
		serialnumber = conn.get_serialnumber()
		fp_version = conn.get_fp_version()
		print ('Serial Number    : {}'.format(serialnumber))
		print ('Finger Version   : {}'.format(fp_version))
		filename = "../{}.json.bak".format(serialnumber)
		print ('')

		print ('Reading file {}'.format(filename))
		infile = open(filename, 'r')
		infile.close()
		#compare versions...
		if data['version'] != '1.00jut':
		    raise BasicException("file with different version... aborting!")
		if data['fp_version'] != fp_version:
		    raise BasicException("fingerprint version mismmatch {} != {} ... aborting!".format(fp_version, data['fp_version']))
		#TODO: check data consistency...
		users = [User.json_unpack(u) for u in data['users']]
		#print (users)
		print ("INFO: ready to write {} users".format(len(users)))
		templates = [Finger.json_unpack(t) for t in data['templates']]
		#print (templates)
		print ("INFO: ready to write {} templates".format(len(templates)))
		erase_device(conn, serialnumber, False)
		print ('Restoring Data...')
		for u in users:
		    #look for Templates
		    temps = list(filter(lambda f: f.uid ==u.uid, templates))
		    #print ("user {} has {} fingers".format(u.uid, len(temps)))
		    conn.save_user_template(u,temps)
		conn.enable_device()
		print ('--- final sizes & capacity ---')
		conn.read_sizes()
		print (conn)
		return "success"

	except BasicException as e:
	    print (e)
	    print ('')
	except Exception as e:
	    print ("Process terminate : {}".format(e))
	    print ("Error: %s" % sys.exc_info()[0])
	    print ('-'*60)
	    traceback.print_exc(file=sys.stdout)
	    print ('-'*60)
	finally:
	    if conn:
	        print ('Enabling device ...')
	        conn.enable_device()
	        conn.disconnect()
	        print ('ok bye!')
	        print ('')



@frappe.whitelist()
def test():
	att_file = open('../att_logs.txt','a')
	att_file.write("ATT "+'\n')
	att_file.close
    	now = datetime.datetime.today().replace(microsecond=0)
	now_hour = now.strftime('%H')
	print str(now_hour)


@frappe.whitelist()
def clear_attendance():
	upload_attendance(toClear=True)#Flage toClear is to avoid twice entering of data in update_attendane function and here
	devices= get_devices()
	for device in devices:
		print device.ip
		print device.port
		if device.ip  and device.port:
			ip_address =device.ip
			port = device.port
			conn = None
			zk = ZK(ip_address, port=int(port), timeout=5, password=0, force_udp=False, ommit_ping=False)
			print ip_address
			print port
	
			try:
		    	    	conn = zk.connect()
			   	conn.disable_device()
				attendances = conn.get_attendance()
				i = 0
				for att in attendances:
					i += 1
					try:
						if (att.timestamp): 
							print ("ATT {:>6}: uid:{:>3}, user_id:{:>8} t: {}, s:{} p:{}".format(i, att.uid, att.user_id, att.timestamp, att.status, att.punch))
							if att.uid:
								send_device_data_to_database(str(att.uid),att.user_id ,att.timestamp ,att.status,att.punch)
					except Exception, e:
						print ('backaup error')
						pass
				#conn.clear_attendance()
			except Exception, e:
				return e
			finally:
				if conn:
					conn.enable_device()
					conn.disconnect()



def send_device_data_to_database(uid,user_id ,timestamp ,status,punch):
	frappe.get_doc({"doctype":"Finger Print Data",
			"uid" : uid,
			"user_id" :user_id , 
			"time":timestamp ,
			"status":status, 
			"punch":punch}).insert(ignore_permissions=True)
