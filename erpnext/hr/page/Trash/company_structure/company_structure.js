//  function myRequire_CS( url ) {
//     var ajax = new XMLHttpRequest();
//     ajax.open( 'GET', url, false ); // <-- the 'false' makes it synchronous
//     ajax.onreadystatechange = function () {
//         var script = ajax.response || ajax.responseText;
//         if (ajax.readyState === 4) {
//             switch( ajax.status) {
//                 case 200:
//                     eval.apply( window, [script] );
//                     //console.log("script loaded: ", url);
//                     break;
//                 default:
//                    // console.log("ERROR: script not loaded: ", url);
//             }
//         }
//     };
//     ajax.send(null);
// }
// myRequire_CS('/assets/newlinetheme2/js/zoom/jquery.mousewheel.min.js');



var data={};
var selected_node='';
var level;
var nodename;
var selected_node_content='';

frappe.pages['company-structure'].on_page_load = function(wrapper) {


	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Administrative Structure'),
		single_column: true
	});

    wrapper.page.add_menu_item(__('Refresh'), function() {
	frappe.hr_structure.make(page);

    });
    //wrapper.page.add_menu_item(__('Print'), function() {
	//	var tree = $(".tree:visible").html();
	//	var me = this;
	//	frappe.ui.get_print_settings(false, function(print_settings) {
	//		var title =  __('Administrative Structure');
	//		frappe.render_tree({title: title, tree: tree, print_settings:print_settings});
	//	});


    //});
	frappe.hr_structure.make(page);

}

