// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Interview', {
	onload: function(frm) {
		const default_company = frappe.defaults.get_default('company');
		frm.set_value('company', default_company);

		if(frm.doc.job_applicant){
		frappe.call({
			method: "erpnext.hr.get_job_applicant_data",
			args:{"job_applicant":frm.doc.job_applicant},
			callback: function(r) { 
				if (r.message){
				frm.set_value("job_opening", r.message.job_title);
				frm.refresh_field('job_opening');}
				//interview_evaluationt
			}
		});
	}
		var average=0.0;
		$.each(frm.doc["interview_evaluationt"] || [], function(i, interview) {
			average += interview.average_score;
		});
		frm.set_value("average", average);
		frm.refresh_field('average');

		    if (frm.is_new()){ //plz don't write arabic alphabits!
		var technical=['ملائمة المؤهلات العلمية','خبرة متعلقة بهذا المجال','مدى الملائمة للوظيفة','التدريب','مدى المعرفة بالجمعية','مؤهلات أخرى'];
		var skills=['اللغات','مدى المعرفة بالكمبيوتر']; 
		var others=['الشخصية','المظهر','الجاهزية'];
		frm.set_value("technical", []);
		frm.set_value("skills", []);
		frm.set_value("others", []);

		for(var i=0; i<technical.length; i++) {
		   var row = frappe.model.add_child(frm.doc, "Trial Period Evaluation Details", "technical");
		   row.quantification = technical[i];
		}
		for(var i=0; i<skills.length; i++) {
		   var row = frappe.model.add_child(frm.doc, "Trial Period Evaluation Details", "skills");
		   row.quantification = skills[i];
		}
		for(var i=0; i<others.length; i++) {
		   var row = frappe.model.add_child(frm.doc, "Trial Period Evaluation Details", "others");
		   row.quantification = others[i];
		}
		frm.refresh_fields(['technical','skills','others']);
	  }



	},
	interview_evaluationt_remove: function(frm) {

	},
	job_applicant: function(frm) {
				if(frm.doc.job_applicant){

		frappe.call({
			method: "erpnext.hr.get_job_applicant_data",
			args:{"job_applicant":frm.doc.job_applicant},
			callback: function(r) {
				if (r.message){
				frm.set_value("job_opening", r.message.job_title);
				frm.refresh_field('job_opening');}
			}
		});
	}
	},
	refresh: function(frm) {
		if (!frm.doc.__islocal && frappe.user.has_role("HR Manager")) {
			if (frm.doc.__onload && frm.doc.__onload.administrative_and_financial_approval) {
				frm.add_custom_button(__("Administrative and Financial Approval"), function() {
					frappe.set_route("Form", "Administrative and Financial Approval", frm.doc.__onload.administrative_and_financial_approval);
				}, __("View"));
			} else if (!frm.doc.__islocal && frm.doc.docstatus==1){
				frm.add_custom_button(__("Administrative and Financial Approval"), function() {
					frappe.route_options = {
						"job_applicant": frm.doc.job_applicant,
						"applicant_name": frm.doc.applicant_name,
						"designation": frm.doc.job_opening,
					};
					frappe.new_doc("Administrative and Financial Approval");
					frm.set_value("is_recommended", 1);
				});
				//frm.add_custom_button(__("Add Applicants"), function() {
					
				//});
		
			}

				
		}

	},

	
});
frappe.ui.form.on('Trial Period Evaluation Details', {
	technical_remove:function(frm, dt, dn) {
		update_final_result(frm, dt, dn);
	},
	skills_remove:function(frm, dt, dn) {
		update_final_result(frm, dt, dn);
	},
	others_remove:function(frm, dt, dn) {
		update_final_result(frm, dt, dn);
	}
});

frappe.ui.form.on("Trial Period Evaluation Details", "degree", function(frm, dt, dn) { 
		update_final_result(frm, dt, dn);
});

var update_final_result = function(frm, dt, dn) {
	var final_result1 = 0;
	var total = 0 ;
	$.each(cur_frm.doc["technical"] || [], function(i, t1) {
		var av_s= parseFloat(t1.degree) || 0.0; 
			if (t1.degree){
			final_result1 += av_s;
}
		total +=1;
	});		
	var final_result2 = 0;
	$.each(cur_frm.doc["skills"] || [], function(i, t2) {
			var av_s= parseFloat(t2.degree) || 0.0; 
				if (t2.degree){
				final_result2 += av_s;
			}
				total +=1;

	});
	var final_result3 = 0;
	$.each(cur_frm.doc["others"] || [], function(i, t3) {
		var av_s= parseFloat(t3.degree) || 0.0; 
				if (t3.degree){
				final_result3 += av_s;
			}
			total +=1;

	});

	//var d = locals[cdt][cdn];
	final_result = (final_result1+ final_result2 +final_result3 ) /total; 
	cur_frm.set_value("average", final_result);
	cur_frm.set_value("total",(final_result1+ final_result2 +final_result3 ));
}




