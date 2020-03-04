

frappe.pages['organizational-struc'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Organizational Structure'),
		single_column: true
	});

    wrapper.page.add_menu_item(__('Refresh'), function() {
	frappe.organizational_struc.make(page);

    });

	frappe.organizational_struc.make(page);
}

frappe.organizational_struc = {
	make: function(page) {
		var me = frappe.organizational_struc;
		me.page = page.main.html(frappe.render_template("organizational_struc", {}));

		frappe.call({
			method: "erpnext.hr.page.organizational_struc.organizational_struc.get_tree_nodes",
			callback: function(r) {				
				if (r.message) {
		                   data = r.message;//console.log(data);
				  

    var getId = function() {
      return (new Date().getTime()) * 1000 + Math.floor(Math.random() * 1001);
    };

	  var oc = $('#chart-container').orgchart({
      'data' : data,
      'nodeContent': 'title',
      'nodeID': 'id',
      'pan': true,
      'zoom': true,
      'parentNodeSymbol': 'fa-th-large',
      'draggable': true,
      'dropCriteria': function($draggedNode, $dragZone, $dropZone) {
	  level=$draggedNode.find('.level').text(); 
 	//if($draggedNode.find('.content').text().indexOf('manager') > -1 && $dropZone.find('.content').text().indexOf('engineer') > -1) {
         // return false;}
	//return true;
	
	  var levels=$draggedNode.find('.levels').text();
	
  
		if(levels == 5 && level ==6 && $dropZone.find('.level').text() ==5)
			return true; 

		else if( levels == 6 && level ==7 || $dropZone.find('.level').text() == 6)
			return true;
		else if(levels == 7 && level ==8 || $dropZone.find('.level').text() ==7) 
			return true;
		else return false;
		console.log(levels+ " " +level +" "+ $dropZone.find('.level').text() );

  }, 
  'createNode': function($node, data) {
        var secondMenuIcon = $('<i>', {
          'class': 'fa fa-info-circle second-menu-icon',
          click: function() {
            $(this).siblings('.second-menu').toggle();
          }
	});

	////////AVATAR


	var img='default-avatar.png';
	if (data.level== '1') img='blue-avatar.png';
	if (data.level== '2') img='pink-avatar.png';
	if (data.level== '3') img='yallow-avatar.png';
	if (data.level== '4') img='green-avatar.png';
	if (data.level== '5') img='pink-avatar.png';

if(data.title!='undefined'){
frappe.call({
			method: "erpnext.hr.page.organizational_struc.organizational_struc.get_emp_user",
			args:{
				'emp':data.title
			      },
			callback: function(r) {	
    		var secondMenu;			
    				if (r.message) {
    		                   user_id = r.message;
    			console.log(user_id);

    			 secondMenu ='<div>'+frappe.avatar(user_id)+'</div>';
         
    			}
    			else  secondMenu = '<div><img class="avatar" src="/assets/newlinetheme2/images/'+img+'"></div>';

    			$node.find('.content').prepend(secondMenu);
      }
});
	
}

$node.append("<div class='level' style='display:none'>"+data.level+"</div>");
frappe.db.get_value('Administrative Structure Categories', null, 'levels', (r) => {
 		 levels = r.levels;
$node.append("<div class='levels' style='display:none'>"+levels+"</div>");
$node.find('.content').append('<a id="add_btn" class="pr-10 btn btn-icon-anim btn-square btn-sm" data-toggle="tooltip" title="" data-original-title="add" style="margin-left: 100px; color: #999999bf;"><i class="octicon octicon-plus" style="font-weight: bold;" ></i></a>\
<a id="del_btn" class="pr-10 btn btn-icon-anim btn-square btn-sm" data-toggle="tooltip" title="" data-original-title="delete" style="color: #999999bf;"><i class="octicon octicon-x" style="font-weight: bold;"></i></a>');
});
$node[0].id = getId();
      }
    });



    oc.$chart.on('nodedrop.orgchart', function(event, extraParams) {console.log(event)
     // console.log('draggedNode:' + extraParams.draggedNode.children('.title').text()
       // + ', dragZone:' + extraParams.dragZone.children('.title').text()
        //+ ', dropZone:' + extraParams.dropZone.children('.title').text()
      //);
	var dragged = extraParams.draggedNode.children('.title').text();
	var dropped = extraParams.dropZone.children('.title').text();
	var dragged1 = extraParams.draggedNode.children('.content').text();
	frappe.confirm(__('Are you sure you want to change the department of the Employee? GO TO here profile <a href="#Form/Employee/{0}" > {1} </a>',[dragged1.trim(),dragged]), function () {
	frappe.call({
			method: "erpnext.hr.page.organizational_struc.organizational_struc.drag_drop_node",
			args:{
				'dragged':dragged1,
				'dropped': dropped,
				'level': level
			      },
			callback: function(r) {				
				if (r.message) {
		                   data = r.message;
			console.log(data);
			}}
		});
},

	function () {location.reload();;return false;});
    });


//////////////
oc.$chart.on('click', '#add_btn', function(data) {

 	var selected_node = $('.orgchart').find('.focused').find('.title').text();

	var d = new frappe.ui.Dialog({
    		'fields': [
		{fieldtype:'Link', fieldname:'node_name', label:__('Employee'), reqd:true, options:"Employee",description: __("Name of new Node")},
		{fieldtype:'Link', fieldname:'director', label:__('Director Name'), options:"Employee"},
		{fieldtype:'Data', fieldname:'parent_name', label:__('Parent Node Name'),read_only:true}
       	
   			 ],
		 primary_action_label: __('Add'),
   		 primary_action: function(){
			 // console.log(d.get_values());
      var $chartContainer = $('#chart-container');
			var nodename = d.get_value('node_name');
			var director = d.get_value('director');
			var nodeType = 'parent';

///////////////////////////
	if (!$('.orgchart').length) {
        	frappe.msgprint(__('Please creat the root node firstly when you want to build up the orgchart from the scratch'));
        	return;
      	}
        if (!selected_node) {
       		frappe.msgprint(__("Please select one node in orgchart"));
        return;
      }
      if (nodeType === 'parent') {
        if (!$chartContainer.children('.orgchart').length) {// if the original chart has been deleted
          oc = $chartContainer.orgchart({
            'data' : { 'name': nodename },
            'exportButton': true,
            'exportFilename': 'SportsChart',
            'parentNodeSymbol': 'fa-th-large',
            'createNode': function($node, data) {
              $node[0].id = getId();

            }
          });
          oc.$chart.addClass('view-state');
        } else {
          oc.addParent($chartContainer.find('.node:first'), { 'name': nodename, 'id': getId() });
        }
      } else if (nodeType === 'siblings') {
        if ($node[0].id === oc.$chart.find('.node:first')[0].id) {
          alert('You are not allowed to directly add sibling nodes to root node');
          return;
        }
        oc.addSiblings($node, nodeVals.map(function (item) {
            return { 'name': item, 'relationship': '110', 'id': getId() };
          }));
      } else {
        var hasChild = $node.parent().attr('colspan') > 0 ? true : false;
        if (!hasChild) {
          var rel = nodeVals.length > 1 ? '110' : '100';
          oc.addChildren($node, nodeVals.map(function (item) {
              return { 'name': item, 'relationship': rel, 'id': getId() };
            }));
        } else {
          oc.addSiblings($node.closest('tr').siblings('.nodes').find('.node:first'), nodeVals.map(function (item) {
              return { 'name': item, 'relationship': '110', 'id': getId() };
            }));
        }
      }
frappe.msgprint(__("Waiting .."));
//frappe.hr_structure.make(page);

/////////////// 
          var hierarchy = oc.getHierarchy();
	var nodeid=getId(); //console.log(nodeid);
var tree = JSON.stringify(hierarchy, null, 2);
frappe.call({
			method: "erpnext.hr.page.organizational_struc.organizational_struc.save_tree_nodes",
			args:{
				'parent': selected_node,
				'nodeid': nodeid,
				'nodename': nodename,
				'director':director,
				'level': level
			      },
			callback: function(r) {				
				if (r.message) {
		                   data = r.message;
				   frappe.msgprint(__("Added Successfully"));
					frappe.organizational_struc.make(page);
					}	
				}

	}); 

/////////////////////////////////////////
      			  d.hide();

    			}
	}); 


	//d.fields_dict.parent_name.$input = selected_node;
	d.set_value('parent_name',selected_node);
	d.show();

      

    });

 oc.$chart.on('click', '.node', function(data) {
      var $this = $(this);
      $('#selected-node').val($this.find('.title').text()).data('node', $this);
	 selected_node=$this.find('.title').text();
	selected_node_content =$this.find('.content').text();
	 level=$this.find('.level').text();
    });

 oc.$chart.on('dblclick', '.node', function() {
      var $this = $(this);
	 selected_node=$this.find('.title').text();
	 var levels=$this.find('.levels').text();
	 //console.log($this.find('.content').text())

	if(level=='1'){
		frappe.db.get_value('Headquarter', selected_node, 'director', (r) => {
 			frappe.set_route("Form", 'Employee', r.director );location.reload();  }); }
	if(level=='2'){
		frappe.db.get_value('Branch', selected_node, 'director', (r) => {
 			frappe.set_route("Form", 'Employee', r.director );location.reload();  }); }

	if(level=='3'){
		frappe.db.get_value('Management', selected_node, 'director', (r) => {
 			frappe.set_route("Form", 'Employee', r.director );location.reload();  }); }

	if(level=='4'){
		frappe.db.get_value('Circle', selected_node, 'director', (r) => {
 			frappe.set_route("Form", 'Employee', r.director );location.reload();  }); }

	if(level=='5'){
		frappe.db.get_value('Department', selected_node, 'director', (r) => {
 			frappe.set_route("Form", 'Employee', r.director );location.reload();  }); }
		
	//if(level=='6'){frappe.set_route("Form", 'Employee', $this.find('.content').text());location.reload();}

	if(levels == '6' && level=='6'){
		frappe.db.get_value('Sub Department', selected_node, 'director', (r) => {
 			frappe.set_route("Form", 'Employee', r.director );location.reload();  }); }
	if(levels == '7' && level=='6'){
		frappe.db.get_value('Sub Department', selected_node, 'director', (r) => {
 			frappe.set_route("Form", 'Employee', r.director );location.reload();  }); }
	if(levels == '7' && level=='7'){
		frappe.db.get_value('Sub Association', selected_node, 'director', (r) => {
 			frappe.set_route("Form", 'Employee', r.director );location.reload();  }); }

	if(levels == '5' && level=='6'){frappe.set_route("Form", 'Employee', $this.find('.content').text());location.reload();}
	if(levels == '6' && level=='7'){frappe.set_route("Form", 'Employee', $this.find('.content').text());location.reload();}
	if(levels == '7' && level=='8'){frappe.set_route("Form", 'Employee', $this.find('.content').text());location.reload();}

    });


    oc.$chart.on('click', '.orgchart', function(event) {
      if (!$(event.target).closest('.node').length) {
        $('#selected-node').val('');
      }
    });


  $('input[name="chart-state"]').on('click', function() {
      $('.orgchart').toggleClass('edit-state', this.value !== 'view');
      $('#edit-panel').toggleClass('edit-state', this.value === 'view');
      if ($(this).val() === 'edit') {
        $('.orgchart').find('tr').removeClass('hidden')
          .find('td').removeClass('hidden')
          .find('.node').removeClass('slide-up slide-down slide-right slide-left');
      } else {
        $('#btn-reset').trigger('click');
      }
    });

    $('input[name="node-type"]').on('click', function() {
      var $this = $(this);
      if ($this.val() === 'parent') {
        $('#edit-panel').addClass('edit-parent-node');
        $('#new-nodelist').children(':gt(0)').remove();
      } else {
        $('#edit-panel').removeClass('edit-parent-node');
      }
    });

    $('#btn-add-input').on('click', function() {
      $('#new-nodelist').append('<li><input type="text" class="new-node"></li>');
    });

    $('#btn-remove-input').on('click', function() {
      var inputs = $('#new-nodelist').children('li');
      if (inputs.length > 1) {
        inputs.last().remove();
      }
    });


 $('#btn-add-nodes').on('click', function() {
      var $chartContainer = $('#chart-container');
      var nodeVals = [];
      $('#new-nodelist').find('.new-node').each(function(index, item) {
        var validVal = item.value.trim();
        if (validVal.length) {
          nodeVals.push(validVal);
        }
      });nodename=nodeVals[0];
      var $node = $('#selected-node').data('node');//console.log($node)

      if (!nodeVals.length) {
        frappe.msgprint(__('Please input value for new node'));
        return;
      }
      var nodeType = $('input[name="node-type"]:checked');//console.log(nodeType)
      if (!nodeType.length) {
        //alert('Please select a node type');
       // return;
      }
      if (nodeType.val() !== 'parent' && !$('.orgchart').length) {
       frappe. msgprint(__('Please creat the root node firstly when you want to build up the orgchart from the scratch'));
        return;
      }
      if (nodeType.val() !== 'parent' && !$node) {
       	frappe.msgprint(__("Please select one node in orgchart"));
        return;
      }
      if (nodeType.val() === 'parent') {
        if (!$chartContainer.children('.orgchart').length) {// if the original chart has been deleted
          oc = $chartContainer.orgchart({
            'data' : { 'name': nodeVals[0] },
            'exportButton': true,
            'exportFilename': 'SportsChart',
            'parentNodeSymbol': 'fa-th-large',
            'createNode': function($node, data) {
              $node[0].id = getId();

            }
          });
          oc.$chart.addClass('view-state');
        } else {
          oc.addParent($chartContainer.find('.node:first'), { 'name': nodeVals[0], 'id': getId() });
        }
      } else if (nodeType.val() === 'siblings') {
        if ($node[0].id === oc.$chart.find('.node:first')[0].id) {
          alert('You are not allowed to directly add sibling nodes to root node');
          return;
        }
        oc.addSiblings($node, nodeVals.map(function (item) {
            return { 'name': item, 'relationship': '110', 'id': getId() };
          }));
      } else {
        var hasChild = $node.parent().attr('colspan') > 0 ? true : false;
        if (!hasChild) {
          var rel = nodeVals.length > 1 ? '110' : '100';
          oc.addChildren($node, nodeVals.map(function (item) {
              return { 'name': item, 'relationship': rel, 'id': getId() };
            }));
        } else {
          oc.addSiblings($node.closest('tr').siblings('.nodes').find('.node:first'), nodeVals.map(function (item) {
              return { 'name': item, 'relationship': '110', 'id': getId() };
            }));
        }
      }
frappe.msgprint(__("Waiting .."));
//frappe.organizational_struc.make(page);

/////////////// 
          var hierarchy = oc.getHierarchy();
	var nodeid=getId();
var tree = JSON.stringify(hierarchy, null, 2);
frappe.call({
			method: "erpnext.hr.page.organizational_struc.organizational_struc.save_tree_nodes",
			args:{
				'parent': selected_node,
				'nodeid': nodeid,
				'nodename': nodename,
				'level': level
			      },
			callback: function(r) {				
				if (r.message) {
		                   data = r.message;
	frappe.msgprint(__("Added Successfully"));
frappe.organizational_struc.make(page);

			console.log(data);
}}
});


            
    });

    //$('#btn-delete-nodes').on('click', function() {
    $('#del_btn').on('click', function() { 
      var $node = $('#selected-node').data('node'); console.log($node);
      if (!$node) {
       	frappe.msgprint(__("Please select one node in orgchart"));
        return;
      } else if ($node[0] === $('.orgchart').find('.node:first')[0]) {
	frappe.confirm(__('Are you sure you want to delete the whole chart?'), function () {
          return;

});
      }

	var node= selected_node;
	frappe.confirm(__('Are you sure you want to delete {0} from the chart?',[node]), function () {

	if(level=='6') node= selected_node_content;
	frappe.call({
			method: "erpnext.hr.page.organizational_struc.organizational_struc.delete_node",
			args:{
				'node': node,
				'level': level
			      },
			callback: function(r) {				
				if (r.message) {
		                   data = r.message;
			           console.log(data);
      			oc.removeNodes($node);
      			$('#selected-node').val('').data('node', null);
	}
}
});
});


    });

    $('#btn-reset').on('click', function() {
      $('.orgchart').find('.focused').removeClass('focused');
      $('#selected-node').val('');
      $('#new-nodelist').find('input:first').val('').parent().siblings().remove();
      $('#node-type-panel').find('input').prop('checked', false);
    });

  

          var hierarchy = oc.getHierarchy();

				}

			}
		});



	}


}
