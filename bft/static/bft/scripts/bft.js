function initUploadControl() {
	
	$("#submit").click(function() {
		$("#form-upload").submit();
		return false;
	});
	
	if(flashCheck()) {
		
		$('#file-upload').uploadify({
			buttonImg: staticURL+"bft/images/choose.png",
			height: "37",
			width: "98",
			wmode: "transparent",
			queueSizeLimit: 5,
			sizeLimit: uploadSizeLimit,
			uploader: staticURL+"bft/images/uploadify.swf",
			cancelImg: staticURL+"bft/images/cancel.png",
			fileDataName: "file_upload",
			onCancel: function (a, b, c, d) {
				flashQueue = d.fileCount;
				flashTotalBytes = d.allBytesTotal;
			},
			onClearQueue: function (a, b) {
				flashQueue = b.fileCount;
				flashTotalBytes = b.allBytesTotal;
			},
			onQueueFull: function(a, b) {
				$.blockUI({
					message: "The queue limit is full. The max size is " + b,
					css: { 
						border:'none', padding:'15px', size:'13.0pt',
						backgroundColor:'#000', color:'#fff', fontWeight:'bold',
						opacity:'.8','-webkit-border-radius': '10px','-moz-border-radius': '10px'
					}
				});
				window.setTimeout($.unblockUI, 3000);
				return false;
			},
			onSelectOnce: function (a, b) {
				if (b.allBytesTotal > uploadSizeLimit) {
					$(this).uploadifyClearQueue();
					
					$.blockUI({
						message: "The size of the files selected exceeds the allowed limit of " + uploadSizeLimit/1024/1024/1024 + " GB.  Please stay within this limit.",
						css: { 
							border:'none', padding:'15px', size:'13.0pt',
							backgroundColor:'#000', color:'#fff', fontWeight:'bold',
							opacity:'.8','-webkit-border-radius': '10px','-moz-border-radius': '10px'
						}
					});
					window.setTimeout($.unblockUI, 5000);
				}
				else {
					flashQueue = b.fileCount;
					flashTotalBytes = b.allBytesTotal;
				}
			},
			onComplete: function (a, b ,c, d, e) {
				flashQueue = e.fileCount;
			},
			onAllComplete: function(a, b) {
				flashQueue = 0;
				$("#uploading").html("Processing...");
				if (b.errors > 0) {
					$(this).uploadifyClearQueue();
					showErrors([uploadServerError], 'Server Error');
				}
				else {
					location.href = submissionURL;
				}
			},
			onProgress: function(a, b, c, d) {
				var percents = parseInt(d.allBytesLoaded/flashTotalBytes*100);
				$('#received').html("Uploading: "+parseInt(d.allBytesLoaded/1024)+"/");
				$('#size').html(parseInt(flashTotalBytes/1024)+" KB");
				$('#percent').html(percents+"%");
				$("#progress").css('width', percents+"%")
				
				return false;
			},
			onError: function(a, b, c, d) {
				if (window.console && window.console.log) {
					console.log(d);
				}
				else {
					location.href = '/500error/';
				}
			},
			auto: false,
			multi: true,
			queueSizeLimit: 5
		});
		
		//create ajax form
		$("#form-upload").ajaxForm({
			iframe: true, 
			dataType: "json",
			success: formSuccess,
			beforeSubmit: formValidate
		});
	}
	else {
		
		$('#form-upload').uploadProgress({
		    jqueryPath: "https://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js",
		    uploadProgressPath: staticURL+"bft/scripts/jquery.uploadProgress.js",
		    start: function() { 
				$('input[type="file"]').each(function(){
					$(this).attr('name', $(this).attr('id'));	
				});
			},
			uploading: function(upload) {
				$('#received').html("Uploading: "+parseInt(upload.received/1024)+"/");
				$('#size').html(parseInt(upload.size/1024)+" KB");
				$('#percent').html(upload.percents+"%");
				$("#progress").css('width', upload.percents+"%");
			},
			complete: function() {
				$("#uploading").html("Processing...");
			},
			error: function() {
				window.clearTimeout(this.timer);
				if (formValid) {
					$('#file-upload').MultiFile('reset');
					showErrors([uploadServerError], 'Server Error');
				}
			},
			progressBar: "#progressbar",
		    progressUrl: progressURL,
		    interval: 2000,
			preloadImages: [staticURL+"bft/images/overlay.png"]
	    }).ajaxForm({
			iframe: true, 
			dataType: "json",
			success: formSuccess,
			beforeSubmit: formValidate
		});
		
		$('#file-upload').MultiFile({
			max: 5,
			STRING: { 
				remove: '<img border="0" src="'+staticURL+'bft/images/cancel.png" alt="remove file">' 
			} 
		});

	}
}


