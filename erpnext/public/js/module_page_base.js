frappe.module = {
	make: function(page,template) {
		console.log(template);
		var me = frappe.module;
		me.page = page;

		frappe.call({
			method: "frappe.desk.moduleview.get",
			args: {
				module: module_name 
			},
			callback: function(r) { 
				var m = frappe.get_module(module_name);
				m.data = r.message.data;

				frappe.module.process_data(module_name, m.data);

		me.page.main.html(frappe.render_template(template,{"data":m.data} ));

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

