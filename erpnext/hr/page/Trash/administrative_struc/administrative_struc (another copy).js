frappe.pages['administrative-struc'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Administrative Structure',
        single_column: true
    });


    wrapper.page.add_menu_item(__('Refresh'), function() {
        wrapper.make_tree();

    });
    wrapper.page.add_menu_item(__('Print'), function() {
		var tree = $(".tree:visible").html();
		var me = this;
		frappe.ui.get_print_settings(false, function(print_settings) {
			var title =  __(me.docname || me.doctype);
			frappe.render_tree({title: title, tree: tree, print_settings:print_settings});
		});


    });

    wrapper.make_tree = function() {

        var ctype = frappe.get_route()[1] || 'Department';
        return frappe.call({
            method: 'erpnext.hr.page.administrative_struc.administrative_struc.get_children',
            args: { ctype: ctype },
            callback: function(r) {
               // console.log(r);
                //var root = r.message[0]["value"];
                frappe.tree_chart = new frappe.TreeChart(ctype, 'root', page,
                    page.main.css({
                        "min-height": "300px",
                        "padding-bottom": "25px"
                    }));
 		
            }
        });
    }

    wrapper.make_tree();

this.page.add_inner_button(__('Expand All'), function() {
			me.tree.rootnode.load_all();
		});
		
}

frappe.pages['administrative-struc'].on_page_show = function(wrapper) {
    // set route
    var ctype = frappe.get_route()[1] || 'Department';

    wrapper.page.set_title(__('Administrative Structure'));


    if (frappe.tree_chart && frappe.tree_chart.ctype != ctype) {
        wrapper.make_tree();
    }

    frappe.breadcrumbs.add(frappe.breadcrumbs.last_module || "Administrative Structure");
    
};

