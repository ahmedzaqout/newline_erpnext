var data={};
var selected_node='';
var level;
var nodename;

frappe.pages['hr-structure'].on_page_load = function(wrapper) {
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
		                   data = r.message;console.log(data);



    var getId = function() {
      return (new Date().getTime()) * 1000 + Math.floor(Math.random() * 1001);
    };

	var oc = $('#chart-container').orgchart({
      'data' : data,
      'ajaxURL': ajaxURLs,
      'depth': 2,
      'nodeContent': 'title',
      'nodeID': 'id',
      'parentNodeSymbol': 'fa-th-large',
      'nodeContent': 'title',
      'draggable': true,
	'dropCriteria': function($draggedNode, $dragZone, $dropZone) {
        if($draggedNode.find('.content').text().indexOf('manager') > -1 && $dropZone.find('.content').text().indexOf('engineer') > -1) {
          return false;
        }
        return true;
      }
    });
	//level=$draggedNode.find('.level').text(); console.log($draggedNode.find('.content').text())
        //if($draggedNode.find('.content').text().indexOf('manager') > -1 && $dropZone.find('.content').text().indexOf('engineer') > -1) {
         // return false;}
 //	if($draggedNode.find('.level').text()!='6') {
   //       return false;}

        //return true;
     // }, 
 'createNode': function($node, data) {
        var secondMenuIcon = $('<i>', {
          'class': 'fa fa-info-circle second-menu-icon',
          click: function() {
            $(this).siblings('.second-menu').toggle();
          }
        });
        var secondMenu = '<div class="second-menu"><img class="avatar" src="/assets/frappe/images/default-avatar.png"></div>';
        $node.append(secondMenuIcon).append(secondMenu);
        $node.append("<div class='org-add-button' style='display:none;'>Add</div><div class='org-del-button' style='display:none;'></div>");
        $node.append("<div class='level' >"+data.level+"</div>");
	$node[0].id = getId();
//console.log($node);
      }
    });


         // $node.on('click', function(event,data) {

		//console.log($(event.target));
//});
        
        //$node.append("<div class='org-add-button' style='display:none'>New</div><div class='org-del-button' style='display:none'></div>");

	//var toolbar = "<div class='tree-node-toolbar btn-group'><button class='btn btn-default btn-xs'>New</button>"+
	//	"<button class='btn btn-default btn-xs'>Edit</button>"+
	//	"<button class='btn btn-default btn-xs'>Delete</button>"+"</span></div>";
       // $node.append(toolbar);

	//$node[0].parentId = getId();

     // }
   // });


    oc.$chart.on('nodedrop.orgchart', function(event, extraParams) {
      console.log('draggedNode:' + extraParams.draggedNode.children('.title').text()
        + ', dragZone:' + extraParams.dragZone.children('.title').text()
        + ', dropZone:' + extraParams.dropZone.children('.title').text()
      );console.log(extraParams);
	var dragged = extraParams.draggedNode.children('.title').text();
	var dropped = extraParams.dropZone.children('.title').text();
	var dragged1 = extraParams.draggedNode.children('.content').text();

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
    });


 //oc.$chart.on('dblclick', '.org-add-button', function() {
    //  var $chartContainer = $('#chart-container');
	//	//console.log(selected_node);

       //});

   
      //oc.$chart.find('.org-del-button').on('click', function() {
       // var nodeIsSelected = oc.$chart.hasClass('.node.focused');
         // var $node = $('.node focused');
		//console.log(selected_node);
      // });

//////////////

 oc.$chart.on('click', '.node', function(data) {
      var $this = $(this);
      $('#selected-node').val($this.find('.title').text()).data('node', $this);
	 selected_node=$this.find('.title').text();
	 level=$this.find('.level').text();
	//console.log(level);
    });

 oc.$chart.on('dblclick', '.node', function() {
      var $this = $(this);
	 selected_node=$this.find('.title').text();
	 console.log($this.find('.content').text())
	//level???////////////////////////////////////////
	if(level=='1')frappe.set_route("Form", 'Headquarter', selected_node);
	if(level=='2')frappe.set_route("Form", 'Branch', selected_node);
	if(level=='3')frappe.set_route("Form", 'Management', selected_node);
	if(level=='4')frappe.set_route("Form", 'Circle', selected_node);
	if(level=='5')frappe.set_route("Form", 'Department', selected_node);
	if(level=='6')frappe.set_route("Form", 'Employee', $this.find('.content').text());
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
        alert('Please input value for new node');
        return;
      }
      var nodeType = $('input[name="node-type"]:checked');//console.log(nodeType)
      if (!nodeType.length) {
        //alert('Please select a node type');
       // return;
      }
      if (nodeType.val() !== 'parent' && !$('.orgchart').length) {
        alert('Please creat the root node firstly when you want to build up the orgchart from the scratch');
        return;
      }
      if (nodeType.val() !== 'parent' && !$node) {
        alert('Please select one node in orgchart');
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

			console.log(data);
}}
});


            
    });

    $('#btn-delete-nodes').on('click', function() {
      var $node = $('#selected-node').data('node');
      if (!$node) {
        frappe.msgprint('Please select one node in orgchart');
        return;
      } else if ($node[0] === $('.orgchart').find('.node:first')[0]) {
        if (!window.confirm('Are you sure you want to delete the whole chart?')) {
          return;
        }
      }
//console.log(selected_node);
//console.log(level);

	frappe.call({
			method: "erpnext.hr.page.hr_structure.hr_structure.delete_node",
			args:{
				'node': selected_node,
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