frappe.hr_structure = {
	make: function(page) {
		var me = frappe.hr_structure;
		me.page = page.main.html(frappe.render_template("drag-drop", {}));

		frappe.call({
			method: "erpnext.hr.page.hr_structure.hr_structure.get_tree_nodes",
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
      'parentNodeSymbol': 'fa-th-large',
      'draggable': true,
      'dropCriteria': function($draggedNode, $dragZone, $dropZone) {
	  level=$draggedNode.find('.level').text(); //console.log($dropZone.find('.level').text())
        //if($draggedNode.find('.content').text().indexOf('manager') > -1 && $dropZone.find('.content').text().indexOf('engineer') > -1) {
         // return false;}
 	  if($draggedNode.find('.level').text()!='6' && $dropZone.find('.level').text()!='5') {
          return false;}

        if($draggedNode.find('.level').text() =='6' && $dropZone.find('.level').text() =='5') {
		return true;}
  }, 
  'createNode': function($node, data) {
        var secondMenuIcon = $('<i>', {
          'class': 'fa fa-info-circle second-menu-icon',
          click: function() {
            $(this).siblings('.second-menu').toggle();
          }
	});
//console.log(data.title);
	////////AVATAR

if(data.title!='undefined'){
frappe.call({
			method: "erpnext.hr.page.hr_structure.hr_structure.get_emp_user",
			args:{
				'emp':data.title
			      },
			callback: function(r) {	
    		var secondMenu;			
    				if (r.message) {
    		                   user_id = r.message;
    			console.log(user_id);

           // secondMenu ='<div><img class="avatar" src="'+frappe.avatar(user_id)+'"></div>';
    			 secondMenu ='<div>'+frappe.avatar(user_id)+'</div>';
         
    			}
    			else  secondMenu = '<div><img class="avatar" src="/assets/frappe/images/default-avatar.png"></div>';

    			$node.find('.content').prepend(secondMenu);
      }
});
	
}
        //$node.append(secondMenuIcon).append(secondMenu);
       // $node.append("<div class='org-add-button' style='display:none;'>Add</div><div class='org-del-button' style='display:none;'></div>");
$node.append("<div class='level' style='display:none'>"+data.level+"</div>");
$node[0].id = getId();
//console.log($node);
      }
    });



    oc.$chart.on('nodedrop.orgchart', function(event, extraParams) {console.log(event)
      console.log('draggedNode:' + extraParams.draggedNode.children('.title').text()
        + ', dragZone:' + extraParams.dragZone.children('.title').text()
        + ', dropZone:' + extraParams.dropZone.children('.title').text()
      );
	var dragged = extraParams.draggedNode.children('.title').text();
	var dropped = extraParams.dropZone.children('.title').text();
	var dragged1 = extraParams.draggedNode.children('.content').text();
	frappe.confirm(__('Are you sure you want to change the department of the Employee? GO TO here profile <a href="#Form/Employee/{0}" > {1} </a>',[dragged1.trim(),dragged]), function () {
	frappe.call({
			method: "erpnext.hr.page.hr_structure.hr_structure.drag_drop_node",
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

	function () {return false;});
    });


//////////////

 oc.$chart.on('click', '.node', function(data) {
      var $this = $(this);
      $('#selected-node').val($this.find('.title').text()).data('node', $this);
	 selected_node=$this.find('.title').text();
	selected_node_content =$this.find('.content').text();
	 level=$this.find('.level').text();
	//console.log(level);
    });

 oc.$chart.on('dblclick', '.node', function() {
      var $this = $(this);
	 selected_node=$this.find('.title').text();
	 console.log($this.find('.content').text())
	//level???////////////////////////////////////////
	if(level=='1'){frappe.set_route("Form", 'Headquarter', selected_node); location.reload();}
	if(level=='2'){frappe.set_route("Form", 'Branch', selected_node);location.reload();}
	if(level=='3'){frappe.set_route("Form", 'Management', selected_node);location.reload();}
	if(level=='4'){frappe.set_route("Form", 'Circle', selected_node);location.reload();}
	if(level=='5'){frappe.set_route("Form", 'Department', selected_node);location.reload();}
	if(level=='6'){frappe.set_route("Form", 'Employee', $this.find('.content').text());location.reload();}
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
        msgprint(__('Please input value for new node'));
        return;
      }
      var nodeType = $('input[name="node-type"]:checked');//console.log(nodeType)
      if (!nodeType.length) {
        //alert('Please select a node type');
       // return;
      }
      if (nodeType.val() !== 'parent' && !$('.orgchart').length) {
        msgprint(__('Please creat the root node firstly when you want to build up the orgchart from the scratch'));
        return;
      }
      if (nodeType.val() !== 'parent' && !$node) {
       	msgprint(__("Please select one node in orgchart"));
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

//frappe.hr_structure.make(page);

/////////////// 
          var hierarchy = oc.getHierarchy();
	var nodeid=getId();
var tree = JSON.stringify(hierarchy, null, 2);
frappe.call({
			method: "erpnext.hr.page.hr_structure.hr_structure.save_tree_nodes",
			args:{
				'parent': selected_node,
				'nodeid': nodeid,
				'nodename': nodename,
				'level': level
			      },
			callback: function(r) {				
				if (r.message) {
		                   data = r.message;
	msgprint(__("Added Successfully"));
frappe.hr_structure.make(page);

			console.log(data);
}}
});


            
    });

    $('#btn-delete-nodes').on('click', function() {
      var $node = $('#selected-node').data('node');
      if (!$node) {
       	msgprint(__("Please select one node in orgchart"));
        return;
      } else if ($node[0] === $('.orgchart').find('.node:first')[0]) {
	frappe.confirm(__('Are you sure you want to delete the whole chart?'), function () {
        //if (!window.confirm('Are you sure you want to delete the whole chart?')) {
          return;
        //}
});
      }
//console.log(selected_node);
//console.log(level);

	var node= selected_node;
	frappe.confirm(__('Are you sure you want to delete {0} from the chart?',[node]), function () {
//if (!window.confirm('Are you sure you want to delete '+node+' from the chart?')) {
          	//return false;}

	if(level=='6') node= selected_node_content;
	frappe.call({
			method: "erpnext.hr.page.hr_structure.hr_structure.delete_node",
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
	  //console.log(hierarchy);

				}

			}
		});



	}


}










$(document).ready(function(){
  setTimeout(function(){
    var scale = 1;
        $('.orgchart').bind('wheel mousewheel', function(e){



          var delta;

          if (e.originalEvent.wheelDelta !== undefined)
              delta = e.originalEvent.wheelDelta;
          else
              delta = e.originalEvent.deltaY * -1;
              if(delta > 0) {
                  // $(".orgchart").css("width", "+=10");
                  // $(".orgchart").css("height", "+=10");
                  scale = scale + 0.5;
                  //console.log("m1:"+scale);
                  if(scale > 0){
                    $(".orgchart").css("transform", "scale("+scale+")");
                  }
              }
              else{
                  // $(".orgchart").css("width", "-=10");
                  // $(".orgchart").css("height", "-=10");
                  scale = scale - 0.5;
                  //console.log("m2:"+scale);
                  if(scale > 0){
                    $(".orgchart").css("transform", "scale("+scale+")");
                  }
              }
          });

    }, 3000);
    

    });




// $(document).ready(function () {
//     console.log("mones2");
//     console.log($("#edit-panel"));
//     $("#edit-panel").draggable();
// });
