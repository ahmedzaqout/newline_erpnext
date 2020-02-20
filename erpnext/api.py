# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import json
import frappe
import frappe.handler
import frappe.client
from frappe.utils.response import build_response
from frappe import _
from six.moves.urllib.parse import urlparse, urlencode
import json
from frappe.utils.password import check_password
import time
import jwt
from datetime import datetime
from frappe import _
import re
from calendar import monthrange
from frappe.utils import add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words,today,time_diff_in_hours

@frappe.whitelist(allow_guest=True)
def login(**kwards):
	data = json.loads(kwards['data'])
	if 'email' not in data or 'password' not in data:

		return  {"status":{"message": "missing credentials","success":False,"code":422}}

	if 'udid' not in data :
		return  {"status":{"message": "missing udid","success":False,"code":422}}


	email=data['email']
	password=data['password']
	udid=data['udid']
	log=frappe.get_doc({"doctype":"Api Log"})
			
			

	if not frappe.get_all("User",['name'],filters={"email":email}):
		frappe.local.response['http_status_code'] = 403	
		log.response="Incorrect credentials"
	        log.request =  "login"
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();

		return  {"status":{"message" : "Incorrect credentials","success":False,"code":403}}
		


	user_list = frappe.get_all("User",['name'],filters={"email":email})
	user_doc = frappe.get_doc("User",user_list[0].name)
	user = None
	try:
		user =check_password(user_doc.name,password)
	
	except Exception, e:
		frappe.local.response['http_status_code'] = 403
		log.response="password wrong"
		log.request =  "login"
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();


		return  {"status":{"message" : "Incorrect credentials","success":False,"code":401}}


	user_doc = frappe.get_doc("User",user)
	firstname = user_doc.first_name
	lastname  = user_doc.last_name
	email  = user_doc.email
	name = user_doc.name
	
	secret_key = "HR System";
	issuedat_claim =  time.time()
	notbefore_claim = issuedat_claim ; 
	expire_claim = issuedat_claim + (60*60*3*24); 
	token = {
	    "iat" : issuedat_claim,
	    "nbf" : notbefore_claim,
	    "exp" : expire_claim,
	    "data" : {
	        "name" : name,
	        "firstname" : firstname,
	        "lastname" : lastname,
	        "email" : email
	}};
	token=jwt.encode(token,secret_key)

        user_devices = frappe.get_all("User Device",['name'],filters={"udid":udid,"docstatus" :['<',2]})
	user_device=None
	if user_devices:
		user_device=frappe.get_doc("User Device",user_devices[0].name)
	else:
		user_device=frappe.get_doc({"doctype":"User Device"})

	user_device.user=user
	user_device.udid = udid;
        user_device.access_token = token
        user_device.enabled = 1

        user_device.flags.ignore_permissions=True
	user_device.save()
	dettt ={"access_token" :token,
		"name" : name,
	        "firstname" : firstname,
	        "lastname" : lastname,
	        "email" : email}
	
	emp = frappe.get_doc("Employee",user_doc.employee)
	if frappe.get_all("Employee Personal Detail",['name'],filters={"employee":emp.name}):
		de = frappe.get_all("Employee Personal Detail",['name'],filters={"employee":emp.name})
		dettt = frappe.get_doc("Employee Personal Detail" , de[0].name)
		dettt = frappe.get_all("Employee Personal Detail" ,["creation", "identity_no","ar_tname","user_id",    "employee_number","en_family_name","ar_sname","religion", "date_of_birth","en_fname","nationality","employee_name","ar_family_name", "en_sname","marital_status","place_of_birth","ar_fname","en_tname","gender","current_address","phone_number","facebook_account","twitter_account"], filters={"name":de[0].name})[0]

	dettt['access_token']=token
	leaves_typ=[]
	leaves_types = frappe.get_all("Leave Type",['name'])
	for le in  leaves_types:
		leaves_typ.append({"id":le.name, "name" :le.name})
	
	exit_types=[{"name": "Special","id":"Special"},{"name": "Work","id":"Work"},{"name": "Sick","id":"Sick"}]

     
        ret_user ={"access_token" :token,
		"name" : name,
	        "firstname" : firstname,
	        "lastname" : lastname,
	        "email" : email}

        msg = "تم تسجيل الدخول بنجاح"
	log.response=msg
	log.token =token
	log.user= user
	log.request =  "login"

	log.flags.ignore_permissions=True
	log.insert()
	frappe.db.commit();


        return  {"status":{"message": msg,
			"code":1,
			"success":True},
		"user" : dettt,
		"leave_types" : leaves_typ,
		"exit_types":exit_types}
             
	
	
	
	
