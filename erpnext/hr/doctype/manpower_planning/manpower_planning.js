// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Manpower Planning', {
	refresh: function(frm) {
		
		frm.set_value("department", '');
		//var $wrapper = d.fields_dict.manpower_planning_item
		var me= this;
//console.log( $($(frm.fields_dict.manpower_planning_item.$wrapper.find('.frappe-control')).find('form-grid').find('grid-heading-row').find('.grid-row').find('data-row row').find('col grid-static-col col-xs-1 ')).css('width', '0px') );
		//$($(frm.fields_dict.manpower_planning_item.$wrapper.find('.form-column')).find('.frappe-control')).css('margin-bottom', '0px');
		frappe.call({
			method: "erpnext.hr.doctype.manpower_planning.manpower_planning.get_salary_components",
			callback: function (r) {						
				earning = r.message[0];
				deduction = r.message[0];
				for (var i=0; i< earning.length; i++) {
					frappe.call({
					method: "erpnext.hr.doctype.manpower_planning.manpower_planning.add_field",
					args:{
					"doctype":"Manpower Planning Items",
					"field_label":earning[0],
					"field_name":earning[0].replace(/\s+/g, '-').toLowerCase(),
					"field_type":"Data"
					},
					callback: function (r) {
						//console.log(r);
							}
					});
				}
				//End For

		}
	});
	},
 	manpower_planning_item_remove: function(frm) {
		calculate_totals(frm.doc);
	},
 	manpower_planning_item_add: function(frm) {
		calculate_totals(frm.doc);
	},
 	calc_total: function(frm) {
		var total_sal = 0.0;
		frm.doc.manpower_planning_item.forEach(function(d) { total_sal += d.total;  });
		frm.set_value("total", total_sal);
		frm.refresh_field('total');

	
		//$.each(frm.doc.manpower_planning_item || [], function(i, row) {
		//	total_sal += d.total;
		//	console.log(row);
		//});
	},


	department:function(frm) {
		//frm.set_value("manpower_planning_item", []);
	   if (frm.doc.department)
	        frm.set_value("manpower_planning_item", []);
		frappe.call({
			method: "erpnext.hr.doctype.manpower_planning.manpower_planning.get_dep",
			args:{"department":frm.doc.department},
			callback: function (r) {
					 //console.log(r.message);

			var manpower_planning_item = $.map(frm.doc.manpower_planning_item, function(d) { return d.employee_number });
				for (var i=0; i< r.message.length; i++) {
						//console.log(manpower_planning_item.indexOf(r.message[i].employee_number))
					if (manpower_planning_item.indexOf(r.message[i].employee_number) === -1 && r.message[i].designation) {
						var row = frappe.model.add_child(frm.doc, frm.fields_dict.manpower_planning_item.df.options, frm.fields_dict.manpower_planning_item.df.fieldname);
						row.designation = r.message[i].designation;
						row.grade = r.message[i].grade;
						row.category = r.message[i].grade_category; 
						row.experience = r.message[i].experience_years;
						row.basic_salary = r.message[i].basic_salary;
						row.work_hour = r.message[i].work_hrs;
						row.total = row.basic_salary;
						}

					}
				calculate_totals(frm.doc);
				frm.refresh_field('manpower_planning_item');
				}
		});
	},



});
//cur_frm.cscript.total = function(doc, cdt, cdn){
//	calculate_totals(doc, cdt, cdn);
//};

var calculate_totals = function(doc) {
	var tbl1 = doc.manpower_planning_item || [];

	var total_sal = 0.0; 
	//for(var i = 0; i < tbl1.length; i++){
	//	total_sal += flt(tbl1[i].amount);
	//}
	//doc.total = total_sal; 
	cur_frm.doc.manpower_planning_item.forEach(function(d) { if(d.grade) total_sal += d.total; else total_sal +=0.0;  });
	cur_frm.set_value("total", total_sal);
	refresh_field('total');

}

