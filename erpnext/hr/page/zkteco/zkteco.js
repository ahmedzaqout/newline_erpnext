frappe.pages['zkteco'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'None',
		single_column: true
	});
chart = new Chart({ 
					parent : "#chart",
		  			data: {
					    labels: ['x','y','z'],
					    datasets: [
					        {
					            values: 	 [10,15,13]
					        }
					    ]
					},
					title: "title",
				    type: 'pie',
				    height: 250,
				   colors: ['#d056e2', '#8a56e2','#56aee2','#ade255']
				});
	//frappe.zkteco.make(page);
}

frappe.zkteco = {
	make: function(page) {
		var me = frappe.zkteco;
		me.page = page;

 		frappe.call({
			method: "erpnext.hr.page.zkteco.zkteco.connec",
			//args: {},
			callback: function(r) {
				console.log(r)			
				}
			});


		}
	}	
