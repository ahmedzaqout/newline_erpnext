frappe.provide('frappe.views');

frappe.pages['work-shifts'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Work Shift'),
		single_column: true
	});

	page.add_field({
		fieldname: 'day',
		label: __('Date'),
		fieldtype:'Date',
		defualt: date.get_today(),
		change: function() {
			frappe.workshifts.day=this.value;
			console.log(frappe.workshifts.day);
			frappe.workshifts.get_data();
			frappe.workshifts.fill_employees();
			frappe.workshifts.fill_absence();	
		}
	});

	page.add_field({
		fieldname: 'department',
		label: __('Department'),
		fieldtype:'Link',
		options:'Department',
		change: function() {
			
		}
	});
	
	page.add_field({
		fieldname: 'branch',
		label: __('Branch'),
		fieldtype:'Link',
		options:'Branch',
		change: function() {
			
		}
	});


	
	wrapper.page.add_menu_item(__('Refresh'), function() {
	this.page=frappe.workshifts.make_page(page);
	frappe.workshifts.saved={};

    });
    wrapper.page.add_menu_item(__('Save'), function() {
    	frappe.workshifts.save();

    });
            
    frappe.workshifts.pp=wrapper.page;
	this.page=frappe.workshifts.make_page(page);
	// wrapper.page.add_date("Date");

}

frappe.workshifts = {
	make_page: function(page) {
		var me = this;
		this.day=null;
		this.employees=null;
		this.branches=null;
		this.departments=null;
		this.designations=null;
		this.saved=[];
		this.absence=null;
		this.get_data()
		
		me.page = page.main.append(frappe.render_template("work_shift", {}));	
	},
	get_data :function()
	{
		me=this;
		frappe.call({
			method: "erpnext.hr.page.work_shifts.work_shift.get_employess",
			freeze:true,
			args: {
				date: me.day
			},
			freeze: true,
			callback: function(r) {
				me.employees=r.message.employee
				console.log(me.employees);

				me.branches=r.message.branches;
				me.departments=r.message.departments;
				me.designations=r.message.designations;
				me.absence=r.message.absence;
				me.fill_employees();
				me.fill_absence();
				
			}
		});
	},
	fill_employees: function(){
		me=this;
		var $wrap = me.page.find(".shifts tbody");
		me.page.find(".shifts tbody").html("");
		
		if (me.employees) {
			$.each(this.employees, function(index, obj) {
				ss=""
				if (obj[2]>0){
				 for (i=0;i<Math.floor(obj[2])-1;i++){
				 	ss+=" <td data-id="+(i+1)+ " id="+obj[8]+(i+1)+" ondrop='drop_handler(event);' ></td> "
				 }

			}
				 rem="";
				 if (Math.floor(obj[2])==0 && Math.floor(obj[3])==0){
				 	 remain=23;
				 }
				 else{

				 remain=Math.floor(24-(Math.floor(obj[2])+Math.floor(obj[3])))+1
				}
				if (Math.floor(obj[2])==0 && Math.floor(obj[3])==0){
				 	 j=2;
				 	}
				else{
				 j=(Math.floor(obj[2])+Math.floor(obj[3]));
				}
				 for (i=0;i<remain;i++){
				 	rem+=" <td data-id="+j+ " id="+obj[8]+j+" ondrop='drop_handler(event);'></td> "
				 	j++;
				 }
				 des=null;
				 if (obj[11]){
				 	des=obj[11].replace(/\s/g, '')
				 } 
				

					
					$(frappe.render_template("work_shift_row", {
						name:obj[8],
						designation:des,
						employee_name: obj[0],
						image: obj[1],
						start: Math.floor(obj[2]),
						period:Math.floor(obj[3]),
						ss:ss,
						color:obj[7],
						remain:rem
					
					})).appendTo($wrap);
			
			});
}

else{
	
	$wrap.append('<tr  style="text-align:center" ><td colspan="25"> No employees found </td></tr>');
}
	},
	fill_absence: function(){
		me=this;
		var $wrap = me.page.find(".absence tbody");
		me.page.find(".absence tbody").html("");
		me.page.find(".absence thead").html("<tr><th>Absence</th></tr>");
		
			console.log(me.absence);

		if (me.absence) {
			$.each(this.absence, function(index, obj) {
				des=null;
				if(obj[5]){
					des=obj[5].replace(/\s/g, '');
				}
				console.log(obj[2]);
					$(frappe.render_template("work", {
						employee_name: obj[0],
						image: obj[2],
						designation:des
					})).appendTo($wrap);
			
			});
		// this.make_filters()
		

}
else{
	$wrap.append('<tr style="text-align:center"><td > No absence for today </td></tr>');

}
	},
	save: function() {
		me=this;
		

		frappe.call({
			method: "erpnext.hr.page.work_shifts.work_shift.save_shifts",
			freeze:true,
			args: {
				shifts: me.saved,
				date: me.day
			},
			freeze: true,
			callback: function(r) {
				console.log(r.message);
			}
		});

			
	}
	
}