var calc_quittance = function(frm,cdt,cdn) {
	   frappe.call({
		method: "erpnext.hr.doctype.leave_application.leave_application.get_leave_balance_on",
		args: {
			employee:'',
			date: frappe.datetime.get_today(),
			leave_type: 'Annual Leave',
			consider_all_leaves_in_the_allocation_period: true
			},
		callback: function(r) {
			if (!r.exc && r.message) {
				annual_leaves=r.message;
				}
					}
				});

		var leavs=0.0;
		var leavs_quant=0.0;
		//vacation_allowance_based_on_basic_salary
		//salary_allowance_based_on_basic_salary
		var salary_period =  0;
		var v_salary = d.total;
		var salary = d.total;
		if (d.salary_period == 'Monthly') salary_period = 30;
		if (d.salary_period == 'Hourly') salary_period = 26;


		frappe.db.get_value("HR Settings", {'name':"HR Settings"}, 'vacation_allowance_based_on_basic_salary', (data) => {
			if( data.vacation_allowance_based_on_basic_salary == '1')
				v_salary= d.basic_salary;
			});

		frappe.db.get_value("HR Settings", {'name':"HR Settings"}, 'salary_allowance_based_on_basic_salary', (data) => {
			if( data.salary_allowance_based_on_basic_salary == '1')
				salary= d.basic_salary;
			});

		if (d.years <= 5){
			leavs=14 * 2;
			leavs_quant = leavs * ( v_salary / salary_period);
			}
		else {
			leavs=21 * 2;
			leavs_quant = leavs * ( v_salary / salary_period);
		    }


		if (d.years <= 5)
			d.quittance= parseFloat(d.years) * (parseFloat(salary) * (1/3)) + leavs_quant;

		else if (d.years > 5  && d.years <= 10)
			d.quittance= parseFloat(d.years) * (parseFloat(salary) * (2/3)) + leavs_quant ;
	
		else if(d.years > 10)
			d.quittance= parseFloat(d.years) * parseFloat(salary) +leavs_quant ;
		

		var dd= frappe.db.get_value("HR Settings", "None", "add_additional_salary_to_end_service_total");

		frappe.db.get_value("HR Settings", {'name':"HR Settings"}, 'add_additional_salary_to_end_service_total', (data) => {
		   if( data.add_additional_salary_to_end_service_total == '1')
			d.end_of_service= parseFloat(d.years) * parseFloat(salary)  + leavs_quant + parseFloat(salary);
		   else
			d.end_of_service= parseFloat(d.years) * parseFloat(salary)  + leavs_quant ;
		});
		refresh_field("quittance", cdn, "manpower_planning_item");
		refresh_field("end_of_service", cdn, "manpower_planning_item");

}

var update_total = function(frm,cdt,cdn) {
		d = locals[cdt][cdn];
		var total_sal = 0.0;
		grade= d.grade;
		experience= d.experience;
		frappe.model.get_value('Grade Category Detail', {'parent': grade, 'experience_year':experience}, 'basic_salary',function(r) {
			    if (!r){
				d.basic_salary = 0;
				//frappe.throw(__("Salary does not setup for that experience years"))
				return false;
				}
				d.basic_salary = r.basic_salary;
				refresh_field("basic_salary", cdn, "manpower_planning_item");
				//d.total = r.basic_salary;
				refresh_field("total", cdn, "manpower_planning_item");
			update_premium_nature_work(frm,cdt,cdn);
		if (d.monthly_work_hour){
			d.hour_cost = parseFloat(r.basic_salary) / parseFloat(d.monthly_work_hour);
			refresh_field("hour_cost", cdn, "manpower_planning_item");}

		var total = (r.basic_salary); console.log(d.premium_nature_work);
		d.total= (parseFloat(r.basic_salary) +(d.premium_nature_work? parseFloat(d.premium_nature_work):0) + (d.bonus_wife? parseFloat(d.bonus_wife):0)+ (d.bonus_children? parseFloat(d.bonus_children):0) +(d.transportation? parseFloat(d.transportation):0) + (d.business_allowance? parseFloat(d.business_allowance):0) + (d.replacement_allowance? parseFloat(d.replacement_allowance):0 ) )- (d.deductions? parseFloat(d.deductions):0) ;
		//d.total= r.basic_salary; console.log(r.basic_salary); 
		refresh_field("total", cdn, "manpower_planning_item");
		calc_quittance(frm,cdt,cdn)


		frm.doc.manpower_planning_item.forEach(function(d) { total_sal += d.total;  });
		if (total_sal==NaN || !total_sal) total_sal = 0.0;

		cur_frm.set_value("total", total_sal);
		cur_frm.refresh_field('total');
		calculate_totals(frm.doc);
	});

}

