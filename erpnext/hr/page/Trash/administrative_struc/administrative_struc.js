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
			var title =  __('Administrative Structure');
			frappe.render_tree({title: title, tree: tree, print_settings:print_settings});
		});


    });

    wrapper.make_tree = function() {

        var ctype = frappe.get_route()[1] || 'Department';
        return frappe.call({
            method: 'erpnext.hr.page.administrative_struc.administrative_struc.get_children',
            callback: function(r) {
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
            method: 'erpnext.hr.page.administrative_struc.administrative_struc.get_children',
            toolbar: [
                { toggle_btn: true },
                {
                    label: __("Edit"),
                    condition: function(node) {
                        return !node.is_root && me.can_read;
                    },
                    click: function(node) {
                             if (node.data.level ==1) frappe.set_route("Form", 'Headquarter', node.label);
                        else if (node.data.level ==2) frappe.set_route("Form", 'Branch', node.label);
                        else if (node.data.level ==3) frappe.set_route("Form", 'Management' , node.label);
                        else if (node.data.level ==4) frappe.set_route("Form", 'Circle' , node.label);
                        else if (node.data.level ==5) frappe.set_route("Form", 'Department', node.label);

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
                //{
                    //label: __("Rename"),
                    //condition: function(node) { return !node.is_root && me.can_write; },
                    //click: function(node) {
                      //  if (node.data.level ==1) {
			//	frappe.model.rename_doc('Headquarter', node.label, function(new_name) {
                          //      node.$a.html(new_name);
                            //});}
                        //else if (node.data.level ==2) {
			//	frappe.model.rename_doc('Branch', node.label, function(new_name) {
                          //      node.$a.html(new_name);
                           // });}
                        //else if (node.data.level ==3)  {
			//	frappe.model.rename_doc('Management', node.label, function(new_name) {
                          //      node.$a.html(new_name);
                           // });}
                        //else if (node.data.level ==4)  {
			//	frappe.model.rename_doc('Circle', node.label, function(new_name) {
                          //      node.$a.html(new_name);
                           // });}
                        //else if (node.data.level ==5)  {
			//	frappe.model.rename_doc('Department', node.label, function(new_name) {
                          //      node.$a.html(new_name);
                           // });}    

                    //},
                   // btnClass: "hidden-xs"
                //},
                {
                    label: __("Delete"),
                    condition: function(node) { return !node.is_root && me.can_delete; },
                    click: function(node) {

                        if (node.data.level ==1) {
				frappe.model.delete_doc('Headquarter', node.label, function() {
                                node.parent.remove();
                            });}
                        else if (node.data.level ==2) {
				frappe.model.delete_doc('Branch', node.label, function() {
                                node.parent.remove();
                            });}
                        else if (node.data.level ==3) {
				frappe.model.delete_doc('Management', node.label, function() {
                                node.parent.remove();
                            });}
                        else if (node.data.level ==4) {
				frappe.model.delete_doc('Circle', node.label, function() {
                                node.parent.remove();
                            });}
                        else if (node.data.level ==5) {
				frappe.model.delete_doc('Department', node.label, function() {
                                node.parent.remove();
                            });}
                    },
                    btnClass: "hidden-xs"
                }

            ],
            onrender: function(node) {
                //node.data.parent_code = '0';
                console.log(node)
                if (node.data.code !== null && node.data.code !== undefined) {
                    $('<span class="label label-success" style="margin-right:20px;padding:3px;float: right;">' +
                        node.data.code +
                        '</span>').insertBefore(node.$ul);
                }
            },
 	     drop: function(node) {
                
              //  console.log("droppppppppp")
              
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
	//console.log(node)
        if (!(node && node.expandable)) {
            frappe.msgprint(__("Select a group node first."));
            return;
        }
	if (node.data.level==0){
            var fields = [
		//****************is_headquarter
		{
                    fieldtype: 'Data',
                    fieldname: 'headquarter',
                    label: __('Headquarter Name Arabic'),
		    reqd:true
                },

                {
                    fieldtype: 'Data',
                    fieldname: 'headquarter_en',
                    label: __('Headquarter Name'),
		    reqd:true
                },


                {
                    fieldtype: 'Data',
                    fieldname: 'parent_headquarter',
                    read_only: true,
                    label: __('Headquarter Parent')

                },
                {
                    fieldtype: 'Link',
                    fieldname: 'director',
                    label: __('Director'),
                    options: 'Employee',
		    reqd:true

                },
                {
                    fieldtype: 'Data',
                    fieldname: 'director_name',
                    label: __('Director Name'),
                    options: 'director.employee_name',
		    read_only: true,
		    hidden:1
                },
                {
                    fieldtype: 'Check',
                    fieldname: 'is_group',
                    label: __('Group Node'),
                    description: __("Further nodes can be only created under 'Group' type nodes"),
		    default:'1'
                },
                {
                    fieldtype: 'Link',
                    fieldname: 'company',
                    label: __('Company'),
                    options: 'Company',
		    default: frappe.defaults.get_default('company') ? frappe.defaults.get_default('company'): ""

                }
            ]
	}

	if (node.data.level==1){
            var fields = [
		//****************is_branch
	  	{
                    fieldtype: 'Data',
                    fieldname: 'branch',
                    label: __('Branch Name Arabic'),
		    reqd:true
                },

                {
                    fieldtype: 'Data',
                    fieldname: 'branch_en',
                    label: __('Branch Name'),
		    reqd:true
                },


                {
                    fieldtype: 'Data',
                    fieldname: 'parent_branch',
                    read_only: true,
                    label: __('Branch Parent')

                },
                {
                    fieldtype: 'Link',
                    fieldname: 'director',
                    label: __('Director'),
                    options: 'Employee',
		    reqd:true

                },
                {
                    fieldtype: 'Data',
                    fieldname: 'director_name',
                    label: __('Director Name'),
                    options: 'director.employee_name',
		    read_only: true,
		    hidden:1
                },
                {
                    fieldtype: 'Check',
                    fieldname: 'is_group',
                    label: __('Group Node'),
                    description: __("Further nodes can be only created under 'Group' type nodes"),
		    default:'1'
                },
                {
                    fieldtype: 'Link',
                    fieldname: 'company',
                    label: __('Company'),
                    options: 'Company',
		    default: frappe.defaults.get_default('company') ? frappe.defaults.get_default('company'): ""

                }
            ]
	}

	if (node.data.level==2){
            var fields = [
		//**************is_management
                {
                    fieldtype: 'Data',
                    fieldname: 'management',
                    label: __('New Management Name'),
		    reqd:true
                },{
                    fieldtype: 'Data',
                    fieldname: 'management_en',
                    label: __('New Management English Name'),
		    reqd:true
                },


                {
                    fieldtype: 'Data',
                    fieldname: 'parent_management',
                    label: __('Parent Management'),
                    read_only: true

                },
                {
                    fieldtype: 'Link',
                    fieldname: 'director',
                    label: __('Director'),
                    options: 'Employee',
		    reqd:true

                },
                {
                    fieldtype: 'Data',
                    fieldname: 'director_name',
                    label: __('Director Name'),
                    options: 'director.employee_name',
		    read_only: true,
		    hidden:1
                },
                {
                    fieldtype: 'Check',
                    fieldname: 'is_group',
                    label: __('Group Node'),
                    description: __("Further nodes can be only created under 'Group' type nodes"),
		    default:'1'
                },
                {
                    fieldtype: 'Link',
                    fieldname: 'company',
                    label: __('Company'),
                    options: 'Company',
		    default: frappe.defaults.get_default('company') ? frappe.defaults.get_default('company'): ""

                }
            ]
	}

	if (node.data.level==3){
            var fields = [
		//**************is_circle
                {
                    fieldtype: 'Data',
                    fieldname: 'circle',
                    label: __('New Circle Name'),
		    reqd:true
                },{
                    fieldtype: 'Data',
                    fieldname: 'circle_en',
                    label: __('New Circle English Name'),
		    reqd:true
                },


                {
                    fieldtype: 'Data',
                    fieldname: 'parent_circle',
                    label: __('Parent Circle'),
                    read_only: true

                },
                {
                    fieldtype: 'Link',
                    fieldname: 'director',
                    label: __('Director'),
                    options: 'Employee',
		    reqd:true

                },
                {
                    fieldtype: 'Data',
                    fieldname: 'director_name',
                    label: __('Director Name'),
                    options: 'director.employee_name',
		    read_only: true,
		    hidden:1
                },
                {
                    fieldtype: 'Check',
                    fieldname: 'is_group',
                    label: __('Group Node'),
                    description: __("Further nodes can be only created under 'Group' type nodes"),
		    default:'1'
                },
                {
                    fieldtype: 'Link',
                    fieldname: 'company',
                    label: __('Company'),
                    options: 'Company',
		    default: frappe.defaults.get_default('company') ? frappe.defaults.get_default('company'): ""

                }
            ]
	}
	if (node.data.level==4){
            var fields = [
		//**************is_department
                {
                    fieldtype: 'Data',
                    fieldname: 'department',
                    label: __('New {0} Name', [__(me.ctype)]),
		    reqd:true
                },{
                    fieldtype: 'Data',
                    fieldname: 'department_en',
                    label: __('New {0} English Name', [__(me.ctype)]),
		    reqd:true
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'parent_department',
                    label: __('Parent Department')
                },
                {
                    fieldtype: 'Link',
                    fieldname: 'director',
                    label: __('Director'),
                    options: 'Employee',
		    reqd:true

                },
                {
                    fieldtype: 'Data',
                    fieldname: 'director_name',
                    label: __('Director Name'),
                    options: 'director.employee_name',
		    read_only: true,
		    hidden:1
                },
                {
                    fieldtype: 'Check',
                    fieldname: 'is_group',
                    label: __('Group Node'),
                    description: __("Further nodes can be only created under 'Group' type nodes")
                },
                {
                    fieldtype: 'Link',
                    fieldname: 'company',
                    label: __('Company'),
                    options: 'Company',
		    default: frappe.defaults.get_default('company') ? frappe.defaults.get_default('company'): ""

                }
            ]
}



        // the dialog
        var d = new frappe.ui.Dialog({
            title: __('New {0}', [__(me.ctype)]),
            fields: fields

        })
	
	var args = $.extend({}, me.args);

	//d.set_value("is_group", 0);
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

			if (node.data.level== 0){
			entry_type= 'Headquarter'; name=v.headquarter; name_en=v.headquarter_en; parent=v.parent_headquarter}
			else if (node.data.level== 1){
			entry_type= 'Branch'; name=v.branch; name_en=v.branch_en; parent=v.parent_branch}
			else if (node.data.level== 2){
			entry_type= 'Management'; name=v.management; name_en=v.management_en; parent=v.parent_management}
			else if (node.data.level== 3){
			entry_type= 'Circle'; name=v.circle; name_en=v.circle_en; parent=v.parent_circle}
			else if (node.data.level== 4){
			entry_type= 'Department'; name=v.department; name_en=v.department_en; parent=v.parent_department}



                    return frappe.call({
                        method: 'erpnext.hr.page.administrative_struc.administrative_struc.add_node',
                        args: {
                      		'entry_type':entry_type,
                                'name': name,
                                'name_en': name_en,
                                'is_group': v.is_group,
                                'parent': parent,
				'director':director,
                                'company': v.company,

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



        });

        d.show();


    },

});