//   $(document).ready(function(){{
//     $( "#draggable" ).draggable();
//   } 

// }) ;$("#branch").onChange(function(){
// function branch_sel(ev) {
// 	// body...

// 	alert("D");
// }
// function department_sel(ev){
// 	$(ev).val();
// }



// $( function() {
//     $( ".resizable" ).resizable();
//   } );


    
function drag(ev) {

    ev.dataTransfer.setData("text", ev.target.id);
    console.log( ev.dataTransfer.getData("text"));
}

function drop_handler(ev) {
	ev.preventDefault();
 	// Get the id of the target and add the moved element to the target's DOM
 	var data = ev.dataTransfer.getData("text");
 	console.log(data);

 	var r=document.getElementById(data).parentNode;
 	m=r.getAttribute("colspan"); 
 	parentsrc=ev.target.parentNode;
 	parenttarger=r.parentNode;
  	if(parentsrc==parenttarger){



 	start=r.getAttribute("data-id");  
 	iddd=r.getAttribute("id");
 	str = iddd.substring(0, (iddd.length - start.length));

		 for (i=(parseInt(m)-1);i>0;i--){ 
		 $(r).after("<td data-id="+(parseInt(i)+parseInt(start))+ " id="+str+(parseInt(i)+parseInt(start))+" ondrop='drop_handler(event);' ></td>");
	}
	r.setAttribute("colspan",1);
	r.setAttribute("data-id",start);
	tar=ev.target;

	len=parseInt(tar.getAttribute("data-id"));

	xx=len+parseInt(m)-24;
	for (j=0;j<xx-1;j++){
		tar=tar.previousElementSibling;
		if (tar.childNodes.lenght>0)
			tar.childNodes[0].remove;
			console.log(tar);						
}

	console.log(tar);
	tar.appendChild(document.getElementById(data));
	startt=parseInt(tar.getAttribute("data-id"));

 	tar.setAttribute("colspan",m);

 for (i=(parseInt(m)-1);i>0;i--){ 
	tar.nextElementSibling.remove();
  }
  fla=false;
  for (k=0;k< frappe.workshifts.saved.length;k++){
  	if (frappe.workshifts.saved[k]['name']==str){
  		frappe.workshifts.saved[k]={"name": str,"start":startt,"period":m};
  		fla=true;
  	}
}
if (! fla){
		frappe.workshifts.saved.push({"name": str,"start":startt,"period":m});
  }
	}
}

function getDesignation(han){
	console.log(han.parentNode);
	var parent=han.parentNode;
	des=parent.getAttribute("data-designation");

	if (des){
	var t="."+des;
	console.log($(t));

	$('.shifts tr').css( "background-color" ,"#ffffff"); 
	$(t).css('background-color','#f5f7fa');

	}
}

function allowDrop(ev) {
    ev.preventDefault();
}
	document.addEventListener("dragover", function(e){
    	e = e || window.event;
    	var dragX = e.pageX, dragY = e.pageY;

    	console.log("X: "+dragX+" Y: "+dragY);
}, false);
