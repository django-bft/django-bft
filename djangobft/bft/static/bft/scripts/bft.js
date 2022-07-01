function initUploadControl() {

	$("#submit").click(() => {
		$("#form-upload").submit();
		return false;
	});

	$('#file-upload').uploadifive({
		'auto': false,
		'multi': true,
		'width': 350,
		'height': 65,
		'buttonClass': 'upload-button',
		'buttonText': 'Drag and drop, or click to browse files...',
		'itemTemplate': '<div class="uploadifive-queue-item"><a class="close" href="#"><i class="fa-solid fa-circle-xmark"></i></a><div class="info-wrapper"><span class="filename"></span><span class="fileinfo"></span></div><div class="progress"><div class="progress-bar"></div></div></div>',
		'fileObjName': 'file_upload',
		'fileSizeLimit': (uploadSizeLimit / 1024),
		'queueSizeLimit': 5,
		'formData': {
			'csrfmiddlewaretoken': csrfToken,
		},
		'uploadScript': `/upload/?slug=${submissionSlug}`,
		'dnd': true,

		onAddQueueItem: function (file) {
			if (flashQueue < 5) {
				flashQueue += 1;
			}
			else {
				flashQueue = 0;
				$('#file-upload').uploadifive('clearQueue');
			}
		},
		onClearQueue: function () {
			flashQueue = 0;
		},
		onCancel: function (file) {
			if (flashQueue > 0) {
				flashQueue -= 1;
			} else {
				flashQueue = 0;
			}
		},
		onQueueComplete: function (uploads) {
			flashQueue = 0;
			$("body").css('cursor', 'default');

			if (uploads.errors > 0) {
				$("#file-upload").uploadifive("clearQueue");
				showErrors([uploadServerError], 'Server Error');
			} else {
				location.href = `/files/${submissionSlug}`;
			}
		},
		onProgress: function (file, event) {
			event.preventDefault();

			if (!$('.fileinfo').val() == "- File Too Large") {

				if (event.lengthComputable) {
					var percent = Math.round((event.loaded / event.total) * 100);
				}
				$('.fileinfo').html(` - ${percent}%`);
				$('.progress-bar').css('width', `${percent}%`);
			}

			$("body").css('cursor', 'wait');

		},
		onError: function (file, fileType, data) {
			if (window.console && window.console.log) {
				console.log(data);
			}
			else {
				location.href = '/500error/';
			}
		},
	});

	//create ajax form
	$("#form-upload").ajaxForm({
		iframe: false,
		dataType: "json",
		success: formSuccess,
		beforeSubmit: formValidate,
	});
}

function initRecipientsControl() {
	$("#addrecip").click(function () {
		let ele = $("<div></div>").html('<label><input type="text" name="recipients" /></label>');

		$("#addrecip").appendTo(ele);
		$("#recipients div label:last").append('<span><a href="#" class="delrecip">Delete</a></span>');
		$(ele).appendTo("#recipients");

		$("a.delrecip").click(function () {
			$(this).closest("div").remove();
			return false;
		});

		return false;
	});

	$("#addanum").click(function () {
		let ele = $("<div></div>").html('<label><input type="text" name="anumbers" /></label>');

		$("#addanum").appendTo(ele);
		$("#anumbers div label:last").append('<span><a href="#" class="delanum">Delete</a></span>');
		$(ele).appendTo("#anumbers");

		$("a.delanum").click(function () {
			$(this).closest("div").remove();
			return false;
		});

		return false;
	});
}

function formSuccess(response, responseStatus, form) {
	//output server validation errors
	if (response.error) {
		$("#file-upload").uploadifive("clearQueue");
		showErrors(response.messages);
	}
	//return success output.
	else {
		//set the submission
		submissionSlug = response.submission_slug;
		if (submissionSlug == undefined) {
			showErrors([browserError], 'Server Error');
		}
		else {
			$("#file-upload").data('uploadifive').settings.uploadScript = `/upload/?slug=${submissionSlug}`;
			$('#file-upload').uploadifive('upload');
		}
	}
}

function formValidate() {
	let messages = [];

	//check if a file is in the queue
	if (flashQueue == 0) {
		messages.push("Please select a file to upload.");
	}

	//check to make sure an email is entered
	if (!$("#email-address").val()) {
		messages.push("Please enter your email address.");
	}
	else if (!isValidEmail($("#email-address").val())) {
		messages.push("Please enter a valid email address.");
	}

	//check field for email submission
	if (uploadType == "email") {
		if (!$("#first-name").val()) {
			messages.push("Please enter your first name.");
		}

		if (!$("#last-name").val()) {
			messages.push("Please enter your last name.");
		}

		let recips = [];

		$("input[name='recipients']").each(function () {
			if ($(this).val()) {
				recips.push($(this).val());
			}
		});

		if (recips.length == 0) {
			messages.push("Please enter an email address for the recipeint(s).");
		}
		else {
			//return error if emails are not valid
			$.each(recips, function (i, val) {
				if (!isValidEmail(val)) {
					messages.push("Please enter a valid email address for the reciepient(s).");
					return false;
				}
			});
		}

		let anums = [];

		$("input[name='anumumbers']").each(function () {
			if ($(this).val()) {
				anums.push($(this).val());
			}
		});

		//return error if anumbers are not valid
		$.each(anums, function (i, val) {
			let a = val.substr(0, 1).toLowerCase();
			let digits = val.toLowerCase().split('a')[1];

			if (a != 'a' || !(/^\d{8}$/.test(digits))) {
				messages.push("One or more of the A-numbers provided are invalid.");
				return false;
			}
		});
		//otherwise join the anumbers to the field
		// $("input[name='anumbers']").val(anums.join(','));

		if (!$("#message").val()) {
			messages.push("Please enter a message for this upload.");
		}

	}

	// signature vaidation
	if (!$("#signiture").val()) {
		messages.push("Please verify that you own the rights to the file(s) by entering your initials in step 3.");
	}

	if (messages.length) {
		showErrors(messages);
		return false;
	}
	else {
		formValid = true;
		return true;
	}
}