function initRecipientsControl() {
	$("#addrecip").click(function(){
		var ele = $("<div></div>").html('<label><input type="text" name="recip" /></label>');
		
		$("#addrecip").appendTo(ele);
		$("#recipients div label:last").append('<span>[<a href="#" class="delrecip">Delete</a>]</span>');
		$(ele).appendTo("#recipients");
		
		$("a.delrecip").click(function(){
			$(this).closest("div").remove();
			return false;
		});
		return false;
	});
}


function initRepactchaControl() {
	Recaptcha.create(captchaKey, "recaptcha", {theme:"custom"});

	$("#captcha-audio").click(function(){
		Recaptcha.switch_type('audio');
		return false;
	});

	$("#captcha-refresh").click(function(){
		Recaptcha.reload();
		return false;
	});
	
}

function flashCheck() {
	if (useFlash == "True" && swfobject.hasFlashPlayerVersion('10.0.0')) {
		return true;
	}
	else {
		useFlash = "False";
		return false;
	}
}


function formSuccess(response, responseStatus, form) {
	//output server validation errors
	if (response.error) {
		if (flashCheck()) {
			$('#file-upload').uploadifyClearQueue();
		}
		else {
			$('#file-upload').MultiFile('reset');
		}
		showErrors(response.messages);
	}
	//return success output.
	else {
		
		//set the submission
		submissionSlug = response.submission_slug;
		submissionURL = response.submission_url;
		
		if (submissionSlug == undefined) {
			showErrors([browserError], 'Server Error');
		}
		else {
			
			//post upload when flash in enabled.
			if (flashCheck()) {
				//$(".uploadifyProgress").show();
				$("#file-upload").uploadifySettings('script', flashURL+"?slug="+submissionSlug);
				$("#file-upload").uploadifyUpload();
			}
			//grab the files if html upload
			else {
				location.href = submissionURL;
			}
		}
	}
	
	if ($("meta[name='use_captcha']").attr("content") == "True") {
		Recaptcha.reload();
	}
		
}


function formValidate() {
	var messages = [];

	//check file upload
	if (flashCheck()){
		if (flashQueue == 0) {
			messages.push("Please select a file to upload.");
		}
	}
	else {
		if (!$("input[id*='file-upload']").val()) {
			messages.push("Please select a file to upload.");
		}
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
		
		var recips = [];
			
		$("input[name='recip']").each(function(){
			if ($(this).val()) {
				recips.push($(this).val());
			}
		});
		
		if (recips.length == 0) {
			messages.push("Please enter an email address for the recipeint(s).");
		}
		else {
			//return error if emails are not valid
			$.each(recips, function(i, val) {
				if (!isValidEmail(val)) {
					messages.push("Please enter a valid email address for the reciepient(s).");
					return false;
				}
			});

			//otherwise join the emails to the field
			$("input[name='recipients']").val(recips.join(','));
		}
		
		var anums = [];
		
		$("input[name='anum']").each(function(){
			if ($(this).val()) {
				anums.push($(this).val());
			}
		});
		
		if (!$("#message").val()) {
			messages.push("Please enter a message for this upload.");
		}
		
	}
	
	// re-captcha vaidation
	if (useCaptcha == "True") {
		if (!$("#recaptcha_response_field").val()) {
			messages.push("Please verify the words or audio in step 3.")
		}
		else {
			// server-side check on captcha
			$.ajax({
				url: captchaURL,
				type: "post",
				async: false,
				data: {
					recaptcha_challenge_field: $("#recaptcha_challenge_field").val(),
					recaptcha_response_field: $("#recaptcha_response_field").val()
				},
				dataType: "html",
				success: function(response, responseStatus, XMLHttpRequest) {
					//output server validation errors
					if (response == "0") {
						messages.push("The response in in step 3 does not match the words or audio, please try again.")
					}
				}
			});
		}
	}
	else {
		if (!$("#signiture").val()) {
			messages.push("Please verify that you own the rights to the file(s) by entering your initials in step 3.")
		}
	}
	
	if (messages.length) {
		showErrors(messages);
		return false;
	}
	else {
		formValid = true;
		$.lightBoxFu.open({
	        html: '<div id="uploading"><span id="received">Processing...</span><span id="size"></span><br/><div id="progress" class="bar"><div id="progressbar">&nbsp;</div></div><span id="percent"></span></div>',
	        width: "250px",
	        closeOnClick: false
	    });
		return true;
	}
}


