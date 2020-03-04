// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Payroll"] = {
	"filters": [
		
	],

	"onload": function() {
	
		
	},
	
	"formatter":function (row, cell, value, columnDef, dataContext, default_formatter) {
			value = default_formatter(row, cell, value, columnDef, dataContext);

			//console.log(value)
			
			//'<input type="text">'

			//$('div.slick-cell.l17.r17.active.selected >input')[0].value
		if (columnDef.field=="10")
	          	 value += "<input type='text' style='border: none;background-color: inherit;' value='"+value+"'>" ;



	            //value = "<span style='background-color:#ffdfa4!important;font-weight:bold'>" + value + "</span>";
		    //var view_data = frappe.slickgrid_tools.get_view_data(me.columns, me.dataView);
//console.log(view_data)

//dataView= frappe.cur_grid_report;
//dataView.getItemMetadata = metadata(dataView.getItemMetadata);

			if (dataContext.AttendanceDate=='12-02-2018') {
var $span = $("<span></span>")
			.css("background-color","#ffdfa4")
			.html(value);
		if (dataContext[me.name_field]) {
			$('<span class="toggle"></span>')
				.addClass(dataContext._collapsed ? "expand" : "collapse")
				.css("margin-right", "7px")
				.prependTo($span);
		}

		return $span.wrap("<p></p>").parent().html();
		}
			return value;

	}
};

console.log($('div.slick-cell.l17.r17.active.selected >input').val());
$('div.slick-cell.l17.r17.active.selected >input').on('change', function() {
			console.log('yessss');});
