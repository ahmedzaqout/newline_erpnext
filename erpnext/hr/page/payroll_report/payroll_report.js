frappe.pages['payroll-report'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Payroll Report'),
		single_column: true
	});
frappe.require(["assets/newlinetheme2/js/editable-table/jquery.dataTables.min.js","assets/newlinetheme2/js/editable-table/editable-table/mindmup-editabletable.js","assets/newlinetheme2/js/editable-table/editable-table/numeric-input-example.js","assets/newlinetheme2/js/editable-table/editable-table-data.js"]);

	required_libs: [
		"assets/newlinetheme2/js/editable-table/jquery.dataTables.min.js","assets/newlinetheme2/js/editable-table/editable-table/mindmup-editabletable.js","assets/newlinetheme2/js/editable-table/editable-table/numeric-input-example.js","assets/newlinetheme2/js/editable-table/editable-table-data.js"
	]
	
	wrapper.page.add_menu_item(__('Refresh'), function() {
	frappe.payroll_report.make(page);
//frappe.show_alert({message: __('Enter Payroll Start Number'), indicator: 'green'});

    });
	//wrapper.page.add_menu_item(__('Save'), function() {
	//frappe.payroll_report.save(page);

  //  });
	//console.log($(wrapper).find(".page-head"));
	wrapper.page.set_primary_action(__("Save"),function() { 
	//console.log(sessionStorage.getItem("data_arr"));
	//var data_arr = localStorage.getItem("data_arr "); 
	//console.log(data_arr);
	frappe.payroll_report.save();
			 }, "fa fa-refresh"),
		
	frappe.payroll_report.make(page);
	//frappe.show_alert({message: __('Enter Payroll Start Number'), indicator: 'green'});
	//$(wrapper).find('#edit_datable_1').editableTableWidget().numericInputExample().find('td:first').focus();

}