@frappe.whitelist(allow_guest=True)
def check_token():
	request = frappe.request
	secret_key = "HR System";
	frappe.local.lang="ar"
	frappe.cache().hset("lang", "Guest", "ar")
	

	if  frappe.get_request_header("Authorization"):
		
		authorization_header = frappe.get_request_header("Authorization").split(" ")
		if authorization_header[0] != "Bearer" and len(authorization_header)!=2 :
			return {"message": "Invalid Token"}

	        token = frappe.get_request_header("Authorization").replace('Bearer ', '');


                userDevices = frappe.get_all("User Device",['name'],filters={"access_token": token,"docstatus" :['<',2]})
		if not userDevices:
			frappe.local.response['http_status_code'] = 403
			return {"message": "Not Permitted"}

		try:
			token=jwt.decode(token,secret_key)
		except Exception, e:
			frappe.local.response['http_status_code'] = 401
			return  {"message" : "Expired Token"}


		
		userdevice=frappe.get_doc("User Device",userDevices[0].name)
		if not userdevice.user:
			frappe.local.response['http_status_code'] = 403
			return {"message": "Not Permitted"}
		user=frappe.get_doc("User",userdevice.user)		


		return {"success":user}
	       
	else:
		frappe.local.response['http_status_code'] = 403
		return {"message": "Not Permitted"}

@frappe.whitelist(allow_guest=True)
def logout(**kwards):
	request = frappe.request
	secret_key = "HR System";
	if  frappe.get_request_header("Authorization"):
		
		authorization_header = frappe.get_request_header("Authorization").split(" ")
		if authorization_header[0] != "Bearer" and len(authorization_header)!=2 :
			return  {"status":{"message": "Invalid Token","success":False,"code":15}}

	        token = frappe.get_request_header("Authorization").replace('Bearer ', '');


                userDevices = frappe.get_all("User Device",['name'],filters={"access_token": token,"docstatus" :['<',2]})
		if not userDevices:
			frappe.local.response['http_status_code'] = 403
			return  {"status":{"message": "Not Permitted","success":False,"code":15}}

		try:
			token=jwt.decode(token,secret_key)
		except Exception, e:
			frappe.local.response['http_status_code'] = 401
			return  {"status":{"message" : "Expired Token","success":False,"code":15}}


		
		user_device=frappe.get_doc("User Device",userDevices[0].name)
		
		frappe.db.sql("""update `tabUser Device` set docstatus=2 where name = '{0}' """.format(user_device.name))
		frappe.db.commit();

		msg = "تم تسجيل الخروج بنجاح"

		return {"status":{"message": msg,
				"success":True,
				"code":15}}



@frappe.whitelist(allow_guest=True)
def notification(**kwards):
	user=None
	token=""
	if  frappe.get_request_header("Authorization"):
		token = frappe.get_request_header("Authorization").replace('Bearer ', '')

	res = check_token()
	log=frappe.get_doc({"doctype":"Api Log"})
	log.token = token
	log.request =  "notification"
	
		
	if 'success' in res:
		user =res['success']
		log.response="success login"
		log.user= user.name
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
	elif 'message' in res:
		log.response=res['message']
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :res['message'],"success" :False,"code":403}}
	else:
		log.response="error"
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :"error","success" :False,"code":401}}

	if not user:
		frappe.local.response['http_status_code'] = 403
		return  {"status":{"message": "Not Permitted","success" :False,"code":401}}


	notifications = frappe.get_all("Notification",['name','tilte','message','seen','doctype_type','doctype_name','creation'],filters={"reciver":user.name},limit_page_length=30)
		
			 
            
	return {"status":{"success":True,"code":1,"message":"returned notifications"},"notifications":notifications}


