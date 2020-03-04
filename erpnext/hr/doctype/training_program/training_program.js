// Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Training Program', {
	refresh: function(frm) {
		frm.fields_dict['training_targate'].grid.get_field('employee').get_query = function(doc, cdt, cdn) {
			return {
				query: "erpnext.hr.doctype.training_program.training_program.emp_department",
				filters:{'department': frm.doc.department}
			}
		}
	},

	candidates_number: function(frm) {
	     if (frm.doc.department)
		frappe.call({
			method: "erpnext.hr.doctype.training_program.training_program.dep_emp_num",
			args: { "department": frm.doc.department },
			callback: function(r){
				if(r){ 
				  if(parseInt(frm.doc.candidates_number) > parseInt(r.message) )
					frappe.throw(__("Not Allowed! Candidates number more than Department employee numbers"));
					}			
				}
			});
		
  	}
});


frappe.ui.form.on('Training Target', {

	'department': function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		var emp='maysaa';	
		frappe.call({
			method:"erpnext.hr.doctype.training_program.training_program.emp_department",
			args:{'department':d.department},
			callback: function (data) {
				if(data.message) {
					emp = data.message[0].employee_name;
		
			emp_div0='<div class="form-group frappe-control input-max-width" data-fieldtype="Check" data-fieldname="employee">\
			<div class="checkbox"><label>\
			<span class="input-area"><input type="checkbox" autocomplete="off" class="input-with-feedback" data-fieldtype="Check" data-fieldname="employee" placeholder="" data-doctype="Training Target"></span>\
			<span class="label-area small">'+emp+'</span></label><p class="help-box small text-muted"></p></div></div>';

			emp_div='<div class="col grid-static-col col-xs-1  text-center" data-fieldname="employees_html" data-fieldtype="Check"><div class="field-area" style="display: block;"><div class="form-group frappe-control input-max-width" data-fieldtype="Check" data-fieldname="excellent">			<div class="checkbox">				<label>					<span class="input-area"><input type="checkbox" autocomplete="off" class="input-with-feedback input-sm" data-fieldtype="Check" data-fieldname="employees_html" placeholder="Employee" data-doctype="Training Target" data-col-idx="1"></span>					<span class="disp-area" style="display: none;"><i class="octicon octicon-check" style="margin-right: 3px;"></i></span>					<span class="label-area small">'+emp+'</span>				</label>				<p class="help-box small text-muted"></p>			</div>		</div></div><div class="static-area ellipsis" style="display: none;"><i class="octicon octicon-check" style="margin-right: 3px;"></i></div></div>';

 			frm.fields_dict['training_targate'].grid.grid_rows_by_docname[cdn].docfields[4].options= emp_div;
			}
		}	
	});


	},
	'employee': function(frm, cdt, cdn) { 
	    if(cur_frm.doc.candidates_number){
		var count = 0;
		$.each(frm.doc["training_targate"] || [], function(i, t) {
			count += i;
		});
		if(parseInt(cur_frm.doc.candidates_number) < parseInt(count) )
			frappe.throw(__("Not Allowed! Candidates number more than Department employee numbers"));
			return false;
	  }
  	},
	'candidates_number': function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
	     if (d.department)
		frappe.call({
			method: "erpnext.hr.doctype.training_program.training_program.dep_emp_num",
			args: { "department": d.department },
			callback: function(r){
				if(r){ 
				  if(parseInt(d.candidates_number) > parseInt(r.message) )
					frappe.throw(__("Not Allowed! Candidates number more than Department employee numbers"));
				}			
				}
			});
		
  }
})


cur_frm.cscript.custom_trainer_evaluation_questions_add = function(frm, cdt, cdn) {
	frappe.model.set_value(cdt, cdn, 'type', 'Trainer');
};

cur_frm.cscript.custom_trainee_evaluation_questions_add = function(frm, cdt, cdn) {
	frappe.model.set_value(cdt, cdn, 'type', 'Trainee');
};


frappe.ui.form.on("Training Evaluation Questions",  {
	question: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		var count =0;
		$.each(frm.doc["trainee_evaluation_questions"] || [], function(i, e) {
			if(d.question == e.question)
				count+= i;
		});
		if (count >=1) frappe.throw(__("Question existed"));

		var count =0;
		$.each(frm.doc["trainer_evaluation_questions"] || [], function(i, e) {
			if(d.question == e.question)
				count+= i;
		});
		if (count >=1) frappe.throw(__("Question existed"));

	}
});


