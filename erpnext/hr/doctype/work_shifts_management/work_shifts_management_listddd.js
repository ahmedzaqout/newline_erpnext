frappe.listview_settings['Work Shifts Management'] = {

	gantt_custom_popup_html: function(ganttobj, task) {
		var html = `<h5><a style="text-decoration:underline"\
			href="#Form/Work Shifts Management/${ganttobj.id}""> ${ganttobj.name} </a></h5>`;

		if(task.name) html += `<p>Project: ${task.name}</p>`;
		html += `<p>Progress: ${ganttobj.progress}</p>`;

		if(task._assign_list) {
			html += task._assign_list.reduce(
				(html, user) => html + frappe.avatar(user)
			, '');
		}

		return html;
	}

};
