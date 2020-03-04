frappe.pages['employee-information'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Employee Information'),
		single_column: true
	});
frappe.employee.make_details(page);
}

frappe.employee ={
	name: 'Marital Status Chart',
	make_details: function(page) {
		me=this;
		this.employees=null;

	me.page = page.main.append("<div id='stat'> <div class='table-responsive'><table id='edit_datable_1' class='table  table-bordered table-striped m-b-0' style='cursor: pointer;'> <thead><tr><th>"+__('Image')+"</th><th>"+__('Employee')+"</th><th>"+__('Employee Name')+"</th><th>"+__('Department')+"</th><th>"+__('Designation')+"</th></tr><tbody id='bod'></tbody</div>");	

	me=this;
		frappe.call({
			method: "erpnext.hr.page.employee_information.employee_information.get_details",
			freeze:true,
			callback: function(r) {
				me.employees=r.message.values;
				me.draw();

			}
		});
	
	},
	draw:function () {
		me=this;
		wrap=me.page.find("#bod");

		for(i=0;i<me.employees.length;i++){
			if (me.employees[i]['image']){
			ss="<tr><td><img src='"+me.employees[i]['image']+"'width='60px'/></td><td>"+me.employees[i]['employee']+"</td><td>"+me.employees[i]['employee_name']+"  </td><td>"+me.employees[i]['department']+"  </td><td>"+me.employees[i]['designation']+"</td></tr>";
}else{
ss="<tr><td><img src='https://x1.xingassets.com/assets/frontend_minified/img/users/nobody_m.original.jpg'width='60px'/></td><td>"+me.employees[i]['employee']+"</td><td>"+me.employees[i]['employee_name']+"  </td><td>"+me.employees[i]['department']+"  </td><td>"+me.employees[i]['designation']+"</td></tr>";
 
}
			wrap.append(ss);

		}


												
				

	}

}