@frappe.whitelist(allow_guest=True)
def attendance(**kwards):
	user=None
	token=""
	if  frappe.get_request_header("Authorization"):
		token = frappe.get_request_header("Authorization").replace('Bearer ', '')

	res = check_token()
	log=frappe.get_doc({"doctype":"Api Log"})
	log.token = token
	log.request =  "attendance"
	
		
	if 'success' in res:
		user =res['success']
		log.response="success login"
		log.user= user.name
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
	elif 'message' in res:
		log.response=res['message']
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :res['message'],"success" :False,"code":403}}
	else:
		log.response="error"
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :"error","success" :False,"code":401}}


	if not user:
		frappe.local.response['http_status_code'] = 403
		return  {"status":{"message": "Not Permitted","success" :False,"code":401}}
	currentDT = datetime.now()
	emp = frappe.get_doc("Employee",user.employee)

	att=frappe.get_doc({"doctype":"Attendance",
			"employee" : user.employee,
			"attendance_date" : currentDT.strftime("%Y-%m-%d"),
			"status" : "Present",
			"attendance_time" :  currentDT.strftime("%H:%M:%S"),
			"owner" : "Administrator",
			"idx" : 5})
	try:
		att.flags.ignore_permissions=True
		att.insert()
		frappe.db.commit();
	except Exception, e:
		e=str(e)
		e=e.decode('utf-8')
		e== e.replace("ValidationError('", '')
		e== e.replace("',)", '')
		frappe.local.response['http_status_code'] = 401
		return   {"status":{"message":_(e),
			"success":False,
			"code" :401}}


	return  {"status":{"success":True,"code":1,"message":"تم تسجيل حضورك بنجاح"},"attendance":[att]}

@frappe.whitelist(allow_guest=True)
def departure(**kwards):
	user=None
	token=""
	if  frappe.get_request_header("Authorization"):
		token = frappe.get_request_header("Authorization").replace('Bearer ', '')

	res = check_token()
	log=frappe.get_doc({"doctype":"Api Log"})
	log.token = token
	log.request =  "departure"
	
		
	if 'success' in res:
		user =res['success']
		log.response="success login"
		log.user= user.name
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
	elif 'message' in res:
		log.response=res['message']
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :res['message'],"success" :False,"code":403}}
	else:
		log.response="error"
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :"error","success" :False,"code":401}}


	if not user:
		frappe.local.response['http_status_code'] = 403
		return  {"status":{"message": "Not Permitted","success" :False,"code":401}}
	currentDT = datetime.now()
	emp = frappe.get_doc("Employee",user.employee)

	att=frappe.get_doc({"doctype":"Departure",
			"employee" : user.employee,
			"departure_date" : currentDT.strftime("%Y-%m-%d"),
			"status" : "Present",
			"departure_time" :  currentDT.strftime("%H:%M:%S"),
			"owner" : "Administrator"})
	try:
		att.flags.ignore_permissions=True
		att.insert()
		frappe.db.commit();
	except Exception, e:
		e=str(e)
		e=e.decode('utf-8')
		e== e.replace("ValidationError('", '')
		e== e.replace("',)", '')
		frappe.local.response['http_status_code'] = 401
		return   {"status":{"message":_(e),
			"success":False,
			"code" :401}}


	return  {"status":{"success":True,"code":1,"message":"تم تسجيل الانصراف بنجاح"},"departure":[att]}


@frappe.whitelist(allow_guest=True)
def exit(**kwards):
	user=None
	token=""
	if  frappe.get_request_header("Authorization"):
		token = frappe.get_request_header("Authorization").replace('Bearer ', '')

	res = check_token()
	log=frappe.get_doc({"doctype":"Api Log"})
	log.token = token
	log.request =  "exit"
	
		
	if 'success' in res:
		user =res['success']
		log.response="success login"
		log.user= user.name
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
	elif 'message' in res:
		log.response=res['message']
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :res['message'],"success" :False,"code":403}}
	else:
		log.response="error"
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :"error","success" :False,"code":401}}


	if not user:
		frappe.local.response['http_status_code'] = 403
		return  {"status":{"message": "Not Permitted","success" :False,"code":401}}
	currentDT = datetime.now()
	data = json.loads(kwards['data'])
	if 'exit_type' not in data:
		return  {"status":{"message": "missing exit type","success":False,"code":422}}
	

	exit_type = data['exit_type']
	emp = frappe.get_doc("Employee",user.employee)
	att=frappe.get_doc({"doctype":"Exit permission",
			"employee" : user.employee,
			"permission_date" : currentDT.strftime("%Y-%m-%d"),
			"type" : "Exit",
			"permission_type_nawa": exit_type,
			"permission_type" : "Exit with return" , 
			"from_date" :  currentDT.strftime("%H:%M:%S"),
			"owner" : "Administrator"})
	try:
		att.flags.ignore_permissions=True
		att.insert()
		frappe.db.commit();
	except Exception, e:
		e=str(e)
		e=e.decode('utf-8')
		e== e.replace("ValidationError('", '')
		e== e.replace("',)", '')
		frappe.local.response['http_status_code'] = 401
		return   {"status":{"message":_(e),
			"success":False,
			"code" :401}}

	return  {"status":{"success":True,"code":1,"message":"تم تسجيل المغادرة بنجاح"},"exit":[att]}

