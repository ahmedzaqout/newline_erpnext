# -*- coding: utf-8 -*-
import os
import sys

CWD = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(CWD)
sys.path.append(ROOT_DIR)

from zk import ZK, const
import zk
print (zk.__file__)

conn = None
zk = ZK('10.10.1.7', port=4370, verbose=True)
try:
	conn = zk.connect()
	#conn.set_user(uid=33, name='33', privilege=const.USER_DEFAULT, password='', user_id='33')
	conn.set_user(uid=60, name='NN-60', privilege=const.USER_DEFAULT, password='', user_id='60')
	conn.set_user(uid=77, name='77', privilege=const.USER_DEFAULT, password='', user_id='77')
	conn.set_user(uid=59, name='NN-59', privilege=const.USER_DEFAULT, password='', user_id='59')
	conn.set_user(uid=89, name='89', privilege=const.USER_DEFAULT, password='', user_id='89')
	conn.set_user(uid=2, name='NN-2', privilege=const.USER_DEFAULT, password='', user_id='2')
	conn.set_user(uid=153, name='153', privilege=const.USER_DEFAULT, password='', user_id='153')
	conn.set_user(uid=17, name='17', privilege=const.USER_DEFAULT, password='', user_id='17')
	conn.set_user(uid=11, name='11', privilege=const.USER_DEFAULT, password='', user_id='11')
	conn.set_user(uid=90, name='90', privilege=const.USER_DEFAULT, password='', user_id='90')
	conn.set_user(uid=50, name='50', privilege=const.USER_DEFAULT, password='', user_id='50')
	conn.set_user(uid=6, name='6', privilege=const.USER_DEFAULT, password='', user_id='6')
	conn.set_user(uid=12, name='12', privilege=const.USER_DEFAULT, password='', user_id='12')
	conn.set_user(uid=13, name='13', privilege=const.USER_DEFAULT, password='', user_id='13')
	conn.set_user(uid=47, name='47', privilege=const.USER_DEFAULT, password='', user_id='47')
	conn.set_user(uid=55, name='NN-55', privilege=const.USER_DEFAULT, password='', user_id='55')
	conn.set_user(uid=20, name='20', privilege=const.USER_DEFAULT, password='', user_id='20')
	conn.set_user(uid=147, name='NN-147', privilege=const.USER_DEFAULT, password='', user_id='147')
	conn.set_user(uid=51, name='51', privilege=const.USER_DEFAULT, password='', user_id='51')
	conn.set_user(uid=54, name='54', privilege=const.USER_DEFAULT, password='', user_id='54')
	conn.set_user(uid=104, name='NN-104', privilege=const.USER_DEFAULT, password='', user_id='104')
	conn.set_user(uid=19, name='19', privilege=const.USER_DEFAULT, password='', user_id='19')
	conn.set_user(uid=183, name='183', privilege=const.USER_DEFAULT, password='', user_id='183')
	conn.set_user(uid=14, name='NN-14', privilege=const.USER_DEFAULT, password='', user_id='14')
	conn.set_user(uid=159, name='159', privilege=const.USER_DEFAULT, password='', user_id='159')
	conn.set_user(uid=31, name='31', privilege=const.USER_DEFAULT, password='', user_id='31')
	conn.set_user(uid=56, name='56', privilege=const.USER_DEFAULT, password='', user_id='56')
	conn.set_user(uid=30, name='30', privilege=const.USER_DEFAULT, password='', user_id='30')
	conn.set_user(uid=62, name='62', privilege=const.USER_DEFAULT, password='', user_id='62')
	conn.set_user(uid=28, name='28', privilege=const.USER_DEFAULT, password='', user_id='28')
	conn.set_user(uid=87, name='87', privilege=const.USER_DEFAULT, password='', user_id='87')
	conn.set_user(uid=61, name='61', privilege=const.USER_DEFAULT, password='', user_id='61')
	conn.set_user(uid=8, name='8', privilege=const.USER_DEFAULT, password='', user_id='8')
	conn.set_user(uid=119, name='119', privilege=const.USER_DEFAULT, password='', user_id='119')
	conn.set_user(uid=66, name='66', privilege=const.USER_DEFAULT, password='', user_id='66')
	conn.set_user(uid=21, name='21', privilege=const.USER_DEFAULT, password='', user_id='21')
	conn.set_user(uid=160, name='NN-160', privilege=const.USER_DEFAULT, password='', user_id='160')
	conn.set_user(uid=196, name='196', privilege=const.USER_DEFAULT, password='', user_id='196')
	conn.set_user(uid=116, name='116', privilege=const.USER_DEFAULT, password='', user_id='116')
	conn.set_user(uid=44, name='NN-44', privilege=const.USER_DEFAULT, password='', user_id='44')
	conn.set_user(uid=45, name='45', privilege=const.USER_DEFAULT, password='', user_id='45')
	conn.set_user(uid=154, name='154', privilege=const.USER_DEFAULT, password='', user_id='154')
	conn.set_user(uid=71, name='71', privilege=const.USER_DEFAULT, password='', user_id='71')
	conn.set_user(uid=64, name='64', privilege=const.USER_DEFAULT, password='', user_id='64')
	conn.set_user(uid=88, name='NN-88', privilege=const.USER_DEFAULT, password='', user_id='88')
	conn.set_user(uid=144, name='NN-144', privilege=const.USER_DEFAULT, password='', user_id='144')
	conn.set_user(uid=105, name='105', privilege=const.USER_DEFAULT, password='', user_id='105')
	conn.set_user(uid=42, name='NN-42', privilege=const.USER_DEFAULT, password='', user_id='42')
	conn.set_user(uid=40, name='NN-40', privilege=const.USER_DEFAULT, password='', user_id='40')
	conn.set_user(uid=82, name='82', privilege=const.USER_DEFAULT, password='', user_id='82')
	conn.set_user(uid=38, name='38', privilege=const.USER_DEFAULT, password='', user_id='38')
	conn.set_user(uid=155, name='155', privilege=const.USER_DEFAULT, password='', user_id='155')
	conn.set_user(uid=145, name='145', privilege=const.USER_DEFAULT, password='', user_id='145')
	conn.set_user(uid=43, name='43', privilege=const.USER_DEFAULT, password='', user_id='43')
	conn.set_user(uid=198, name='198', privilege=const.USER_DEFAULT, password='', user_id='198')
	conn.set_user(uid=27, name='NN-27', privilege=const.USER_DEFAULT, password='', user_id='27')
	conn.set_user(uid=29, name='29', privilege=const.USER_DEFAULT, password='', user_id='29')
	conn.set_user(uid=23, name='23', privilege=const.USER_DEFAULT, password='', user_id='23')
	conn.set_user(uid=85, name='NN-85', privilege=const.USER_DEFAULT, password='', user_id='85')
	conn.set_user(uid=67, name='67', privilege=const.USER_DEFAULT, password='', user_id='67')
	conn.set_user(uid=65, name='65', privilege=const.USER_DEFAULT, password='', user_id='65')
	conn.set_user(uid=197, name='197', privilege=const.USER_DEFAULT, password='', user_id='197')
	conn.set_user(uid=167, name='NN-167', privilege=const.USER_DEFAULT, password='', user_id='167')
	conn.set_user(uid=78, name='78', privilege=const.USER_DEFAULT, password='', user_id='78')
	conn.set_user(uid=58, name='NN-58', privilege=const.USER_DEFAULT, password='', user_id='58')
	conn.set_user(uid=35, name='NN-35', privilege=const.USER_DEFAULT, password='', user_id='35')
	conn.set_user(uid=7, name='7', privilege=const.USER_DEFAULT, password='', user_id='7')
	conn.set_user(uid=33, name='33', privilege=const.USER_DEFAULT, password='', user_id='33')
	conn.set_user(uid=32, name='32', privilege=const.USER_DEFAULT, password='', user_id='32')
	conn.set_user(uid=70, name='70', privilege=const.USER_DEFAULT, password='', user_id='70')
	conn.set_user(uid=199, name='199', privilege=const.USER_DEFAULT, password='', user_id='199')
	conn.set_user(uid=200, name='200', privilege=const.USER_DEFAULT, password='', user_id='200')
	conn.set_user(uid=34, name='34', privilege=const.USER_DEFAULT, password='', user_id='34')
	conn.set_user(uid=151, name='151', privilege=const.USER_DEFAULT, password='', user_id='151')
	conn.set_user(uid=39, name='NN-39', privilege=const.USER_DEFAULT, password='', user_id='39')
	conn.set_user(uid=72, name='NN-72', privilege=const.USER_DEFAULT, password='', user_id='72')
	conn.set_user(uid=68, name='NN-68', privilege=const.USER_DEFAULT, password='', user_id='68')
	conn.set_user(uid=57, name='NN-57', privilege=const.USER_DEFAULT, password='', user_id='57')
	conn.set_user(uid=46, name='46', privilege=const.USER_DEFAULT, password='', user_id='46')
	conn.set_user(uid=63, name='63', privilege=const.USER_DEFAULT, password='', user_id='63')
	conn.set_user(uid=999, name='NN-999', privilege=const.USER_DEFAULT, password='', user_id='999')
	conn.set_user(uid=112, name='112', privilege=const.USER_DEFAULT, password='', user_id='112')
	conn.set_user(uid=109, name='109', privilege=const.USER_DEFAULT, password='', user_id='109')
	conn.set_user(uid=108, name='108', privilege=const.USER_DEFAULT, password='', user_id='108')
	conn.set_user(uid=107, name='107', privilege=const.USER_DEFAULT, password='', user_id='107')
	conn.set_user(uid=203, name='203', privilege=const.USER_DEFAULT, password='', user_id='203')
	conn.set_user(uid=99, name='NN-99', privilege=const.USER_DEFAULT, password='', user_id='99')
	conn.set_user(uid=115, name='115', privilege=const.USER_DEFAULT, password='', user_id='115')
	conn.set_user(uid=111, name='111', privilege=const.USER_DEFAULT, password='', user_id='111')
	conn.set_user(uid=106, name='106', privilege=const.USER_DEFAULT, password='', user_id='106')
	conn.set_user(uid=161, name='161', privilege=const.USER_DEFAULT, password='', user_id='161')
	conn.set_user(uid=110, name='110', privilege=const.USER_DEFAULT, password='', user_id='110')
	conn.set_user(uid=113, name='113', privilege=const.USER_DEFAULT, password='', user_id='113')
	conn.set_user(uid=157, name='NN-157', privilege=const.USER_DEFAULT, password='', user_id='157')
	conn.set_user(uid=100, name='100', privilege=const.USER_DEFAULT, password='', user_id='100')
	conn.set_user(uid=69, name='69', privilege=const.USER_DEFAULT, password='', user_id='69')
	conn.set_user(uid=156, name='NN-156', privilege=const.USER_DEFAULT, password='', user_id='156')
	conn.set_user(uid=168, name='NN-168', privilege=const.USER_DEFAULT, password='', user_id='168')
	conn.set_user(uid=163, name='163', privilege=const.USER_DEFAULT, password='', user_id='163')
	conn.set_user(uid=166, name='NN-166', privilege=const.USER_DEFAULT, password='', user_id='166')
	conn.set_user(uid=164, name='NN-164', privilege=const.USER_DEFAULT, password='', user_id='164')
	conn.set_user(uid=170, name='NN-170', privilege=const.USER_DEFAULT, password='', user_id='170')
	conn.set_user(uid=171, name='NN-171', privilege=const.USER_DEFAULT, password='', user_id='171')
	conn.set_user(uid=172, name='NN-172', privilege=const.USER_DEFAULT, password='', user_id='172')
	conn.set_user(uid=173, name='173', privilege=const.USER_DEFAULT, password='', user_id='173')
	conn.set_user(uid=174, name='NN-174', privilege=const.USER_DEFAULT, password='', user_id='174')
	conn.set_user(uid=1, name='NN-1', privilege=const.USER_DEFAULT, password='', user_id='1')
	conn.set_user(uid=175, name='NN-175', privilege=const.USER_DEFAULT, password='', user_id='175')
	conn.set_user(uid=176, name='176', privilege=const.USER_DEFAULT, password='', user_id='176')
	conn.set_user(uid=177, name='177', privilege=const.USER_DEFAULT, password='', user_id='177')
	conn.set_user(uid=178, name='178', privilege=const.USER_DEFAULT, password='', user_id='178')
	conn.set_user(uid=179, name='NN-179', privilege=const.USER_DEFAULT, password='', user_id='179')
	conn.set_user(uid=180, name='NN-180', privilege=const.USER_DEFAULT, password='', user_id='180')
	conn.set_user(uid=182, name='182', privilege=const.USER_DEFAULT, password='', user_id='182')
	conn.set_user(uid=181, name='181', privilege=const.USER_DEFAULT, password='', user_id='181')
	conn.set_user(uid=184, name='NN-184', privilege=const.USER_DEFAULT, password='', user_id='184')
	conn.set_user(uid=185, name='185', privilege=const.USER_DEFAULT, password='', user_id='185')
	conn.set_user(uid=186, name='186', privilege=const.USER_DEFAULT, password='', user_id='186')
	conn.set_user(uid=205, name='205', privilege=const.USER_DEFAULT, password='', user_id='205')
	conn.set_user(uid=189, name='NN-189', privilege=const.USER_DEFAULT, password='', user_id='189')
	conn.set_user(uid=188, name='NN-188', privilege=const.USER_DEFAULT, password='', user_id='188')
	conn.set_user(uid=190, name='NN-190', privilege=const.USER_DEFAULT, password='', user_id='190')
	conn.set_user(uid=191, name='191', privilege=const.USER_DEFAULT, password='', user_id='191')
	conn.set_user(uid=192, name='192', privilege=const.USER_DEFAULT, password='', user_id='192')
	conn.set_user(uid=193, name='193', privilege=const.USER_DEFAULT, password='', user_id='193')
	conn.set_user(uid=194, name='194', privilege=const.USER_DEFAULT, password='', user_id='194')
	conn.set_user(uid=195, name='195', privilege=const.USER_DEFAULT, password='', user_id='195')
	conn.set_user(uid=201, name='201', privilege=const.USER_DEFAULT, password='', user_id='201')
	conn.set_user(uid=204, name='204', privilege=const.USER_DEFAULT, password='', user_id='204')
	conn.set_user(uid=206, name='206', privilege=const.USER_DEFAULT, password='', user_id='206')
	print ("Process set")
except Exception as e:
    print ("Process terminate : {}".format(e))
finally:
    if conn:
        conn.disconnect()