function isValidEmail(str) {
   return (str.indexOf(".") > 0) && (str.indexOf("@") > 0);
}


function showErrors(messages, title) {
	$.lightBoxFu.close();
	
	formValid = false;
	
	if (hasCaptcha()) {
		Recaptcha.reload();
	}
	
	$("#dialog").html("<ul class='errors'></ul>")
	$.each(messages, function(i, val){
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


function hasCaptcha() {
	if (useCaptcha == "True") {
		return true;
	}
	else {
		return false;
	}
}

$(document).ready(function() {
	var docStr = document.location.toString();
	
	var flashPlayerMeta = swfobject.getFlashPlayerVersion().major + '.' + swfobject.getFlashPlayerVersion().minor + '.' + swfobject.getFlashPlayerVersion().release;

	//$("#noscript").remove();
	$("#form-upload").show();

	$.lightBoxFu.initialize({imagesPath: absStaticURL+'images/', stylesheetsPath: absStaticURL+'styles/'});
	
	$('body').ajaxError(function(event, XMLHttpRequest, ajaxOptions, thrownError) {
		//reset the uploader
		if (flashCheck()) {
			$('#file-upload').uploadifyClearQueue();
		}
		else {
			$('#file-upload').MultiFile('reset');
		}
		
		showErrors(['There was an error processing your request, please contact your web administrator.'], 'Server Error');

		if (window.console && window.console.log) {
			console.log(arguments);
			console.log(XMLHttpRequest.responseText)
		}
		return false;
	});
	
	$("#dialog").dialog({
		autoOpen: false,
		modal: true,
		width: 400,
		buttons: {
			"Ok": function() {
				$(this).dialog('close');
			}
		},
		close: function(event, ui) {
			$("input[type='file']").removeAttr('disabled');
			$(this).html('');
		}
	});
	
	$("#tabs a").click(function(){
		uploadType = $(this).attr('href').split('#')[1];
		
		$("#step-two").children().hide();
		$("#steps-right").children().hide();
		
		if (uploadType == "link") {
			$("#submit").html("Get Link(s)").addClass("btn-link").removeClass("btn-email");
			$("#email-address").prependTo("#input-email");
			$("#password-field").appendTo("#input-password");
			$("#step-two .border").show();
			$("#step-email").show();
			$("#links").show();
		}
		else {
			$("#submit").html("Submit Email").addClass("btn-email").removeClass("btn-link");
			$("#email-address").appendTo("#info-email");
			$("#password-field").appendTo("#label-password");
			$("#info-message").show();
			$("#step-four").show();
			$("#step-five").show();
			$("#step-six").show();
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
	
	if (hasCaptcha()) {
		initRepactchaControl();
	}
	
	//inject browser and flash player meta
	$("#flash-meta").val('Has Flash: ' + flashCheck() + '  Flash Player:' + flashPlayerMeta);
	
	
	//show alert for firebug
	if (window.console && window.console.firebug) {
		$("body").prepend("<div id='warning'>It looks like you have Firebug enabled in your browser.  For best performance, please disable it before using BFT.</div>")
	}
	//show ie 7 or earlier
	else if ($.browser.msie && parseFloat($.browser.version) < 7) {
		$("body").prepend("<div id='warning'>It looks like you are using Internet Explorer version 7 or earlier. This site is not fully supported by your browser.  Please upgrade your browser to Internet Explorer 8 or later.</div>")
	}
});