@frappe.whitelist(allow_guest=True)
def return_from_exit(**kwards):
	user=None
	token=""
	if  frappe.get_request_header("Authorization"):
		token = frappe.get_request_header("Authorization").replace('Bearer ', '')

	res = check_token()
	log=frappe.get_doc({"doctype":"Api Log"})
	log.token = token
	log.request =  "return"
	
		
	if 'success' in res:
		user =res['success']
		log.response="success login"
		log.user= user.name
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
	elif 'message' in res:
		log.response=res['message']
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :res['message'],"success" :False,"code":403}}
	else:
		log.response="error"
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :"error","success" :False,"code":401}}


	if not user:
		frappe.local.response['http_status_code'] = 403
		return  {"status":{"message": "Not Permitted","success" :False,"code":401}}
	currentDT = datetime.now()
	emp = frappe.get_doc("Employee",user.employee)

	att=frappe.get_doc({"doctype":"Exit permission",
			"employee" : user.employee,
			"permission_date" : currentDT.strftime("%Y-%m-%d"),
			"permission_type" : "Exit with return" , 
			"type" : "Return",
			"to_date" :  currentDT.strftime("%H:%M:%S"),
			"owner" : "Administrator"})
	try:
		att.flags.ignore_permissions=True
		att.insert()
		frappe.db.commit();
	except Exception, e:
		e=str(e)
		e=e.decode('utf-8')
		e== e.replace("ValidationError('", '')
		e== e.replace("',)", '')
		frappe.local.response['http_status_code'] = 401
		return   {"status":{"message":_(e),
			"success":False,
			"code" :401}}


	return  {"status":{"success":True,"code":1,"message":"تمت العودة بنجاح"},"departure":[att]}

	
@frappe.whitelist(allow_guest=True)
def leave_application(**kwards):
	user=None
	token=""
	if  frappe.get_request_header("Authorization"):
		token = frappe.get_request_header("Authorization").replace('Bearer ', '')

	res = check_token()
	log=frappe.get_doc({"doctype":"Api Log"})
	log.token = token
	log.request =  "leave_application"
	
		
	if 'success' in res:
		user =res['success']
		log.response="success login"
		log.user= user.name
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
	elif 'message' in res:
		log.response=res['message']
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :res['message'],"success" :False,"code":403}}
	else:
		log.response="error"
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :"error","success" :False,"code":401}}

	

	data = json.loads(kwards['data'])
	if 'from_date' not in data:
		return  {"status":{"message": "missing From Date","success":False,"code":422}}
	if 'to_date' not in data:
		return  {"status":{"message": "missing To Date","success":False,"code":422}}
	if 'leave_type' not in data:
		return  {"status":{"message": "missing Leave Type","success":False,"code":422}}

	from_date= data['from_date']
	from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
	to_date= data['to_date']
	to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
	leave_type= data['leave_type']
	reson= data['reson']


	currentDT = datetime.now()
	emp = frappe.get_doc("Employee",user.employee)

	leave=frappe.get_doc({"doctype":"Leave Application",
			"employee" : user.employee,
			"from_date" : from_date,
			"to_date" : to_date,
			"leave_type" : leave_type,
			"description" :  reson,
			"workflow_state" :"Pending Request",
			"owner" : "Administrator"})
	try:
		leave.flags.ignore_permissions=True
		leave.insert()
		frappe.db.commit();
	except Exception, e:
		e = str(e)
		e=e.decode('utf-8')
		frappe.local.response['http_status_code'] = 401
		cleanr = re.compile('<.*?>')
		e = re.sub(cleanr, '', e)
		return {"status":{"message":e,
				"success":False,
				"code":422}
			}

	return  {"status":{"success":True,"code":1,"message":"تم تقديم الإجازة بنجاح"},"leave":[leave]}


