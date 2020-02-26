// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trial Period Evaluation', {
	onload: function(frm){
	    if (frm.is_new()){
		var items=['المعرفة بالعمل','سرعة التعلم','جودة العمل','الإنتاجية','مهارات الاتصال','الثقة بالنفس','التعاون مع الموظفين','المبادرة','العمل تحت ضغط العمل','القدرة على التنظيم','الالتزام (الحضور، الاجراءات، النظام، المظهر ...)الالتزام (الحضور، الاجراءات، النظام، المظهر ...)'];
		for(var i=0; i<items.length; i++) {
		   var row = frappe.model.add_child(frm.doc, "Trial Period Evaluation Details", "trial_period_evaluation_details");
		   row.quantification = items[i];
		}
		refresh_field('trial_period_evaluation_details');
	  }
	},
	refresh: function(frm) {
		frm.fields_dict.employee.get_query = function(doc, cdt, cdn) {
			return { query: "erpnext.controllers.queries.trial_employee_query",
				 filters: {
					from_date:  frm.doc.from_date , 
					to_date	 :  frm.doc.to_date }
				}
			 }
	},
	employee:function(frm) {
		if (frm.doc.employee)
			frappe.call({
				method: "get_emp_designation",
				doc: frm.doc,
				callback: function(r) { 
					frm.set_value("designation" ,r.message.designation);
					refresh_field("designation");
				}
			});
	}
});
