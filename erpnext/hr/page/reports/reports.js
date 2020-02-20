var module_name = "HR";
frappe.pages['reports'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Reports'),
		single_column: true
	});

	frappe.reports.make(page);
}



frappe.reports = {
	make: function(page) {
		var me = frappe.reports;
		me.page = page;

		frappe.call({
			method: "frappe.desk.moduleview.get",
			args: {
				module: module_name 
			},
			callback: function(r) {
				var m = frappe.get_module(module_name);
				m.data = r.message.data; 
				frappe.reports.process_data(module_name, m.data);
				//page.section_data[module_name] = m;
				console.log(m.data)
		me.page.main.html(frappe.render_template('reports',{"test":"test","data":m.data} ));
	//$(frappe.render_template('reports'),{'test':'test','data':data}).appendTo(me.page.main);
			},
			freeze: true,
		});


	//frappe.reports.get_reports(me.page);

	},
	get_reports: function(page) {
		//var module_name = "HR";
		frappe.call({
			method: "frappe.desk.moduleview.get",
			args: {
				module: module_name 
			},
			callback: function(r) {
				var m = frappe.get_module(module_name);
				m.data = r.message.data; 
				frappe.reports.process_data(module_name, m.data);
				//page.section_data[module_name] = m;
			page.main.html(frappe.render_template('modules_section', m));
	//$(frappe.render_template('reports'),{m}).appendTo(me.page.main);
			},
			freeze: true,
		});
	},

	process_data: function(module_name, data) {
		//frappe.module_links[module_name] = [];
		data.forEach(function(section) {
			section.items.forEach(function(item) {
				item.style = '';
				if(item.type==="doctype") {
					item.doctype = item.name;

					// map of doctypes that belong to a module
					//frappe.module_links[module_name].push(item.name);
				}
				if(!item.route) {
					if(item.link) {
						item.route=strip(item.link, "#");
					}
					else if(item.type==="doctype") {
						if(frappe.model.is_single(item.doctype)) {
							item.route = 'Form/' + item.doctype;
						} else {
							if (item.filters) {
								frappe.route_options=item.filters;
							}
							item.route="List/" + item.doctype;
							//item.style = 'font-weight: 500;';
						}
						// item.style = 'font-weight: bold;';
					}
					else if(item.type==="report" && item.is_query_report) {
						item.route="query-report/" + item.name;
					}
					else if(item.type==="report") {
						item.route="Report/" + item.doctype + "/" + item.name;
					}
					else if(item.type==="page") {
						item.route=item.name;
					}
				}

				if(item.route_options) {
					item.route += "?" + $.map(item.route_options, function(value, key) {
						return encodeURIComponent(key) + "=" + encodeURIComponent(value); }).join('&');
				}

				if(item.type==="page" || item.type==="help" || item.type==="report" ||
				(item.doctype && frappe.model.can_read(item.doctype))) {
					item.shown = true;
				}
			});
		});
	}


}