frappe.payroll_report = {
	make: function(page) {
		var me = frappe.payroll_report;
		me.page = page;

		//me.more = $('<div class="for-more"><button class="btn btn-sm btn-default btn-more">'
		//	+ __("Save") + '</button></div>').appendTo(me.page.main)
		//	.find('.btn-more').on('click', function() {

		//	});

 
	me.more = $('<div class="row input_class"><div class="col-sm-3"><input type="text" autocomplete="off" class="input-with-feedback form-control input-sm" data-fieldtype="Float" data-fieldname="salary_budget" placeholder="'+__("Salary Budget")+'" data-col-idx="7"></div><div class="col-sm-3"><input type="text" autocomplete="off" class="input-with-feedback form-control input-sm" data-fieldtype="Float" data-fieldname="total_employee" placeholder="'+__("Total Employee")+'" data-col-idx="7"></div><div class="col-sm-1"><button class="btn btn-sm btn-default btn-more">'+ __("Calculate") + '</button></div></div></div>').appendTo(me.page.main)
			.find('.btn-more').on('click', function() {

				var salary_budget= $('input[data-fieldname="salary_budget"]').val();
				var total_employee= $('input[data-fieldname="total_employee"]').val();
				var salary_average= (parseFloat(salary_budget)/ parseFloat(total_employee)) *10;
				var start_payroll=   Math.round( (parseFloat(salary_average)/2) * 100) / 100;
				//var e = $.Event( "keyup", {which: 13} );
				me.page.wrapper.find('#smain').text(start_payroll)
				//me.page.wrapper.find('#smain').trigger(e);
				var $rows = me.page.wrapper.find('#edit_datable_1 tbody >tr');
				//sessionStorage.setItem("start_payroll", start_payroll);
				//console.log($rows);
	 frappe.call({
		method: "erpnext.hr.page.payroll_report.payroll_report.payroll_increase_ratio",
				callback: function(r) {				
					if(!r.exc) {
					var payroll_increase_ratio= (r.message[2])?r.message[2]:0;
					var payroll_increase_ratio1= (r.message[1])?r.message[1]:0;
					var payroll_discount_ratio= (r.message[0])?r.message[0]:2.5;
				//console.log(payroll_discount_ratio)
for (var r = 1; r < $rows.length; r++) 
for (var j = 17; j > 0; j--) {

if (j==17)
$rows[r].cells[j].innerHTML =Math.round( (parseFloat($rows[r-1].cells[j].innerHTML) *parseFloat(payroll_discount_ratio)/100 + parseFloat($rows[r-1].cells[j].innerHTML))*10)/10;
else{
if($rows[0].cells[j] && j!=17) 
	if(j>=7)
		$rows[0].cells[j].innerHTML = Math.round( (parseFloat($rows[0].cells[j+1].innerHTML) + parseInt(payroll_increase_ratio)) * 100) / 100 ; 
	else
		$rows[0].cells[j].innerHTML = Math.round( ( parseFloat($rows[0].cells[j+1].innerHTML) +  parseInt(payroll_increase_ratio1)) * 100) / 100; 

$rows[r].cells[j].innerHTML =Math.round( (parseFloat($rows[r-1].cells[j].innerHTML) *parseFloat(payroll_discount_ratio)/100 + parseFloat($rows[r-1].cells[j].innerHTML))*10)/10;
}


}
	}
				}
			});

	
				
			});

	$(frappe.render_template('payroll_report'),{}).appendTo(me.page.main);
	frappe.payroll_report.get_grades();
	
	


		//console.log($(wrapper).find('.layout-main-section');)

	},
	get_grades: function() {
		var grad_arr = ['','A1','A2','A3','A4','A','B','C','1','2','3','4','5','6','7','8','9','10'];
		var $rows = this.page.wrapper.find('#edit_datable_1 tbody >tr');
	for (var g = 1; g < grad_arr.length ; g++) {
		 frappe.call({
				method: "erpnext.hr.page.payroll_report.payroll_report.get_grades",
				args: {
					"grade" : grad_arr[g]
				},
				callback: function(r) {
					if(!r.exc) {	
				var grdes = ['','A1','A2','A3','A4','A','B','C','1','2','3','4','5','6','7','8','9','10'];
				num =grdes.indexOf(r.message[0].parent);
			
					//console.log(r.message)
					if (r.message)
					for (var i = 0; i < 30; i++) {
						$rows[i].cells[num].innerHTML= r.message[i].basic_salary;

							}
					}
				}
			});
		}

	},
	


	save: function() {

		var grad_arr = ['','A1','A2','A3','A4','A','B','C','1','2','3','4','5','6','7','8','9','10']
		var category_arr = ['Top category','First category','second category','Third category','Fourth category','Fifth category']
//		var salary= sessionStorage.getItem("data_arr");
		var $rows = this.page.wrapper.find('#edit_datable_1 tbody >tr');

		frappe.show_alert({message:__('Wait...'), indicator:'green'});

	 for (var g = 1; g < grad_arr.length ; g++) {
		if (g< 5) category = category_arr[0];
		else if (g>=5 && g<8) category = category_arr[1];	
		else if (g>=8 && g<13) category = category_arr[2];		
		else if (g>=11 && g<16) category = category_arr[3];		
		else if (g>=12 && g<17) category = category_arr[4];		
		else if (g>=13 && g<18) category = category_arr[5];		

		
	
		var sal= new Array();
		for (var i = 0; i < 30; i++) {
  			sal.push( $rows[i].cells[g].innerHTML) ;
			}
		var salary = JSON.parse(JSON.stringify(sal));
		//console.log(salary);
		 frappe.call({
				method: "erpnext.hr.page.payroll_report.payroll_report.save_payroll",
				args: {
					"salary": salary,
					"grade" : grad_arr[g],
					"category":category
				},
				callback: function(r) {
					console.log(r);
					if(!r.exc) {		
					frappe.show_alert({message:__(r.message), indicator:'green'});
					}
				}
			});
		}
	}




}




