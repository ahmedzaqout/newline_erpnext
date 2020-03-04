// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Shift', {
	onload: function(frm) {
	     frm.set_value("employee","");
		(frm.doc.work_shift_details)
			frm.events.count_day(frm);

	
	   if(frm.is_new()){
	 	var day_list = ["Saturday","Sunday","Monday","Tuesday","Wednesday","Thursday","Friday"]
		for(var i=0; i<day_list.length; i++) {
		   var row = frappe.model.add_child(cur_frm.doc, "Work Shift Details", "work_shift_details");
		   row.day = day_list[i];
		   refresh_field("work_shift_details");
		}

	}
	
	//if (frm.work_shift != null) console.log(frm.work_shift);
	   if(!frm.is_new())
	 	frappe.call({
			method: "erpnext.hr.employee_shift",
			args: { "work_shift": frm.doc.work_shift },
			callback: function(r)
			{
			     frm.set_value("employee_numbers",r.message);
		  	     refresh_field("employee_numbers");
			}
		});

   },
     validate:function(frm){
	frm.events.count_day(frm);
	},

      all_day:function(frm){
	  if (frm.doc.all_day=='1'){
		    var length = frm.fields_dict['work_shift_details'].grid.grid_rows.length;
		    var start_work = frm.fields_dict['work_shift_details'].grid.grid_rows[0].doc.start_work;
			//if(start_work >='08:00:0')
			  for(var i=1; i<frm.fields_dict['work_shift_details'].grid.grid_rows.length; i++) {
				frm.fields_dict['work_shift_details'].grid.grid_rows[i].doc.start_work.set_value = (start_work);
				refresh_field(frm.fields_dict['work_shift_details'].grid.grid_rows[i].doc.start_work);
		}
	      }
	},
  
	work_shift:function(frm){	
		if (frm.doc.work_shift)
			frappe.call({
			method: "erpnext.hr.utils.validate_only_arabic",
			args: { "ar_field": frm.doc.work_shift }
			});

	},
	work_shift_en:function(frm){	
		if (frm.doc.work_shift_en)
			frappe.call({
			method: "erpnext.hr.utils.validate_only_english",
			args: { "en_field": frm.doc.work_shift_en }
			});
	},

	count_day: function(frm) {
		var total_hours= 0;	
		$.each(frm.doc["work_shift_details"] || [], function(i, work_shift) {
			frappe.call({
			method: "erpnext.assets.doctype.asset_repair.asset_repair.get_downtime",
			args: { 
				"failure_date":work_shift.start_work,
				"completion_date":work_shift.end_work },
			callback: function(r){
				total_hours += r.message;
				frm.set_value("total_hours",total_hours);
				frm.refresh_field('total_hours');
			}
		});

		});	
	},
	get_time:function(start_work,end_work){
		return frappe.call({
			method: "erpnext.assets.doctype.asset_repair.asset_repair.get_downtime",
			args: { 
				"failure_date":start_work,
				"completion_date":end_work },
			callback: function(r)
			{
			}
		});
	}

});

frappe.ui.form.on('Work Shift Details', {
	onload: function(frm) {
		//frm.events.get_time(frm)	
		
	},
	start_work:function(frm){
		//frm.events.get_time(frm)	
	},
	end_work:function(frm){
		//frm.events.get_time(frm)	
	}
});

function timeToSeconds(time) {
    time = time.split(/:/);
    return time[0] * 3600 + time[1] * 60 + time[2];
}

function toTime(timeString){
    var timeTokens = timeString.split(':');
    return new Date(1970,0,1, timeTokens[0], timeTokens[1], timeTokens[2]);
}
