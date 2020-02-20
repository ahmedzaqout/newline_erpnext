frappe.listview_settings['Attendance'] = {
	add_fields: ["status", "attendance_date"],
	filters: [["discount_salary_from_leaves","=", "0"]],
	get_indicator: function(doc) {
		return [__(doc.status), doc.status=="Present" ? "green" : "darkgrey", "status,=," + doc.status];
	}
};
