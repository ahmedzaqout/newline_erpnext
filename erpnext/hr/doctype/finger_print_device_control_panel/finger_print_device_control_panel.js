// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Finger Print Device Control Panel', {
		set_indicator: function (frm) {
		
		// navigator.onLine
		connection_status = false;
		frm.page.set_indicator(__("Offline"), "grey")
		frappe.call({
			method: "erpnext.hr.doctype.finger_print_device_control_panel.finger_print_device_control_panel.test_connection",
			args: {
				ip_address: frm.doc.ip_address,
				port:frm.doc.port},
			callback: function (r) {
				if (r.message.conn) {
					me.connection_status = true;
					frm.page.set_indicator(__("Online"), "green")
				}
			}
		})
	},
	refresh: function(frm) {
		frm.trigger('set_indicator');

		frm.add_custom_button(__('Test Connection'),
				function () { 
					if (frm.doc.connected==1)
						return frappe.show_alert(__('Already Connected'))
					return cur_frm.call({
						method: "erpnext.hr.doctype.finger_print_device_control_panel.finger_print_device_control_panel.test_connection",
						args: {
							ip_address: frm.doc.ip_address,
							port:frm.doc.port},
						callback: function(r) {
							if (r.message.conn){
								frappe.msgprint(__('Success Connection'))
							}else {
								frappe.msgprint(__('Can not connected!'))
							}
						  }
					});
				}
		);
		//frm.add_custom_button(__('Disconnect Connection'),
				//function () { 
				//	return cur_frm.call({
				//		method: "disconnect_connection",
				//		args: {
				//			ip_address: frm.doc.ip_address,
				//			port:frm.doc.port},
				//		callback: function(r) {
				//			if (r.message){
				//				frappe.show_alert(__('Success Disconnection'))
				//			}else {
				//				frappe.msgprint(__('Can not connected!'))
				//			}
				//		  }
				//	});
				//}
		//);


		frm.add_custom_button(__('Update Attendances'),
				function () {
					frappe.prompt([
   						 {'fieldname': 'month', 'fieldtype': 'Select', 'label': 'Month', 'reqd': 1,"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec", "default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov","Dec"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()]}  
						],
					function(values){// console.log(values);
						frappe.msgprint(__('Waiting...'))
						return cur_frm.call({
						method: "upload_attendance",
						args:{'month':values.month},
						callback: function(r) {
							if (r.message){
							if (r.message.success >= 0){
								frappe.msgprint(__('Successfully Stored '+r.message.success+' Attendance Records on db'))
							}
							}else {
								frappe.msgprint(__('Can not connected!'))
							}
						  }
					});
					},	'Update Attendance','Update')


				}
		);



		//frm.add_custom_button(__('Start Recording'),
		//		function () {
		//			return ""
		//			if (frm.doc.connected==1)
		//				return frappe.show_alert(__('Already Connected'))
		//			return cur_frm.call({
		//				method: "zk_exec",
		//				callback: function(r) { conosle.log(r)
		//					frappe.show_alert(__('Started..'))
		//					if (r.message === 'success'){
		//						frappe.show_alert(__('Started..'))
		//					}else {
		//						frappe.msgprint(__('Can not connected!'))
		//					}
		//				  }
		//			});
		//		}
		//);


		frm.add_custom_button(__('Backup'),
				function () {
					//return cur_frm.call({
					//	method: "backup_attendance",
					//	callback: function(r) {
					//		if (r.message === 'success'){
					//			frappe.show_alert(__('Successfully Backuped'))
					//		}else {
					//			frappe.msgprint(__('Can not connected!'))
					//		}
					//	  }
					//});
				}
		);





	}

});