@frappe.whitelist(allow_guest=True)
def me(**kwards):
	user=None
	token=""
	if  frappe.get_request_header("Authorization"):
		token = frappe.get_request_header("Authorization").replace('Bearer ', '')

	res = check_token()
	log=frappe.get_doc({"doctype":"Api Log"})
	log.token = token
	log.request =  "me"
	
		
	if 'success' in res:
		user =res['success']
		log.response="success login"
		log.user= user.name
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
	elif 'message' in res:
		log.response=res['message']
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :res['message'],"success" :False,"code":403}}
	else:
		log.response="error"
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :"error","success" :False,"code":401}}


	if not user:
		frappe.local.response['http_status_code'] = 403
		return  {"status":{"message": "Not Permitted","success" :False,"code":401}}

	emp = frappe.get_doc("Employee",user.employee)
	if frappe.get_all("Employee Personal Detail",['name'],filters={"employee":emp.name}):
		de = frappe.get_all("Employee Personal Detail",['name'],filters={"employee":emp.name})
		dettt = frappe.get_doc("Employee Personal Detail" , de[0].name)
		dettt = frappe.get_all("Employee Personal Detail" ,["creation", "identity_no","ar_tname","user_id",    "employee_number","en_family_name","ar_sname","religion", "date_of_birth","en_fname","nationality","employee_name","ar_family_name", "en_sname","marital_status","place_of_birth","ar_fname","en_tname","gender","current_address","phone_number","facebook_account","twitter_account"], filters={"name":de[0].name})[0]
			 
            
		return {"status":{"success":True,"code":1,"message":"user details"},"user":dettt}

	return {"status":{"success":False,"code":401}}
@frappe.whitelist(allow_guest=True)
def edit_attendance(**kwards):
	user=None
	token=""
	if  frappe.get_request_header("Authorization"):
		token = frappe.get_request_header("Authorization").replace('Bearer ', '')

	res = check_token()
	log=frappe.get_doc({"doctype":"Api Log"})
	log.token = token
	log.request =  "edit_attendance"
	
		
	if 'success' in res:
		user =res['success']
		log.response="success login"
		log.user= user.name
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
	elif 'message' in res:
		log.response=res['message']
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :res['message'],"success" :False,"code":403}}
	else:
		log.response="error"
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :"error","success" :False,"code":401}}


	if not user:
		frappe.local.response['http_status_code'] = 403
		return  {"status":{"message": "Not Permitted","success" :False,"code":403}}
	
	data= kwards
	data = json.loads(kwards['data'])
	if 'date' not in data:
		return  {"status":{"message": "missing From Date","success":False,"code":422}}
	if 'attendance_time' not in data:
		return  {"status":{"message": "missing To Date","success":False,"code":422}}
	if 'departure_time' not in data:
		return  {"status":{"message": "missing Leave Type","success":False,"code":422}}

	date= data['date']
	#date = datetime.strptime(date, '%Y-%m-%d').date()
	attendance_time= data['attendance_time']
	#attendance_time = datetime.strptime(attendance_time, '%H:%M:%S').date()
	departure_time= data['departure_time']
	#departure_time = datetime.strptime(departure_time, '%H:%M:%S').date()
	note= data['note']


	currentDT = datetime.now()
	emp = frappe.get_doc("Employee",user.employee)

	leave=frappe.get_doc({"doctype":"Employee Edit Time",
			"employee" : user.employee,
			"attendance_date" : date,
			"attendance_time" : attendance_time,
			"departure_time" : departure_time,
			"note" :  note,
			"workflow_state" :"Pending Request",
			"owner" : "Administrator"})
	try:
		leave.flags.ignore_permissions=True
		leave.insert()
		frappe.db.commit();
	except Exception, e:
		e=str(e)
		e=e.decode('utf-8')
		e== e.replace("ValidationError('", '')
		e== e.replace("',)", '')
		frappe.local.response['http_status_code'] = 401
		return   {"status":{"message":_(e),
			"success":False,
			"code" :401}}
	
	return  {"status":{"success":True,"code":1,"message":"تم تقديم طلب تعديل الدوام بنجاح"},"leave":[leave]}



