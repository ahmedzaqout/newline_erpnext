frappe.require("/assets/js/libs.min.js");


// import { Chart } from "frappe-charts"

frappe.pages['working_hours'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Working Hours',
		single_column: true
		});

	page.warehouse_field = page.add_field({
		fieldname: 'employee',
		label: __('Employee'),
		fieldtype:'Link',
		options:'Employee',
		reqd: 1,
		change: function() {
		frappe.working_hours.emplyee=this.value;
		this.page=frappe.working_hours.make_page(page);

		}
	});
	this.page=frappe.working_hours.make_page(page);

}

frappe.working_hours = {

	make_page: function(page) {
		me=this;
		me,employee=null;
		me.page = page.main.append('<div id="chart"></div>');	
		me.get_att();


	},
	get_att:function(){
		me=this;
		frappe.call({
			method: "erpnext.hr.page.working_hours.working_hours.get_att",
			freeze:true,
			args: {
				employee: me.employee
			},
			freeze: true,
			callback: function(r) {
				console.log(r);
				me.draw();
				
				
			}
		});
	},

	draw:function () {	
		da = new Date();
		month=da.getMonth()
		d=da.getDate();
		console.log(d);
			l=[]
			if(d<13){
				j=1;
			}
			else{
				j=d-11;
			}
			for(i=j;i<=d;i++){
				l.push(i+ "/"+ month);
			}

  data={
      labels: l,

      datasets: [
        {
          // name: "Some Data", chartType: 'bar',
          values: [25, 40, 30, 35, 8, 52]
        }]
    };
	chart = new Chart( { 
    parent:"#chart",
    title: "Attendance",
    type: 'bar', 
    height: 300,
    colors: ['purple'],
    data:data


   
  });

	}
}