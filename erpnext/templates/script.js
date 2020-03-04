$('#save-btn').on('click',function(e){
  	e.preventDefault();
	var m = this;
	$(m).css("disabled","true");
	$(m).html('<i class="fa fa-circle-o" aria-hidden="true"></i>');

	data1={}
	var data = $("#interview").serializeArray();
		console.log(data);
	for (i=0;i<data.length;i++){
		console.log(data[i]['name']);
		data1[data[i]['name']]=data[i]['value'];
	}
	console.log(data1);
	frappe.call({
		type: "POST",
		args: data1,
		method: 'erpnext.hr.doctype.job_applicant.job_applicant.test_interview',
		freeze: true,
		 async: false,
		callback: function(r){
			if(r.message){
				console.log(r.message);
				if (r.message.status =="success")
				$('.quiz-wrapp').html("لقد تم قبول طلبك ضمن الطلبات المقدمة لاجتيازك الاختبار بنجاح");
				else{
				if (r.message.status =="repaited")
				$('.quiz-wrapp').html("لقد قدمت الاختبار من قبل, لا يمكن تقديمه مرة أخرى");
				else{
				$('.quiz-wrapp').html("لم يتم قبول طلبك لأنك لم تجتاز الاختبار");				
						}
					}
			}
			}
		});

});

