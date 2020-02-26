// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Workshift Schedule', {
	refresh: function(frm) {

	},
	department:function(frm) {
		console.log(frm.doc.department);
		if (frm.doc.department){
		frappe.call({
		method: "erpnext.hr.doctype.workshift_schedule.workshift_schedule.get_employees",
			args: { 
				"department":frm.doc.department
			 },
			freeze:true,
			callback: function(r)
			{
			data=r.message;
			frm.set_value("employee_shift", []);
			for(var i=0; i<data.length; i++) {
		 	  var row = frappe.model.add_child(cur_frm.doc, "Employee Shift", "employee_shift");
		   	row.employee = data[i]['employee'];	
			row.employee_name=data[i]['employee_name'];	

				}
			refresh_field("employee_shift");
	}
		});
}



	},
		
});