@frappe.whitelist(allow_guest=True)
def leaves(**kwards):
	user=None
	token=""
	if  frappe.get_request_header("Authorization"):
		token = frappe.get_request_header("Authorization").replace('Bearer ', '')

	res = check_token()
	log=frappe.get_doc({"doctype":"Api Log"})
	log.token = token
	log.request =  "leaves"
	
		
	if 'success' in res:
		user =res['success']
		log.response="success login"
		log.user= user.name
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
	elif 'message' in res:
		log.response=res['message']
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :res['message'],"success" :False,"code":403}}
	else:
		log.response="error"
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :"error","success" :False,"code":401}}


	if not user:
		frappe.local.response['http_status_code'] = 403
		return  {"status":{"message": "Not Permitted","success" :False,"code":401}}

	data= kwards
	data = json.loads(kwards['data'])
	if 'month' not in data:
		return  {"status":{"message": "missing Month","success":False,"code":422}}
	
	if 'year' not in data:
		return  {"status":{"message": "missing Year","success":False,"code":422}}
	month=0
	year=0

	try:
		month=int(data['month'])
	except Exception, e: 
		return  {"status":{"message": "Month must be number","success":False,"code":422}}	
	try:
		year=int(data['year'])
	except Exception, e:
		return  {"status":{"message": "Year must be number","success":False,"code":422}}	
	
	start_date=datetime.today()
	end_date=datetime.today()
	delta = cint(monthrange( cint(year), cint(month) )[1])
	try:
		start_date = datetime.strptime(str(year)+"-"+str(month)+"-1" , '%Y-%m-%d')
	except Exception, e:
		return  {"status":{"message": "Unknown year and month format","success":False,"code":422}}
	try:
		end_date = datetime.strptime(str(year)+"-"+str(month)+"-"+str(delta) , '%Y-%m-%d')
	except Exception, e:
		return  {"status":{"message": "Unknown year and month format","success":False,"code":422}}



			

	emp = frappe.get_doc("Employee",user.employee)
	leaves = frappe.db.sql("""select from_date,to_date , leave_type,workflow_state  from `tabLeave Application` where docstatus = 1 and employee = '{0}' and ((from_date between '{1}' and '{2}') or (to_date between '{1}' and '{2}')) order by from_date desc""".format(emp.name,start_date,end_date),as_dict=1)
		
			 
            
	return {"status":{"success":True,"code":1,"message":"returned Leaves"},"leaves":leaves}

@frappe.whitelist(allow_guest=True)
def exit_permissions(**kwards):
	user=None
	token=""
	if  frappe.get_request_header("Authorization"):
		token = frappe.get_request_header("Authorization").replace('Bearer ', '')

	res = check_token()
	log=frappe.get_doc({"doctype":"Api Log"})
	log.token = token
	log.request =  "exit_permissions"
	
		
	if 'success' in res:
		user =res['success']
		log.response="success login"
		log.user= user.name
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
	elif 'message' in res:
		log.response=res['message']
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :res['message'],"success" :False,"code":403}}
	else:
		log.response="error"
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :"error","success" :False,"code":401}}


	if not user:
		frappe.local.response['http_status_code'] = 403
		return  {"status":{"message": "Not Permitted","success" :False,"code":401}}

	data = json.loads(kwards['data'])
	if 'month' not in data:
		return  {"status":{"message": "missing Month","success":False,"code":422}}
	
	if 'year' not in data:
		return  {"status":{"message": "missing Year","success":False,"code":422}}
	month=0
	year=0

	try:
		month=int(data['month'])
	except Exception, e:
		return  {"status":{"message": "Month must be number","success":False,"code":422}}	
	try:
		year=int(data['year'])
	except Exception, e: 
		return  {"status":{"message": "Year must be number","success":False,"code":422}}	

	start_date=datetime.today()
	end_date=datetime.today()
	delta = cint(monthrange( cint(year), cint(month) )[1])
	try:
		start_date = datetime.strptime(str(year)+"-"+str(month)+"-1" , '%Y-%m-%d')
	except Exception, e:
		return  {"status":{"message": "Unknown year and month format","success":False,"code":422}}
	try:
		end_date = datetime.strptime(str(year)+"-"+str(month)+"-"+str(delta) , '%Y-%m-%d')
	except Exception, e:
		return  {"status":{"message": "Unknown year and month format","success":False,"code":422}}



	emp = frappe.get_doc("Employee",user.employee)
	exits  = frappe.db.sql("""select r.employee, r.permission_date,e.from_date, e.permission_type_nawa as permission_type ,r.to_date,TIME_TO_SEC(r.diff_exit)/3600 as diff  from `tabExit permission` as e join `tabExit permission` as r on e.permission_date=r.permission_date and e.employee=r.employee and e.type='Exit' and  r.type='Return' and e.permission_type='Exit with return' and r.permission_type='Exit with return' where r.docstatus = 1 and e.docstatus = 1 and r.employee = '{0}' and r.permission_date between '{1}' and '{2}' order by r.permission_date desc""".format(emp.name,start_date,end_date),as_dict=1)
		
			 
            
	return {"status":{"success":True,"code":1,"message":"returned exits"},"exits":exits}



