# -*- coding: utf-8 -*-
import frappe
import math, json, subprocess
from frappe import _, _dict
from frappe.model.create_new import make_new_doc
from frappe.utils.data import cint
import os,sys,uuid,multiprocessing, time, socket
from subprocess import Popen
from urllib import unquote
from time import gmtime, strftime
from frappe import conf,get_site_config,get_file_json
from frappe.utils import get_site_name
from frappe.utils.data import formatdate
from frappe.utils import now_datetime, getdate, flt, cint, get_fullname,cstr,nowdate
from frappe.geo.country_info import get_country_info


reload(sys)
sys.setdefaultencoding('utf-8')


def site_url_without_port():
    return "%s"%frappe.get_site_config(frappe.local.sites_path)['site_url']

def get_mariadb_password():
    return frappe.get_site_config(frappe.local.sites_path)['maria_db']

def _generate_random(length):
    if not isinstance(length, int) or length < 8:
        raise _("temp name_site must have positive length")
    chars = "abcdefghigklmnopqrstuvwxyz0123456789"
    from os import urandom
    return "".join([chars[ord(c) % len(chars)] for c in urandom(length)])


def _get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("",0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def _update_json_file(file , old ,new):
    with open(file) as f:
        data = json.load(f)
        for i in range(len(data)):
            if data[i]['name'] == old['name']:
                data[i] = new
                with open(erpnext.file_directory, 'w') as outfile:
                    json.dump(data, outfile)
                    return "Done"
    return "Fail"

def _read_json_file(file_directory):
    with open(file_directory) as json_file:
        json_data = json.load(json_file)
        data = json_data if not None else []
    return data


# @frappe.whitelist(allow_guest=True)
def get_site_db_name(site_name):
    config={}
    site_path= '/home/frappe/frappe-bench/sites/'+site_name
    site_config=os.path.join(site_path, "site_config.json")
    config.update(get_file_json(site_config))
    frappe.local.conf= _dict(config)
    return frappe.local.conf.db_name


#@frappe.whitelist(allow_guest=True)
def setup_data_wizard(site,domain,company,country=None,langu=None,abbreviation=None):
    datafile='/home/frappe/frappe-bench/apps/erpnext/erpnext/hr/wdata/data.json'
    with open(datafile) as json_file:
        json_data = json.load(json_file)
        data = json_data if not None else []
        data['domain'] = domain
        data['company_name'] = company
        data['bank_account'] = company
        data['company_tagline'] = company
        if not abbreviation:
            abbreviation= ''.join([c[0] for c in company.split()]).upper()
        data['company_abbr'] = abbreviation.strip()
        data['country'] = country

        country_data= get_country_info(country)
        if  'currency' in country_data:
            currency= country_data.currency
            if currency:
                data['currency'] = currency
            else:
                data['currency'] = "ILS"

        if  'timezones' in country_data:
            timezones= country_data.timezones
            if timezones:
                data['timezone'] = timezones[0]
            else:
                data['timezone'] = "Asia/Jerusalem"

        with open(datafile, 'w') as outfile:
            json.dump(data, outfile, sort_keys=True,indent=4)

    return "done"

@frappe.whitelist(allow_guest=True)
def install_site(email=None,company=None,Modules=None,domain=None,country=None,langu=None,abbreviation=None):
    try:
	email='mesa_safd@hotmail.com'
        admin_password=_generate_random(10)
        user_password=_generate_random(10)
        app1="newlinetheme2"
        app2="bdtheme"
        site= 'site'+_generate_random(10)
        port = _get_open_port()
        DateAndTime=strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
    except Exception:
        error_var="An error occurred in the sent variables"
	print error_var

    # complete_setup_wizard
    #try:
     #   setup_data_wizard(site, domain, company,country,langu,abbreviation)
    #except Exception:
     #   setup_wizard="An error occurred while setup wizard"
	#print setup_wizard

    #try:
   #all operation to install
    print str(site)
    #os.system('../create_site.sh %s %s %s %s %s %s %s %s' % (str(site),str(get_mariadb_password()) , str(user_password) ,str(app1),str(app2),str(port),str(email),str(admin_password)))
    #d=subprocess.call('./create_site.sh %s %s %s %s %s %s %s %s   ' % (str(site),'erperp' , str(user_password) ,str(app1),str(app2),str(port),str(email),str(admin_password),), shell=True)
    #command = "../create_site.sh sitty  erperp maysaa newlinetheme2 bdtheme 8004"
    #process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    #output, error = process.communicate()
    d=Popen('../create_site.sh %s %s %s %s %s %s %s %s   ' % (str(site),'erperp' , str(user_password) ,str(app1),str(app2),str(port),str(email),str(admin_password),), shell=True)
    #print str(output)
    #print str(error)
    #except Exception:
     #   install_site="An error occurred in install site function"
	#print install_site

    return "Installing done for:: "+str(d)


def timetest(site_name):
    import time
    
    if check_apss(site_name):
        return True
    time.sleep(5)
    

@frappe.whitelist(allow_guest=True)
def check_apss(site):
    import commands
    app=("cd ..&&bench --site %s list-apps " % (site))
    apps=commands.getstatusoutput(app)
 
    if len(apps[1])==23:
        return True
    else:
        return False

