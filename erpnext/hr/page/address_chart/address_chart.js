frappe.pages['address-chart'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Address Chart',
		single_column: true
	});
		frappe.address.make_chart(page);	

}

frappe.address ={
	name: 'Address Chart',
	make_chart: function(page) {
		me=this;
		this.labels=null;
		this.values=null;

     
	me.page = page.main.append("<div id='chart'></div>");	
	page.main.append("<div id='stat'> <div class='table-responsive'><table id='edit_datable_1' class='table  table-bordered table-striped m-b-0' style='cursor: pointer;'> <thead><tr><th>Address</th><th>Count</th><th>Persentage</th></tr><tbody id='bod'></tbody</div>");	

	me=this;
		frappe.call({
			method: "erpnext.hr.page.address_chart.address_chart.get_addreses",
			freeze:true,
			callback: function(r) {
				me.labels=r.message.labels;
				me.values=r.message.values;
				data={
					    labels: me.labels,
					    datasets: [
					        {
					            values: me.values
					        }
					    ]
					};
					console.log(data);
					me.draw();
				
				
			}
		});


		
	},
	draw:function () {
		me=this;
		total=0
		for(i=0;i<me.values.length;i++){
				total+=me.values[i];
			}
			if (total==0){
				ch=me.page.find("#chart");
				ch.append("<h2> No Employee with any city found</h2>")
			}
			else{
			chart = new Chart({ 
					parent : "#chart",
		  			data: {
					    labels: me.labels,
					    datasets: [
					        {
					            values: me.values
					        }
					    ]
					},
					title: "Address Chart",
				    type: 'pie',
				    height: 250,
				   colors: ['#d056e2', '#8a56e2','#56aee2','#ade255']
				
				});
		}
			total=0
			for(i=0;i<me.values.length;i++){
				total+=me.values[i];
			}

			wrap=me.page.find("#bod");
			console.log(wrap);
			console.log(me.labels.length);


			for(i=0;i<me.labels.length;i++){
				if (total==0)
				ss="<tr><td>"+me.labels[i]+"</td><td>"+me.values[i]+"</td><td> </td></tr>";
			else{
				per=(me.values[i] *100.0 / total).toFixed(2);
				ss="<tr><td>"+me.labels[i]+"</td><td>"+me.values[i]+"</td><td>"+per+" % </td></tr>";
}
				wrap.append(ss);

			}


												
				

	}

}
