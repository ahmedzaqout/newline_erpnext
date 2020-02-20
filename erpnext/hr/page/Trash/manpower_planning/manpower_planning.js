 function myRequire( url ) {
    var ajax = new XMLHttpRequest();
    ajax.open( 'GET', url, false ); // <-- the 'false' makes it synchronous
    ajax.onreadystatechange = function () {
        var script = ajax.response || ajax.responseText;
        if (ajax.readyState === 4) {
            switch( ajax.status) {
                case 200:
                    eval.apply( window, [script] );
                    break;
                default:

            }
        }
    };
    ajax.send(null);
}
myRequire('/assets/newlinetheme2/js/editable-table/jquery.dataTables.min.js');
myRequire('/assets/newlinetheme2/js/editable-table/editable-table/mindmup-editabletable.js');
myRequire('/assets/newlinetheme2/js/editable-table/editable-table/numeric-input-example.js');
myRequire('/assets/newlinetheme2/js/editable-table/manpower_planning_data.js');



frappe.pages['manpower-planning'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Manpower Planning'),
		single_column: true
	});
alert(window.location)
frappe.require(["assets/newlinetheme2/js/editable-table/jquery.dataTables.min.js","assets/newlinetheme2/js/editable-table/editable-table/mindmup-editabletable.js","assets/newlinetheme2/js/editable-table/editable-table/numeric-input-example.js","assets/newlinetheme2/js/editable-table/manpower_planning_data.js"]);
	wrapper.page.add_menu_item(__('Refresh'), function() {
		frappe.manpower_planning.make(page);

    });
	wrapper.page.set_primary_action(__("Save"),
				function() { 
	frappe.manpower_planning.save();
			 }, "fa fa-refresh"),
		
	frappe.manpower_planning.make(page);
}

frappe.manpower_planning = {
	make: function(page) {

		var me = frappe.manpower_planning;
		me.page = page;
		var grade =["A1","A2","A3","A4","C","B","A","1","2","3","4","5","6","7","8","9","10"];
		//var category =["الفئة العليا","الفئة الأولى","الفئة الثانية","الفئة الثالثة","الفئة الرابعة","الفئة الخامسة"];
		var category  = [__("Top category"),__("First category"),__("second category"),__("Third category"),__("Fourth category"),__("Fifth category")]

		//
		frappe.call({
			method: "erpnext.hr.page.manpower_planning.manpower_planning.get_departments",
			callback: function(r) {
				if(!r.exc) {
					departments = r.message;
					//console.log(departments)

					frappe.call({
						method: "erpnext.hr.page.manpower_planning.manpower_planning.get_data",
						callback: function(r) {
							if(!r.exc) {
								if (r.message ==undefined)
									frappe.throw(__("No Data"))
								//console.log(r.message)
								employees=r.message;




					frappe.call({
						method: "erpnext.hr.page.manpower_planning.manpower_planning.get_salary_components",
						callback: function(r) {
								//console.log(r)
							if(!r.exc) {

								ecomponent = r.message[0];
								dcomponent = r.message[1];}

					frappe.call({
						method: "erpnext.hr.page.manpower_planning.manpower_planning.get_salary_components_data",
						callback: function(r) {
								//console.log(r)
							if(!r.exc) {

								e_comp = r.message[0];
								d_comp = r.message[1];}

	
	me.page = page.main.html(frappe.render_template("manpower_planning", {"departments":departments,"data":employees,"category":category,"grade":grade,"ecomponent":ecomponent,"dcomponent":dcomponent,"e_comp":e_comp,"d_comp":d_comp}));


}});
}});



							}
						}
					});


				}
			}
		});


	},
	save: function() {
		return frappe.call({
				method: "erpnext.hr.page.manpower_planning.manpower_planning.save_payroll",
				args: {
					"salary": salary
				},
				callback: function(r) {
					if(!r.exc) {
					frappe.show_alert({message:__('Saved'), indicator:'darkgrey'});
					}
				}
			});
	}
},


$(document).ready(function(){
	console.log("ddd")

});



