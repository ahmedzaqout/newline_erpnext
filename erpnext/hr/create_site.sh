#!/bin/bash
args=("$@")
#cd ..
error='Done............. Enjoy without errors'
mv /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/user/user.json /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/user/user.or.json
mv /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/user/user0.json /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/user/user.json



mv /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/user/user.py /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/user/user.or.py
mv /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/user/user0.py /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/user/user.py

    #create new site 
bench new-site ${args[0]} --mariadb-root-password ${args[1]} --admin-password 1 || error="bench new-site ${args[0]} --db-name ${args[0]} --mariadb-root-password ${args[1]} --admin-password ${args[12]} \n" 



    #install erpnext
bench --site ${args[0]} install-app erpnext || error="$error bench --site ${args[0]} install-app erpnext \n"

bench --site ${args[0]} install-app ${args[3]} || error="$error bench --site ${args[0]} install-app ${args[3]} \n"
 
    #install newlinetheme2 
bench --site ${args[0]} install-app ${args[4]} || error="$error bench --site ${args[0]} install-app ${args[4]} \n"



mv /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/user/user.py /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/user/user0.py
mv /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/user/user.or.py /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/user/user.py


mv /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/user/user.json /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/user/user0.json
mv /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/user/user.or.json /home/frappe/frappe-bench/apps/frappe/frappe/core/doctype/user/user.json


    #set port 
yes | bench set-nginx-port  ${args[0]} ${args[5]} || error="$error yes | bench set-nginx-port  ${args[0]} ${args[5]} \n"

    #setup nginx
yes | bench setup nginx|| error="$error yes | bench setup nginx \n"

    #reload nginx
yes | sudo service nginx reload || error="$error yes | sudo service nginx reload \n"


    #add_system_manager
#bench --site ${args[0]} add-system-manager ${args[6]} || error="$error bench --site ${args[0]} add-system-manager ${args[6]} \n"


    #limit users
#bench --site  ${args[0]} set-limit users  ${args[7]} || error="$error bench --site  ${args[0]} set-limit users  ${args[7]} \n"

    # #limit_space
#bench --site  ${args[0]} set-limit space  ${args[8]} || error="$error bench --site  ${args[0]} set-limit space  ${args[8]} \n"

    # #limit_email
#bench --site  ${args[0]} set-limit emails  ${args[9]} || error="$error bench --site  ${args[0]} set-limit emails  ${args[9]} \n"

    # #expiry
#bench --site  ${args[0]} set-limit expiry  ${args[10]} || error="$error bench --site  ${args[0]} set-limit expiry  ${args[10]} \n"



    #update_usersite_password
#bench --site ${args[0]} execute newlinetheme2.scripts.update_password --args "'${args[6]}','${args[2]}'" || error="$error bench --site ${args[0]} execute newlinetheme2.scripts.update_password --args  ${args[6]} , ${args[2]} \n"


    # #cron job every x day
#(crontab -l 2>/dev/null;  echo "0 0 */${args[11]} * * cd /home/frappe/frappe-bench/ && /usr/local/bin/bench --site ${args[0]} backup") | crontab - 
   


   #add disable_website_cache true  on site.conf
bench --site  ${args[0]}  set-config disable_website_cache True || error="$error bench --site  ${args[0]}  set-config disable_website_cache True \n"




    #setup_wizard(site, domain, company)

bench --site ${args[0]} execute newlinetheme2.newlinetheme2.setup_mywizard.complete  || error="$error bench --site ${args[0]} execute newlinetheme2.setup_mywizard.complete \n "


    #import_translation
#bench --site ${args[0]} execute erpstyle.scripts.import_translation || error="$error bench --site ${args[0]} execute #erpstyle.scripts.import_translation \n "

bench --site ${args[0]} import-csv /home/frappe/frappe-bench/apps/newlinetheme2/newlinetheme2/Translation.csv
bench --site ${args[0]} migrate

  # add *** in last errors 
error="$error \n \n  ..............................................................................................\n \n "


    #save errores to frappe system
#bench --site site1.local execute newlinetheme2.scripts.save_errores --args "'${args[0]}','$error'" 

  # save errores in file  erors_in_install_site

#echo $error >> erors_in_install_site.txt


  #save data site in subs.txt

#echo  "site name :'${args[0]}',mariadb_password :'${args[1]}',user_password :'${args[2]}',app1 :'${args[3]}',app2 :'${args[4]}',port :'${args[5]}',email :'${args[6]}',limit_user :'${args[7]}',limit_space :'${args[8]}',limit_email :'${args[9]}',expiry :'${args[10]}',limit_backup :'${args[11]}',admin_password :'${args[12]}',company :'${args[13]}' "  >> subs.txt

