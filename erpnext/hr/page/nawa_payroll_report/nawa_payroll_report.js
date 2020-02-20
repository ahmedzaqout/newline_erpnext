frappe.pages['nawa-payroll-report'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		single_column: true
	});
frappe.require(["assets/newlinetheme2/js/editable-table/jquery.dataTables.min.js","assets/newlinetheme2/js/editable-table/editable-table/mindmup-editabletable.js","assets/newlinetheme2/js/editable-table/editable-table/numeric-input-example.js","assets/newlinetheme2/js/editable-table/editable-table-data.js"]);

	required_libs: [
		"assets/newlinetheme2/js/editable-table/jquery.dataTables.min.js","assets/newlinetheme2/js/editable-table/editable-table/mindmup-editabletable.js","assets/newlinetheme2/js/editable-table/editable-table/numeric-input-example.js","assets/newlinetheme2/js/editable-table/editable-table-data.js"
	]
	
	wrapper.page.add_menu_item(__('Refresh'), function() {
	frappe.nawa_payroll_report.make(page);

    });
		
	frappe.nawa_payroll_report.make(page);

}

frappe.nawa_payroll_report = {
	make: function(page) {
		var me = frappe.nawa_payroll_report;
		me.page = page;
		//var salary=[1925,1125,875,650,525,450,420,414];
		var sal=[1925];	var sal2=[1125];var sal3=[875];	var sal4=[650];var sal5=[525];	var sal6=[450];var sal7=[420];	var sal8=[414];
		for(var i=0;i<=20;i++){
			 sal.push( (sal[i] *0.03 +sal[i]) );sal[i]=Math.round(sal[i]);
			 sal2.push( Math.ceil(sal2[i] *0.03 +sal2[i]) );sal2[i]=Math.round(sal2[i]);
			 sal3.push( Math.ceil(sal3[i] *0.03 +sal3[i]) );sal3[i]=Math.round(sal3[i]);
			 sal4.push( Math.ceil(sal4[i] *0.03 +sal4[i]) );sal4[i]=Math.round(sal4[i]);
			 sal5.push( Math.ceil(sal5[i] *0.03 +sal5[i]) );sal5[i]=Math.round(sal5[i]);
			 sal6.push( Math.round(sal6[i] *0.03 +sal6[i]) );sal6[i]=Math.round(sal6[i]);
			 sal7.push( Math.round(sal7[i] *0.03 +sal7[i]) );sal7[i]=Math.round(sal7[i]);
			 sal8.push( Math.round(sal8[i] *0.03 +sal8[i]) );sal8[i]=Math.round(sal8[i]);

			}
		console.log(sal);
		var job_nums=['101','201','202','203','301','302','303','304','305','306','307','401','402','403','404','405','406','407','408','409','410','411','501','502','503','504','601','602','701','702','801','802','803']
	 	frappe.call({
			method: "erpnext.hr.page.nawa_payroll_report.nawa_payroll_report.get_designation",
			callback: function(r) {				
				if(!r.exc) { 
				var designation= 
['المدير/ة  التنفيذي/ة','مدير/ة دائرة الشؤون الإدارية والمالية','مدير/ة دائرة التخطيط والبرامج','مدير/ة دائرة ضمان الجودة','مسؤول/ة الشؤون الإدارية والموارد البشرية','مسؤول/ة الشؤون المالية','مسؤول/ة الثقافة والفنون','مسؤول/ة التعليم','مسؤول/ة الإتصال وتنمية الموارد','مسؤول/ة الامتثال','مسؤول/ة المتابعة والتقييم','منسق/ة المشتريات','المحاسب/ة','منسق/ة  مكتبة الخضر','منسق/ة مركز النوى الثقافي','منسق/ة منتزهات النوى','منسق/ة مركز الداروم','منسق/ة معرض النوى ','منسق/ة الطفولة المبكرة','منسق/ة التدريب','منسق/ة العلاقات العامة','منسق/ة مناصرة','منشط/ة رئيسي /ة','أخصائي/ة نفسي/ة','مدير/ة روضة','مصور/ة','منشط/ة','فني صيانة وبرمجيات','مساعد/ة إداري','أخصائي /ة طفولة مبكرة','الحارس','عامل/ة نظافة','مراسل/ة']//r.message; 
				$(frappe.render_template('nawa_payroll_report',{'designation':designation,'job_nums':job_nums,'sal':sal,'sal2':sal2,'sal3':sal3,'sal4':sal4,'sal5':sal5,'sal6':sal6,'sal7':sal7,'sal8':sal8})).appendTo(me.page.main);
				}
			}
		});

	


	}













}




