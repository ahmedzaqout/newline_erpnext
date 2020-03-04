	var $form = $("form[data-web-form='job-application']");
	
frappe.ready(function() {




	var $form = $("form[data-web-form='job-application']");


	// read file attachment
	$form.on("change", "[data-fieldname='governorate']", function() {
			area = $form.find("[data-fieldname='governorate']").val();
			console.log(area);
			filterCity(area);

});
});


	


function filterCity(area) {
		console.log('api/resource/City?filters=[["governorate","=","${area}"]]');
			$.ajax({
			url: 'api/resource/City?filters=[["governorate","=","'+area+'"]]',
			success: function(result) {
			console.log(result);
			var options = []
			for (var i = 0; i < result.data.length; i++) {

			options.push({
			'label': result.data[i].name,
			'value': result.data[i].name
			})
			 var field = frappe.web_form.field_group.get_field('city');
			 field._data = options;
			 field.refresh();

		  }
  

}
});

};
var get_data = function get_data() {
		frappe.mandatory_missing_in_last_doc = [];
		console.log($form);
		var doc = get_data_for_doctype($form, frappe.web_form_doctype);
		doc.doctype = frappe.web_form_doctype;
		if (frappe.doc_name) {
			doc.name = frappe.doc_name;
		}
		frappe.mandatory_missing = frappe.mandatory_missing_in_last_doc;

		$('.web-form-grid').each(function () {
			var fieldname = $(this).attr('data-fieldname');
			var doctype = $(this).attr('data-doctype');
			doc[fieldname] = [];

			$(this).find('[data-child-row=1]').each(function () {
				if (!$(this).hasClass('hidden')) {
					frappe.mandatory_missing_in_last_doc = [];
					var d = get_data_for_doctype($(this), doctype);

					var name = $(this).attr('data-name');
					if (name) {
						d.name = name;
					}

					var has_value = false;
					for (var key in d) {
						if (typeof d[key] === 'string') {
							d[key] = d[key].trim();
						}
						if (d[key] !== null && d[key] !== undefined && d[key] !== '') {
							has_value = true;
							break;
						}
					}

					if (has_value) {
						doc[fieldname].push(d);
						frappe.mandatory_missing = frappe.mandatory_missing.concat(frappe.mandatory_missing_in_last_doc);
					}
				}
			});
		});

		return doc;
	};

	var get_data_for_doctype = function get_data_for_doctype(parent, doctype) {
		var out = {};
		parent.find("[name][data-doctype='" + doctype + "']").each(function () {
			var $input = $(this);
			var input_type = $input.attr("data-fieldtype");
			var no_attachment = false;

			if (input_type === "Attach") {
				if ($input.get(0).filedata) {
					var val = $input.get(0).filedata;
				} else {
					var val = $input.attr('data-value');
					if (!val) {
						val = { '__no_attachment': 1 };
						no_attachment = true;
					}
				}
			} else if (input_type === 'Text Editor') {
				var val = $input.parent().find('.note-editable').html();
			} else if (input_type === "Check") {
				var val = $input.prop("checked") ? 1 : 0;
			} else if (input_type === "Date") {
				if ($input.val()) {
					var val = moment($input.val(), moment.defaultFormat).format('YYYY-MM-DD');
				} else {
					var val = null;
				}
			} else {
				var val = $input.val();
			}

			if (typeof val === 'string') {
				val = val.trim();
			}

			if ($input.attr("data-reqd") && (val === undefined || val === null || val === '' || no_attachment)) {
				frappe.mandatory_missing_in_last_doc.push([$input.attr("data-label"), $input.parents('.web-form-page:first').attr('data-label')]);
			}

			out[$input.attr("name")] = val;
		});
		return out;
	};


function save(for_payment) {
		if (window.saving) return false;
		window.saving = true;
		frappe.form_dirty = false;

		if (frappe.file_reading) {
			window.saving = false;
			frappe.msgprint(__("Uploading files please wait for a few seconds."));
			return false;
		}

		var data = get_data();
		console.log(data);
			if ((!frappe.allow_incomplete || for_payment) && frappe.mandatory_missing.length) {
				window.saving = false;
				show_mandatory_missing();
			return false;
		}
		data2=data

		frappe.call({
			type: "POST",
			method: "frappe.website.doctype.web_form.web_form.accept",
			args: {
				data: data,
				web_form: frappe.web_form_name,
				for_payment: for_payment
			},
			freeze: true,
			btn: $form.find("[type='submit']"),
			callback: function callback(data) {
				if (!data.exc) {
					frappe.doc_name = data.message;
					if (!frappe.login_required) {
					window.location.href = "/job_applicant_questions?job_applicant="+ data.message+"&&job_title="+ data2.job_title;

						
					}

					if (frappe.is_new && frappe.login_required) {
						window.location.href = window.location.pathname + "?name=" + frappe.doc_name;
					}

					if (for_payment && data.message) {
						window.location.href = data.message;
					}
				} else {
					frappe.msgprint(__('There were errors. Please report this.'));
				}
			},
			always: function always() {
				window.saving = false;
			}
		});
		return true;
	}
function show_mandatory_missing() {
		var text = [],
		    last_section = null;
		/*frappe.mandatory_missing.forEach(function (d) {
			if (last_section != d[1]) {
				text.push('');
				text.push(d[1].bold());
				last_section = d[1];
			}
			text.push(d[0]);
		});*/
		frappe.msgprint(__('The following mandatory fields must be filled:<br>') + text.join('<br>'));
	}


function show_success_message() {
		$form.addClass("hide");
		$(".comments, .introduction, .page-head").addClass("hide");
		scroll(0, 0);
		$(".form-message").html("kjk").removeClass("hide");

	}
$('.btn-form-submit').on('click', function () {
		console.log("SDs");
		save();
		console.log("www");
		return false;
});


