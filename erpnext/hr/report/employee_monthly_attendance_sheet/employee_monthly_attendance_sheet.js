// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
var d = new Date();

frappe.query_reports["Employee Monthly Attendance Sheet"] = {
	"filters": [

		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": new Date(d.getFullYear(),d.getMonth(),1),//frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"reqd": 1,
			"read_only": 0,
			on_change: function() {
				var employee = frappe.query_report_filters_by_name.employee.get_value();
				frappe.db.get_value("Employee", employee, "employee_name", function(value) {
					frappe.query_report_filters_by_name.employee_name.set_value(value["employee_name"]);
				});

			}


		},
		{
			"fieldname":"employee_name",
			"label": __("Employee Name"),
			"fieldtype": "Data",
			"read_only":1
		},
	
		{
			"fieldtype": "Break",
		},

		{
			"fieldname":"morning_late",
			"label": __("Morning Late"),
			"default": 1,
			"fieldtype": "Check"
		},
		{
			"fieldname":"overtime",
			"label": __("Overtime"),
			"default": 1,
			"fieldtype": "Check"
		},
	
		
		{
			"fieldname":"ex_per",
			"label": __("Exit Permissions"),
			"default": 1,
			"fieldtype": "Check"
		},
		
		{
			"fieldname":"early_dep",
			"label": __("Early Departure"),
			"default": 1,
			"fieldtype": "Check"
		},
		{
			"fieldname":"disc_hrs",
			"label": __("Discount Hours"),
			"default": 1,
			"fieldtype": "Check"
		},
		{
			"fieldname":"penalty",
			"label": __("Penalty Discount"),
			"default": 1,
			"fieldtype": "Check"
		},

	],

	"onload": function(frm) {
		var employee = frappe.query_report_filters_by_name.employee;
		if(!frappe.user.has_role("HR Manager"))
			employee.df.read_only = 1;
		else
			employee.df.read_only = 0;
		employee.refresh();

		frappe.db.get_value("Employee Personal Detail", {'user_id':frappe.session.user}, "employee", function(value) {
			frappe.query_report_filters_by_name.employee.set_value(value['employee'])
				});

		return  frappe.call({
			method: "erpnext.hr.report.employee_monthly_attendance_sheet.employee_monthly_attendance_sheet.get_attendance_years",
			callback: function(r) {
				var year_filter = frappe.query_report_filters_by_name.year;
				year_filter.df.options = r.message;
				year_filter.df.default = r.message.split("\n")[0];
				year_filter.refresh();
				year_filter.set_input(year_filter.df.default);
			}
		});		

	},
	"formatter":function (row, cell, value, columnDef, dataContext, default_formatter) {
			value = default_formatter(row, cell, value, columnDef, dataContext);
			//if (columnDef.field=="Status")
				//console.log(columnDef.field)

				//console.log(dataContext.الحالة)
	           // value = "<span style='background-color:#ffdfa4!important;font-weight:bold'>" + value + "</span>";
		    //var view_data = frappe.slickgrid_tools.get_view_data(me.columns, me.dataView);
//console.log(view_data)

//dataView= frappe.cur_grid_report;
//dataView.getItemMetadata = metadata(dataView.getItemMetadata);
		//	console.log(dataContext);
			if (columnDef.field==__("Overtime") ){
			if ( dataContext.النوع =='compensatory' || dataContext.Type =='compensatory') 
                                    value = "<span style='color:green;font-weight:bold'>" + value + "</span>";

			if ( dataContext.النوع =='Normal' || dataContext.Type =='Normal') 
                                    value = "<span style='color:blue;font-weight:bold'>" + value + "</span>";
			}
			
			if ( dataContext.الحالة ==__('On Leave') || dataContext.Status ==__('On Leave')) {
				value = "<div style='background-color:#ffdfa4!important;margin: 0px -4px'>" + value + "</div>";
			}
			if ( dataContext.الحالة ==__('On Holiday')|| dataContext.Status ==__('On Holiday')) {
				value = "<div style='background-color:#fd6c6c94!important;margin: 0px -4px'>" +value+ "</div>";
			}
			if ( dataContext.الحالة ==__('Absent')|| dataContext.Status ==__('Absent')) {
				value = "<div style='background-color:#b9ff77a6!important;margin: 0px -4px'>" +value+ "</div>";
			}

			if ( dataContext.يوم =='' || dataContext.Day =='' || dataContext.اليوم =='' ) {
				value = "<div style='background-color:#ffec03c9!important; color: red;font-size: 14px; padding: 2px;font-weight:bold;margin: 0px -4px'>" +value+ "</div>";
			}
			if (columnDef.field==__("Exit Permissions") ){
				var zero_val='0:00:00';
				if ( dataContext.الأذونات != zero_val ) {
                                        value = "<span style='color:#ff8d00;font-weight:bold'>" + value + "</span>";}
			}



			if (columnDef.field==__("Late Hours") ){
				frappe.db.get_value("HR Settings", {name: 'HR Settings'}, "morning_delay", function(value) {
					var morning_delay= parseFloat(value['morning_delay']/60); 							//console.log(timeStringToFloat(dataContext["تأخير صباحي"]) +" "+(morning_delay) );
					if ( timeStringToFloat(dataContext["Late Hours"]) >= morning_delay || timeStringToFloat(dataContext["تأخير صباحي"]) >=morning_delay)    
						value = "<span style='color:red;font-weight:bold'>" + value + "</span>";
				});
			}

			if (dataContext.AttendanceDate=='12-02-2018') {
//var $span = $("<span></span>")
			//.css("background-color","#ffdfa4")
			//.html(value);
		if (dataContext[me.name_field]) {
			//$('<span class="toggle"></span>')
				//.addClass(dataContext._collapsed ? "expand" : "collapse")
				//.css("margin-right", "7px")
				//.prependTo($span);
		}

		return $span.wrap("<p></p>").parent().html();
		}
			return value;

	}
}

function timeStringToFloat(time) {
if (time && time !=''){
  var hoursMinutes = time.split(/[.:]/);
  var hours = parseInt(hoursMinutes[0], 10);
  var minutes = hoursMinutes[1] ? parseInt(hoursMinutes[1], 10) : 0;
  return hours + minutes / 60;
}
else return 0;
}