///
var interview_average = function(frm, dt, dn) {
	frm.set_value('total_working_hour', 0);
	$.each(frm.doc["timesheets"] || [], function(i, timesheet) {
		frm.doc.total_working_hour += timesheet.working_hours;
	});
	frm.refresh_field('total_working_hour');
}

var get_average_score = function(frm,dt, dn) {
	var doc = locals[dt][dn];
	var total= 0.0;var average_score= 0.0; 
	var department_member= parseFloat(doc.department_member) || 0.0; 
	var department_member2= parseFloat(doc.department_member2) || 0.0; 
	var department_member3= parseFloat(doc.department_member3) || 0.0; 
	var bureau_delegate= parseFloat(doc.bureau_delegate) || 0.0; 
	var committee_chairman= parseFloat(doc.committee_chairman) || 0.0; 
	total = department_member +department_member2 + department_member3 +bureau_delegate +committee_chairman ;
	doc.average_score= total/5 ; //5 person
	refresh_field("average_score", dn, "interview_evaluationt");
}

var calculate_total_avarage =  function(frm) {
	var doc = frm.doc;
	console.log("sds");

	totall = 0.0
	cou = 0;
	if(doc.interview_evaluationt) {
		$.each(doc.interview_evaluationt, function(index, data){
			var av_s= parseFloat(data.average_score) || 0.0; 
			if (data.average_score){
			totall += av_s;
			cou += 1;
}
				console.log(totall);

		})
	}
	av= totall / cou ;
		frm.set_value('average', av);
		refresh_field('average');
}

frappe.ui.form.on('Interview Evaluation', {
	department_member: function(frm, dt, dn) {
		var doc = locals[dt][dn]; 
		if ( parseFloat(doc.department_member) > parseFloat(doc.extreme_grade) ) {
			frappe.msgprint(__('Should not exceed extreme grade value'));
			doc.department_member = 0;
			refresh_field("department_member", dn, "interview_evaluationt");
		}
		else
		get_average_score(frm, dt, dn);
			calculate_total_avarage(frm);

	},
	department_member2: function(frm, dt, dn) {
		var doc = locals[dt][dn]; 
		if ( parseFloat(doc.department_member2) > parseFloat(doc.extreme_grade) ) {
			frappe.msgprint(__('Should not exceed extreme grade value'));
			doc.department_member2 = 0;
			refresh_field("department_member2", dn, "interview_evaluationt");
		}
		get_average_score(frm, dt, dn);
				calculate_total_avarage(frm);

	},
	department_member3: function(frm, dt, dn) {
		var doc = locals[dt][dn]; 
		if ( parseFloat(doc.department_member3) > parseFloat(doc.extreme_grade) ) {
			frappe.msgprint(__('Should not exceed extreme grade value'));
			doc.department_member3 = 0;
			refresh_field("department_member3", dn, "interview_evaluationt");
		}
		get_average_score(frm, dt, dn);
		calculate_total_avarage(frm);

	},
	bureau_delegate: function(frm, dt, dn) {
		var doc = locals[dt][dn]; 
		if ( parseFloat(doc.bureau_delegate) > parseFloat(doc.extreme_grade) ) {
			frappe.msgprint(__('Should not exceed extreme grade value'));
			doc.bureau_delegate = 0;
			refresh_field("bureau_delegate", dn, "interview_evaluationt");
		}
		get_average_score(frm, dt, dn);
				calculate_total_avarage(frm);

	},
	committee_chairman: function(frm, dt, dn) {
		var doc = locals[dt][dn]; 
		if ( parseFloat(doc.committee_chairman) > parseFloat(doc.extreme_grade) ){
			frappe.msgprint(__('Should not exceed extreme grade value'));
			doc.committee_chairman = 0;
			refresh_field("committee_chairman", dn, "interview_evaluationt");
		}
		get_average_score(frm, dt, dn);
		calculate_total_avarage(frm);
	}
	
});