frappe.TreeChart = Class.extend({
    init: function(ctype, root, page, parent) {
        $(parent).empty();
        var me = this;
        me.ctype = ctype;
        me.page = page;
        me.can_read = frappe.model.can_read(this.ctype);
        me.can_create = frappe.boot.user.can_create.indexOf(this.ctype) !== -1 ||
            frappe.boot.user.in_create.indexOf(this.ctype) !== -1;
        me.can_write = frappe.model.can_write(this.ctype);
        me.can_delete = frappe.model.can_delete(this.ctype);

        me.page.set_primary_action(__("New"), function() {
            me.new_node();
        }, "octicon octicon-plus");

        this.tree = new frappe.ui.Tree({
            parent: $(parent),
            label: __('root'),
            args: { ctype: ctype },
            method: 'erpnext.hr.page.administrative_struc.administrative_struc.get_children',
            toolbar: [
                { toggle_btn: true },
                {
                    label: __("Edit"),
                    condition: function(node) {
                        return !node.root && me.can_read;
                    },
                    click: function(node) {
			//console.log(parent);			console.log(me)
                        if (node.parent_label == 'root') frappe.set_route("Form", 'Branch', node.label);
                        else frappe.set_route("Form", me.ctype, node.label);

                    }
                },
                {
                    label: __("Add Child"),
                    condition: function(node) { return me.can_create && node.expandable; },
                    click: function(node) {
                        me.new_node();
                    },
                    btnClass: "hidden-xs"
                },
                {
                    label: __("Rename"),
                    condition: function(node) { return !node.root && me.can_write; },
                    click: function(node) {
                        if (node.parent_label == 'root') {
                            frappe.model.rename_doc('Branch', node.label, function(new_name) {
                                node.$a.html(new_name);
                            });
                        } else {
                            frappe.model.rename_doc(me.ctype, node.label, function(new_name) {
                                node.$a.html(new_name);

                            });
                        }

                    },
                    btnClass: "hidden-xs"
                },
                {
                    label: __("Delete"),
                    condition: function(node) { return !node.root && me.can_delete; },
                    click: function(node) {

                        if (node.parent_label == 'root') {
                            frappe.model.delete_doc('Branch', node.label, function() {
                                node.parent.remove();
                            });
                        } else {
                            frappe.model.delete_doc(me.ctype, node.label, function() {
                                node.parent.remove();
                            });
                        }
                    },
                    btnClass: "hidden-xs"
                }

            ],
            onrender: function(node) {
                node.data.parent_code = '0';
                //console.log(node)
                if (node.data.code !== null && node.data.code !== undefined) {
                    $('<span class="label label-success" style="margin-right:20px;padding:3px;float: right;">' +
                        node.data.code +
                        '</span>').insertBefore(node.$ul);
                }
            },
        });
    },
    set_title: function(val) {
        var chart_str = this.ctype == "Department" ? __("Administrative Structure") : __("Administrative Structure");
        if (val) {
            this.page.set_title(chart_str + " - " + cstr(val));
        } else {
            this.page.set_title(chart_str);
        }
    },


    new_node: function() {
        var me = this;
        var node = me.tree.get_selected_node();

        if (!(node && node.expandable)) {
            frappe.msgprint(__("Select a group node first."));
            return;
        }

            var fields = [
		{
                fieldtype: 'Check',
                fieldname: 'is_headquarter',
                label: __('Is Headquarter'),
                default: '1'
            },
            {
                fieldtype: 'Column Break',
                fieldname: 'column_break'

            },
		{
                fieldtype: 'Check',
                fieldname: 'is_branch',
                label: __('Is Branch')
            },
            {
                fieldtype: 'Column Break',
                fieldname: 'column_break2'
            },
            {
                fieldtype: 'Check',
                fieldname: 'is_management',
                label: __('Is Management')
            },
            {
                fieldtype: 'Column Break',
                fieldname: 'column_break3'

            },
            {
                fieldtype: 'Check',
                fieldname: 'is_circle',
                label: __('Is Circle')
            },
            {
                fieldtype: 'Column Break',
                fieldname: 'column_break3'

            },
            {
                fieldtype: 'Check',
                fieldname: 'is_department',
                label: __('Is Department')
            },
            {
                fieldtype: 'Section Break',
                fieldname: 'section_break'

            },//****************is_headquarter
		{
                    fieldtype: 'Data',
                    fieldname: 'headquarter',
                    label: __('Headquarter Name Arabic'),
                    depends_on: 'eval:doc.is_headquarter==1'
                },

                {
                    fieldtype: 'Data',
                    fieldname: 'headquarter_en',
                    label: __('Headquarter Name'),
                    depends_on: 'eval:doc.is_headquarter==1'
                },


                {
                    fieldtype: 'Data',
                    fieldname: 'parent_headquarter',
                    read_only: true,
                    label: __('Headquarter Parent'),
                    depends_on: 'eval:doc.is_headquarter==1'

                },
               //****************is_branch
	  	{
                    fieldtype: 'Data',
                    fieldname: 'branch',
                    label: __('Branch Name Arabic'),
                    depends_on: 'eval:doc.is_branch==1'
                },

                {
                    fieldtype: 'Data',
                    fieldname: 'branch_en',
                    label: __('Branch Name'),
                    depends_on: 'eval:doc.is_branch==1'
                },


                {
                    fieldtype: 'Data',
                    fieldname: 'parent_branch',
                    read_only: true,
                    label: __('Branch Parent'),
                    depends_on: 'eval:doc.is_branch==1'

                },
		//**************is_management
                {
                    fieldtype: 'Data',
                    fieldname: 'management',
                    label: __('New Management Name'),
                    depends_on: 'eval:doc.is_management==1'
                },{
                    fieldtype: 'Data',
                    fieldname: 'management_en',
                    label: __('New Management English Name'),
                    depends_on: 'eval:doc.is_management==1'
                },


                {
                    fieldtype: 'Data',
                    fieldname: 'parent_management',
                    label: __('Parent Management'),
                    read_only: true,
                    depends_on: 'eval:doc.is_management==1'

                },//**************is_circle
                {
                    fieldtype: 'Data',
                    fieldname: 'circle',
                    label: __('New Circle Name'),
                    depends_on: 'eval:doc.is_circle==1'
                },{
                    fieldtype: 'Data',
                    fieldname: 'circle_en',
                    label: __('New Circle English Name'),
                    depends_on: 'eval:doc.is_circle==1'
                },


                {
                    fieldtype: 'Data',
                    fieldname: 'parent_circle',
                    label: __('Parent Circle'),
                    read_only: true,
                    depends_on: 'eval:doc.is_circle==1'

                },

		//**************is_department
                {
                    fieldtype: 'Data',
                    fieldname: 'department',
                    label: __('New {0} Name', [__(me.ctype)]),
                    depends_on: 'eval:doc.is_department==1'
                },{
                    fieldtype: 'Data',
                    fieldname: 'department_en',
                    label: __('New {0} English Name', [__(me.ctype)]),
                    depends_on: 'eval:doc.is_department==1'
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'parent_department',
                    label: __('Parent Department'),
                    read_only: true,
                    depends_on: 'eval:doc.is_department==1'
                },
                {
                    fieldtype: 'Link',
                    fieldname: 'director',
                    label: __('Director'),
                    options: 'Employee'

                },
                {
                    fieldtype: 'Data',
                    fieldname: 'director_name',
                    label: __('Director Name'),
                    options: 'director.employee_name',
		    read_only: true

                },


                {
                    fieldtype: 'Check',
                    fieldname: 'is_group',
                    label: __('Group Node'),
                    description: __("Further nodes can be only created under 'Group' type nodes")
                }
            ]

        // the dialog
        var d = new frappe.ui.Dialog({
            title: __('New {0}', [__(me.ctype)]),
            fields: fields

        })
	
	var args = $.extend({}, me.args);

	d.set_value("is_group", 0);
	d.set_values(args);

        d.set_value("parent_department", me.tree.get_selected_node().label);
        d.set_value("parent_branch", me.tree.get_selected_node().label);
        d.set_value("parent_circle", me.tree.get_selected_node().label);
        d.set_value("parent_management", me.tree.get_selected_node().label);
        d.set_value("parent_headquarter", me.tree.get_selected_node().label);
        //if (me.tree.get_selected_node().label != 'root') d.set_value("branch", me.tree.get_selected_node().label);


        // create

        d.set_primary_action(__("Create New"), function() {


            var btn = this;
            var v = d.get_values();
            if (!v) return;

            var node = me.tree.get_selected_node();

             v.parent = node.label;
            v.ctype = me.ctype;

			var entry_type,name,name_en,is_group,parent,director, director_name;
			director=v.director; director_name=v.director_name;

			if (v.is_headquarter== 1){
			entry_type= 'Headquarter'; name=v.headquarter; name_en=v.headquarter_en; parent=v.parent_headquarter}
			else if (v.is_branch== 1){
			entry_type= 'Branch'; name=v.branch; name_en=v.branch_en; parent=v.parent_branch}
			else if (v.is_management== 1){
			entry_type= 'Management'; name=v.management; name_en=v.management_en; parent=v.parent_management}
			else if (v.is_circle== 1){
			entry_type= 'Circle'; name=v.circle; name_en=v.circle_en; parent=v.parent_circle}
			else if (v.is_department== 1){
			entry_type= 'Department'; name=v.department; name_en=v.department_en; parent=v.parent_department}
			else frappe.throw(__("Check type of new entry"));

            //frappe.call({
              //  method: "erpnext.hr.page.administrative_struc.administrative_struc.get_account_level",
                //args: {
                  //  cur_parent: node.data.value
                //},
                //callback: function(r) {
                  //  var level = r.message;

                    return frappe.call({
                        method: 'erpnext.hr.page.administrative_struc.administrative_struc.add_node',
                        args: {
                      	'entry_type':entry_type,
                                'name': name,
                                'name_en': name_en,
                                'is_group': v.is_group,
                                'parent': parent,
				'director':director,
				'director_name':director_name

                        },
                        callback: function(r) {
                            if (!r.exc) {
                                d.hide();
                                if (node.expanded) {
                                    node.toggle_node();
                                }
                                node.reload();
                            }
                        }
                    });


//                }
  //          });



        });

        d.show();

	d.fields_dict.is_headquarter.$input.on("change", function(event) {
            var val = d.get_values();

            if( val.is_branch == 1 || val.is_management == 1 || val.is_circle == 1 || val.is_department == 1  ) {
                d.set_value("is_branch", 0);
                d.set_value("is_management", 0);
                d.set_value("is_circle", 0);
                d.set_value("is_department", 0);
            } 
            d.fields_dict.is_headquarter.refresh();
        });

	d.fields_dict.is_branch.$input.on("change", function(event) {
            var val = d.get_values();

            if( val.is_headquarter == 1 || val.is_management == 1 || val.is_circle == 1 || val.is_department == 1  ) {
                d.set_value("is_headquarter", 0);
                d.set_value("is_management", 0);
                d.set_value("is_circle", 0);
                d.set_value("is_department", 0);
            } 
            d.fields_dict.is_branch.refresh();
        });

       d.fields_dict.is_management.$input.on("change", function(event) {
            var val = d.get_values();

            if( val.is_branch == 1 || val.is_headquarter == 1 || val.is_circle == 1 || val.is_department == 1  ) {
                d.set_value("is_branch", 0);
                d.set_value("is_headquarter", 0);
                d.set_value("is_circle", 0);
                d.set_value("is_department", 0);
            } 
            d.fields_dict.is_management.refresh();
        });

       d.fields_dict.is_circle.$input.on("change", function(event) {
            var val = d.get_values();

            if( val.is_branch == 1 || val.is_headquarter == 1 || val.is_management == 1 || val.is_department == 1  ) {
                d.set_value("is_branch", 0);
                d.set_value("is_headquarter", 0);
                d.set_value("is_management", 0);
                d.set_value("is_department", 0);
            } 
            d.fields_dict.is_circle.refresh();
        });

       d.fields_dict.is_department.$input.on("change", function(event) {
            var val = d.get_values();

            if( val.is_branch == 1 || val.is_headquarter == 1 || val.is_circle == 1 || val.is_management == 1  ) {
                d.set_value("is_branch", 0);
                d.set_value("is_headquarter", 0);
                d.set_value("is_circle", 0);
                d.set_value("is_management", 0);
            } 
            d.fields_dict.is_department.refresh();
        });



    },

});