function isValidEmail(str) {
	return (str.indexOf(".") > 0) && (str.indexOf("@") > 0);
}

function showErrors(messages, title) {
	// formValid = false;

	$("#dialog").html("<ul class='errors'></ul>");
	$.each(messages, function (i, val) {
		$("<li></li>").html(val).appendTo(".errors");
	});
	if (title) {
		$("#dialog").dialog('option', 'title', title);
	}
	else {
		$("#dialog").dialog('option', 'title', 'Validation Error');
	}
	$("#dialog").dialog('open');
}

$(document).ready(function () {
	let docStr = document.location.toString();

	$("#form-upload").show();

	$('body').ajaxError(function (event, XMLHttpRequest, ajaxOptions, thrownError) {
		//reset the uploader
		$('#file-upload').uploadifive('clearQueue');

		showErrors(['There was an error processing your request, please contact your web administrator.'], '');

		if (window.console && window.console.log) {
			console.log(arguments);
		}

		return false;
	});

	$("#dialog").dialog({
		autoOpen: false,
		modal: true,
		width: 400,
		buttons: {
			"Ok": function () {
				$(this).dialog('close');
			}
		},
		close: function (event, ui) {
			$("input[type='file']").removeAttr('disabled');
			$(this).html('');
		}
	});

	$("#tabs a").click(function () {
		uploadType = $(this).attr('href').split('#')[1];

		$("#step-two").children().hide();
		$("#steps-right").children().hide();

		if (uploadType == "link") {
			$("#submit").html("Get Link(s)").addClass("btn-link").removeClass("btn-email");
			$("#email-address").prependTo("#input-email");
			$("#step-two .border").show();
			$("#step-email").show();
			$("#links").show();

			$("#tab-link").css('background-color', '#384660');
			$("#tab-email").css('background-color', '#2F3A50');
		}
		else {
			$("#submit").html("Submit Email").addClass("btn-email").removeClass("btn-link");
			$("#email-address").appendTo("#info-email");
			$("#info-message").show();
			$("#step-four").show();
			$("#step-five").show();
			$("#step-six").show();

			$("#tab-link").css('background-color', '#2F3A50');
			$("#tab-email").css('background-color', '#384660');
		}

		$("#type").val(uploadType);

		$("div.nav-border").removeClass('hide-border');

		$(this).next().addClass('hide-border');
	});

	//open the type based upon the anchor in the url
	if (docStr.match('#link')) {
		$("#tab-link").click();
	}
	else if (docStr.match('#email') || docStr.match('#') || docStr.match('')) {
		$("#tab-email").click();
	}

	initUploadControl();
	initRecipientsControl();

	// DRAG AND DROP FUNCTIONALITY
	let counter = 0;

	document.addEventListener('dragenter', e => {
		e.preventDefault();
		if (e.target === $("#uploadifive-file-upload").children()[$("#uploadifive-file-upload").children().length - 1]) {
			counter++;
			$("#uploadifive-file-upload").addClass('highlight');
		}
	})
	document.addEventListener('dragleave', e => {
		e.preventDefault();
		if (e.target === $("#uploadifive-file-upload").children()[$("#uploadifive-file-upload").children().length - 1]) {
			counter--;
			if (counter === 0) {
				$("#uploadifive-file-upload").removeClass('highlight');
			}
		}
	})
	document.addEventListener('drop', e => {
		if (e.target == $("#uploadifive-file-upload").children()[$("#uploadifive-file-upload").children().length - 1]) {
			counter = 0;
			$("#uploadifive-file-upload").removeClass('highlight');
		}
	})

	//show alert for firebug
	if (window.console && window.console.firebug) {
		$("body").prepend("<div id='warning'>It looks like you have Firebug enabled in your browser.  For best performance, please disable it before using BFT.</div>");
	}
	//show ie 7 or earlier
	else if ($.browser.msie && parseFloat($.browser.version) < 7) {
		$("body").prepend("<div id='warning'>It looks like you are using Internet Explorer version 7 or earlier. This site is not fully supported by your browser.  Please upgrade your browser to Internet Explorer 8 or later.</div>");
	}
});