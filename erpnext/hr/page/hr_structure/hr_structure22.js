frappe.pages['hr-structure'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Administrative Structure',
		single_column: true
	});
	frappe.hr_structure.make(page);
}

frappe.hr_structure = {
	start: 0,
	make: function(page) {
		var me = frappe.hr_structure;
		me.page = page;
		me.body = $('<div class="dropzone">HEAD</div>').appendTo(me.page.main);
		me.more = $('<div class="for-more" id="draggable" draggable="true" ondragstart="event.dataTransfer.setData("text/plain",null)"><button class="btn btn-sm btn-default btn-more">'
			+ __("More") + '</button></div>').appendTo(me.page.main)
			.find('.btn-more').on('drag', function() {
				$('<div class="for-more"><button class="btn btn-sm btn-default btn-more">'
			+ __("MAYSAA") + '</button></div>').appendTo(me.page.main)
			});
		me.start += 5;
	}
}