var update_premium_nature_work = function(frm,cdt,cdn) {
	d = locals[cdt][cdn];
	frappe.model.get_value('Earnings Detail', {'designation':d.designation,'degree':d.grade}, 'ratio',function(r) {
			if(r){
			d.premium_nature_work = (r.ratio/100) * parseFloat(d.basic_salary);
			refresh_field("premium_nature_work", cdn, "manpower_planning_item");
			}
		});

}
frappe.ui.form.on("Manpower Planning Items",  {

	grade: function(frm,cdt,cdn) {
		
		update_total(frm,cdt,cdn);

//calculate_totals(frm.doc);
	},

	designation: function(frm,cdt,cdn) {
		d = locals[cdt][cdn];
	    if(d.designation){
		update_premium_nature_work(frm,cdt,cdn);
		var earnings_ammount=0; 

	        frappe.call({
			method: "erpnext.hr.doctype.manpower_planning.manpower_planning.get_job_description",
			args: { "designation":d.designation},
			callback: function(r) { //console.log(r);
			    if (!r.exc && r.message) {
				d.grade = r.message[0].grade;
				d.category = r.message[0].category;
				d.basic_salary = r.message[0].basic_salary;
				d.experience = r.message[0].experience_year;
				d.monthly_work_hour = r.message[0].monthly_work_hours;
				d.salary_period = r.message[0].salary_period;
				d.hour_cost = r.message[0].hour_cost;
				d.deductions = r.message[0].deductions;

			    }
			}
		});

		update_total(frm,cdt,cdn);
		calculate_totals(frm.doc);
		refresh_field("manpower_planning_item");

	      }
	},

	experience: function(frm,cdt,cdn) {
		update_total(frm,cdt,cdn);
	},
	basic_salary: function(frm,cdt,cdn) {
		update_total(frm,cdt,cdn);
	},
	monthly_work_hour: function(frm,cdt,cdn) {
		d = locals[cdt][cdn];
		d.hour_cost = parseFloat(d.basic_salary) / parseFloat(d.monthly_work_hour);
		refresh_field("hour_cost", cdn, "manpower_planning_item");
			update_total(frm,cdt,cdn);

	},

	years: function(frm,cdt,cdn) {
		d = locals[cdt][cdn];

			calc_quittance(frm,cdt,cdn);
			update_total(frm,cdt,cdn);

	},
	
	bonus_wife : function(frm,cdt,cdn) {
		d = locals[cdt][cdn];
		frappe.model.get_value('HR Settings', {'name': 'HR Settings'}, 'bonus_wife_ratio', function(r) {
			if (r.bonus_wife_ratio && d.basic_salary){
				//if (r.bonus_wife_ratio == NaN)
				var bw = d.bonus_wife;
				if (d.bonus_wife>1)  bw=1;
		
				var bonus_wife = bw * (r.bonus_wife_ratio ) ;
				d.bonus_wife = bonus_wife;

			}
			else d.bonus_wife = 0;

			refresh_field("bonus_wife", cdn, "manpower_planning_item");

			update_total(frm,cdt,cdn);

		})


	},
	bonus_children : function(frm,cdt,cdn) {
		d = locals[cdt][cdn];
		frappe.model.get_value('HR Settings', {'name': 'HR Settings'}, 'bonus_children_ratio', function(r) {
			if (r.bonus_children_ratio && d.basic_salary){
				var bonus_children = d.bonus_children* (r.bonus_children_ratio ) ;
				d.bonus_children = bonus_children;

			}
			else d.bonus_children = 0;

			refresh_field("bonus_children", cdn, "manpower_planning_item");
			update_total(frm,cdt,cdn);

		})


	},
	premium_nature_work : function(frm,cdt,cdn) {
			update_total(frm,cdt,cdn); 
	},
	transportation : function(frm,cdt,cdn) {
			update_total(frm,cdt,cdn); 
	},
	business_allowance : function(frm,cdt,cdn) {
			update_total(frm,cdt,cdn); 
	},
	replacement_allowance : function(frm,cdt,cdn) {
			update_total(frm,cdt,cdn); 
	},
	deductions : function(frm,cdt,cdn) {
			update_total(frm,cdt,cdn); 
	},
	individual_tax : function(frm,cdt,cdn) {
			update_total(frm,cdt,cdn); 
	},
	insurance_tax : function(frm,cdt,cdn) {
			update_total(frm,cdt,cdn); 
	},
	premium_nature_work : function(frm,cdt,cdn) {
		update_premium_nature_work(frm,cdt,cdn);
	},
	
	 update_totals_old: function(frm,cdt,cdn) {
		d = locals[cdt][cdn];
		d.total= parseFloat(d.basic_salary) +parseFloat(d.basic_salary) +parseFloat(d.premium_nature_work) +parseFloat(d.bonus_wife) -parseFloat(d.deductions) 
		var total_sal = 0.0;
		frm.doc.manpower_planning_item.forEach(function(d) { total_sal += d.total;  });
		frm.set_value("total", total_sal);
		refresh_field("total", cdn, "manpower_planning_item");
		frm.refresh_field('total');
	},

	//console.log(d);

	//total: function(frm,cdt,cdn) {
	//	d = locals[cdt][cdn];
	//	var total_sal = 0.0;
	//	frm.doc.manpower_planning_item.forEach(function(d) { total_sal += d.total;  });
	//	frm.set_value("total", total_sal);
	//	frm.refresh_field('total');
	//}

});


