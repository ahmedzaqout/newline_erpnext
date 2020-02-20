frappe.listview_settings['Work Shifts Management'] = {
	add_fields: ["start_hour", "end_hour", "employee","hours"],
	//gantt_view_mode: 'Quarter Day',
	//view_mode: 'Quarter Day',
	//filters: [["day", "=",__( ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Saturday"][new Date().getDay()]) ]],
//["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
	gantt_view_mode: 'Quarter Day',
	gantt_on_date_change: function(task, start, end) {
	     // if(!me.can_write()) return;
		//me.update_gantt_task(task, start, end);
		console.log(task);
		var field_map = frappe.views.calendar[this.doctype].field_map;
		frappe.call({
			method: 'frappe.desk.gantt.update_task',
			args: {
				args: {
					doctype: task.doctype,
					name: task.id,
					start: start,
					end: end
				},
				field_map: field_map
			},
			callback: function() {
				//me.gantt.updating_task = false;
				frappe.show_alert({message:__("Saved"), indicator: 'green'}, 1);
			}
		});
		},
	gantt_custom_popup_html: function(ganttobj, task) {
		var html = `<h5><a style="text-decoration:underline"\
			href="#Form/Work Shifts Management/${ganttobj.id}""> ${task.employee_name} </a></h5>`;

		if(task.employee) html += `<p>Employee: ${task.employee}</p>`;
		html += `<p>Shift: ${task.hours}</p>`;
		html += `<img src=${task.image} style="width: 2%;">`;
		html += `<p ${task.day}</p>`;

		if(task._assign_list) {
			html += task._assign_list.reduce(
				(html, user) => html + frappe.avatar(user)
			, '');
		}

		return html;
	},
	onload: function(listview) {
		//console.log(new Date().getDay())
//console.log(["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Saturday"][new Date().getDay()])
		
		frappe.call({
		method: 'erpnext.hr.doctype.work_shifts_management.work_shifts_management.get_curday',
		callback: function(r) {
				//var day = cur_list.page.fields_dict.day;
				//day.df.default = r.message;
				//day.refresh();
				//day.set_input(day.df.default);
				frappe.route_options = {
				"day": r.message
				};
				listview.refresh();
				console.log(cur_list);


			}
		});

		frappe.call({
		method: 'erpnext.hr.doctype.work_shifts_management.work_shifts_management.get_shifts',
		callback: function(r) {
			//console.log(r);
			}
		});
	},




};
