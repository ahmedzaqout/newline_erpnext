var data={};
frappe.pages['hr-structure'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Administrative Structure',
		single_column: true
	});

    wrapper.page.add_menu_item(__('Refresh'), function() {
	frappe.hr_structure.make(page);

    });
    wrapper.page.add_menu_item(__('Print'), function() {
		var tree = $(".tree:visible").html();
		var me = this;
		frappe.ui.get_print_settings(false, function(print_settings) {
			var title =  __('Administrative Structure');
			frappe.render_tree({title: title, tree: tree, print_settings:print_settings});
		});


    });
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
		                   data = r.message;
				  
	var ajaxURLs = {
    'children': '/orgchart/children/',
    'parent': '/orgchart/parent/',
    'siblings': function (nodeData) {
        return '/orgchart/siblings/' + nodeData.id;
    },
    'families': function (nodeData) {
        return '/orgchart/families/' + nodeData.id;
    }
};

    var getId = function() {
      return (new Date().getTime()) * 1000 + Math.floor(Math.random() * 1001);
    };

	var oc = $('#chart-container').orgchart({
      'data' : data,
      'ajaxURL': ajaxURLs,
      'depth': 2,
      'nodeTitle': 'name',
      'nodeContent': 'title',
      'parentNodeSymbol': 'fa-th-large',
      'draggable': true,
      'dropCriteria': function($draggedNode, $dragZone, $dropZone) {
        if($draggedNode.find('.content').text().indexOf('manager') > -1 && $dropZone.find('.content').text().indexOf('engineer') > -1) {
          return false;
        }
        return true;
      }, 
      'createNode': function($node, data) {
        var secondMenuIcon = $('<i>', {
          'class': 'fa fa-info-circle second-menu-icon',
          click: function() {
            $(this).siblings('.second-menu').toggle();
          }
        });
        var secondMenu = '<div class="second-menu"><img class="avatar" src="/assets/frappe/images/default-avatar.png"></div>';
        $node.append(secondMenuIcon).append(secondMenu);
        $node.append("<div class='org-add-button'>Add</div><div class='org-del-button'></div>");
	$node[0].id = getId();
//console.log($node);
      }
    });


    oc.$chart.on('nodedrop.orgchart', function(event, extraParams) {
      console.log('draggedNode:' + extraParams.draggedNode.children('.title').text()
        + ', dragZone:' + extraParams.dragZone.children('.title').text()
        + ', dropZone:' + extraParams.dropZone.children('.title').text()
      );
    });


      oc.$chart.find('.org-add-button').on('click', function($node) {
      var $chartContainer = $('#chart-container');
         // var $node = oc.$chart.find('.node.focused');
	 // var nodeIsSelected = oc.$chart.find('.node.focused')?true:false;
		
		//console.log($node.find('.node.focused'));
		console.log($chartContainer.find('.node.focused')[0]);

       });

   
      oc.$chart.find('.org-del-button').on('click', function() {
        var nodeIsSelected = oc.$chart.hasClass('.node.focused');
          var $node = $('.node focused');
		console.log($node);
       });


          var hierarchy = oc.getHierarchy();
	  //console.log(hierarchy);

				}

			}
		});



	}


}
