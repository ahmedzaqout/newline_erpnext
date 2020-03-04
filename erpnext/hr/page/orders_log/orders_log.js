frappe.pages['orders-log'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Orders Log'),
		single_column: true
	});
	frappe.orders_log.make(page);
}


frappe.orders_log = {
	make: function(page) {
		var me = frappe.orders_log;
		me.page = page;

		frappe.call({
		     method: "erpnext.hr.page.orders_log.orders_log.get_data",
		     args: {'user':frappe.session.user},
		     callback: function(r) { console.log(r);
			edit_time_orders = r.message[0];
			timesheet = r.message[1];
			permission_orders = r.message[2];
			leave_orders = r.message[3];


		$(frappe.render_template('orders_log'),{'edit_time_orders':edit_time_orders,'timesheet':timesheet,'permission_orders':permission_orders,'leave_orders':leave_orders}).appendTo(me.page.main);

			}
		});


	}

}
