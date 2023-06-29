$(document).ready(function() {
	if ($("#id_type").val() != 'email') {
		$("#id_email-TOTAL_FORMS").parent().hide();
	}
	
	$("#id_type").change(function(){
		if ($(this).val() == 'email') {
			$("#id_email-TOTAL_FORMS").parent().show();
		}
		else {
			$("#id_email-TOTAL_FORMS").parent().hide();
		}
	});
});