$(function() {
	$('div#feedback div.handle').click( function() {
		var leftStr = "0px";
		($("div#feedback").css("left") == "0px") ? leftStr="-280px" : leftStr="0px"; 
	    $("div#feedback").animate({ left: leftStr }, 500 );
	});
	
	$('div#feedback form input[type="submit"]').click( function() {
		
		if ($('#feedback-email').val() == '' || $('#feedback-message').val() == ''){
			alert('Both the email and message fields are required.');
			return false;
		}
		
		var parent = $('p.feedback-submit');
		parent.after('<div class="message feedback-sending hide"><p>Sending...</p></div>')
		
		$('p.feedback-element').fadeOut(400, function() {
			$('div.feedback-sending').fadeIn();
		});
		
		// Submit the form via Ajax
		$.ajax({
			type: "POST",
			url: feedbackURL,
			data: {
				"email" : $('#feedback-email').val(),
				"message" : $('#feedback-message').val()
			},
			success: function() {
				$('div.feedback-sending').fadeOut(400, function() {
					parent.after('<div class="message hide"><p>Thank you for your feedback.</p></div>').next('.message').fadeIn();
					$(this).remove();
				});
			},
			error: function (XMLHttpRequest, textStatus, errorThrown) {
				parent.after('<div class="message"><p>Something went wrong and your message could not be sent.</p></div>');
				return false;
			}
		});
		
		return false;
	});
});