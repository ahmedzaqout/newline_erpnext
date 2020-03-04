# -*- coding: utf-8 -*-
import sys
#sys.path.append("zk")
print(sys.path)
from zk import ZK, const

conn = None
zk = ZK('10.10.1.7', port=4370, timeout=15, password=0, force_udp=False, ommit_ping=False,verbose=True)
try:
    print(zk)
    print ('Connecting to device ...')
    conn = zk.connect()
    print ('Disabling device ...')
    #conn.disable_device()
    conn.enable_device()
    print ('Firmware Version: : {}'.format(conn.get_firmware_version()))
    print '--- Get User ---'
    attendance = conn.get_attendance()    
    #print(len(attendance))
    print '--- END len ---'
    for user in attendance:
        #print ('----------------------')
        #print ('- UID: #{} timestamp:'.format(user.uid))
        #print ('  punch       : {}'.format(user.punch))
        #print ('  uid  : {}'.format(user.uid))
        #print ('  timestamp   : {}'.format(user.timestamp))
        #print ('  status   : {}'.format(user.status))
        #print ('  user_id: {} timestamp: {} status:{}'.format(user.user_id,user.timestamp,user.punch))
        uid, status, punch, timestamp = unpack('<HBB4s', attendance.ljust(8, b'\x00')[:8])
        print(uid)


    #print ("Voice Test ...")
  #  conn.test_voice()
    print ('Enabling device ...')
    conn.enable_device()
except Exception as e:
    print ("Process terminate : {}".format(e))

