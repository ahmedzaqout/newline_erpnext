// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project Closing', {
	onload: function(frm){
		 if(frm.is_new()){
	 	var day_list = ["Customer","Company","Other"];
		for(var i=0; i<day_list.length; i++) {
		   var row = frappe.model.add_child(cur_frm.doc, "Lateness Doc", "lateness");
		   row.lateness_type = day_list[i];
		   refresh_field("lateness");
		}

}


	},
	refresh: function(frm) {
	hideTheButtonWrapper = $('*[data-fieldname="lateness"]');
	hideTheButtonWrapper .find('.grid-add-row').hide();
		
	hideTheButtonWrapper = $('*[data-fieldname="working_hours"]');
	hideTheButtonWrapper .find('.grid-add-row').hide();
	
	hideTheButtonWrapper = $('*[data-fieldname="millstone"]');
	hideTheButtonWrapper .find('.grid-add-row').hide();



	me=this;
	if (me.labels && me.re){
		chart = new Chart({ 
					parent : "#chart",
		  			data: {
					    labels: me.labels,
					    datasets: [
					       {
						name: "Estimated",
						values: me.re,

					      },
					      {
						name: "Real",
						values: me.est,

					      }
					    ]
					},
					title: "Employee Working Hours",
				    type: 'bar',
				    height: 250,
				   colors: ['#d056e2','#8a56e2','#56aee2','#ade255']
				});

chart = new Chart({ 
					parent : "#chart2",
		  			data: {
					    labels: ["Estimated","Real"],
					    datasets: [
					        {
				 values:  [me.totaldata['totalexp'],me.totaldata['totalreal']]
					        }
					    ]
					},
					title: "Total Working Hours",
				    type: 'bar',
				    height: 250,
				   colors: ['#56aee2']
				});
		
}
	
	},
	project: function(frm){
	
	me=this;
	this.labels=[];
	this.re=[];
	this.est=[];
	if (frm.doc.project){
	frappe.call({
		method: "erpnext.projects.doctype.project_closing.project_closing.get_schedule",
			args: { 
				"project":frm.doc.project
			 },
			freeze:true,
			callback: function(r)
			{
			data=r.message.data;
			me.totaldata=r.message.totaldata;
			first=r.message.first;
			millstone=r.message.millstone;
			frm.set_value("real_start_date",first);
		   refresh_field("real_start_date");
			frm.set_value("working_hours", []);

			frm.set_value("millstone", []);
			for(var i=0; i<millstone.length; i++) {
		   var row = frappe.model.add_child(cur_frm.doc, "Millstone", "millstone");
			row.no = "تسليم "+ (i+1);	
		   	row.date = millstone[i][0];	
				}

		   refresh_field("millstone");




		for(var i=0; i<data.length; i++) {
		   var row = frappe.model.add_child(cur_frm.doc, "Project Working Hours", "working_hours");
		   	row.employee = data[i][0];	
			row.employee_name=data[i][1];
			row.specialization=data[i][2];
			row.expected_time=data[i][3];
			row.real_time=data[i][4];
			row.differentiation=data[i][5];
			row.diff_percent=data[i][6]+ " %";
			
			me.labels.push(data[i][1]+"-"+data[i][2]);
			me.re.push(data[i][4]);
			me.est.push(data[i][3]);
			

		}
				   refresh_field("working_hours");
		frm.set_value("total_expected_time", me.totaldata['totalexp']);
		frm.set_value("total_real_time", me.totaldata['totalreal']);
		frm.set_value("total_differentiation", me.totaldata['totdiff']);
		frm.set_value("percent", me.totaldata['totper']+ " %");
		   refresh_field("total_expected_time");
		   refresh_field("total_real_time");
		   refresh_field("total_differentiation");
		   refresh_field("percent");
			console.log(r);

		chart = new Chart({ 
					parent : "#chart",
		  			data: {
					    labels: me.labels,
					    datasets: [
					       {
						name: "Estimated",
						values: me.re,

					      },
					      {
						name: "Real",
						values: me.est,

					      }
					    ]
					},
					title: "Employee Working Hours",
				    type: 'bar',
				    height: 250,
				   colors: ['#d056e2','#8a56e2','#56aee2','#ade255']
				});

chart = new Chart({ 
					parent : "#chart2",
		  			data: {
					    labels: ["Estimated","Real"],
					    datasets: [
					        {
				 values:  [me.totaldata['totalexp'],me.totaldata['totalreal']]
					        }
					    ]
					},
					title: "Total Working Hours",
				    type: 'bar',
				    height: 250,
				   colors: ['#56aee2']
				});

				
			}
		});
}
cur_frm.refresh();
}
});


frappe.ui.form.on('Lateness Doc', {
	lateness_days: function (frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		if (child.lateness_type=="Customer"){
		console.log(frm.doc.hidd_exp);
		var expected=frm.doc.hidd_exp;
		var date = new Date(expected);
		date.setDate( date.getDate()+child.lateness_days);
		d=new Date(date).toISOString().slice(0, 10);;
		frm.doc.expected_end_date=d;
		console.log(d);
		frm.set_value("expected_end_date", d);
		refresh_field("expected_end_date");
		
}
		var tl = frm.doc.lateness || [];
		var latness = 0;
		for(var i=0; i<tl.length; i++) {
			if (tl[i].lateness_days) {
				latness += parseFloat(tl[i].lateness_days);
			}
		}
		frm.set_value("total_lateness", latness);
	}
});