@frappe.whitelist(allow_guest=True)
def attendance_sheet(**kwards):
	from datetime import date, timedelta
	user=None
	token=""
	if  frappe.get_request_header("Authorization"):
		token = frappe.get_request_header("Authorization").replace('Bearer ', '')

	res = check_token()
	log=frappe.get_doc({"doctype":"Api Log"})
	log.token = token
	log.request =  "attendance_sheet"
	
		
	if 'success' in res:
		user =res['success']
		log.response="success login"
		log.user= user.name
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
	elif 'message' in res:
		log.response=res['message']
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :res['message'],"success" :False,"code":403}}
	else:
		log.response="error"
		log.flags.ignore_permissions=True
		log.insert()
		frappe.db.commit();
		return {"status":{"message" :"error","success" :False,"code":401}}


	if not user:
		frappe.local.response['http_status_code'] = 403
		return  {"status":{"message": "Not Permitted","success" :False,"code":401}}

	data = json.loads(kwards['data'])
	if 'month' not in data:
		return  {"status":{"message": "missing Month","success":False,"code":422}}
	
	if 'year' not in data:
		return  {"status":{"message": "missing Year","success":False,"code":422}}
	month=0
	year=0

	try:
		month=int(data['month'])
	except Exception, e:
		return  {"status":{"message": "Month must be number","success":False,"code":422}}	
	try:
		year=int(data['year'])
	except Exception, e:
		return  {"status":{"message": "Year must be number","success":False,"code":422}}	

	start_date=datetime.today()

	try:
		start_date = datetime.strptime(str(year)+"-"+str(month)+"-1" , '%Y-%m-%d')
	except Exception, e:
		return  {"status":{"message": "Unknown year and month format","success":False,"code":422}}	
	
	
	delta = cint(monthrange( cint(year), cint(month) )[1])
	emp = frappe.get_doc("Employee",user.employee)
	result=[]
	for i in range(delta ):
    		day = start_date + timedelta(days=i)
		attendance_sheet  = frappe.db.sql("""select distinct att.attendance_date , DAYNAME(att.attendance_date) as day,att.attendance_time, dept.departure_time,GREATEST(round(TIMESTAMPDIFF(MINUTE,att.attendance_time,dept.departure_time)/60,2),0) as total_hours,att.status from  tabAttendance as att  left join  tabDeparture as dept on dept.employee=att.employee and att.attendance_date=dept.departure_date where  dept.docstatus = 1 and att.docstatus=1 and att.employee= '{0}' and att.attendance_date='{1}' order by att.attendance_date desc""".format(emp.name,getdate(day)),as_dict=1)
		if attendance_sheet:
			result.append(attendance_sheet[0])
		else:
			result.append({"attendance_date":day.strftime("%Y-%m-%d"),"day": _(day.strftime("%A")), "attendance_time":"", "departure_time":"" ,"total_hours":0,"status":"Absent"})
		
			 
	return {"status":{"success":True,"code":1,"message":"returned attendance sheet"},"attendance_sheet":result}





