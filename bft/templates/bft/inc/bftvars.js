var staticURL = "{{ STATIC_URL }}";
var absStaticURL = "{{ abs_static_url }}";
var flashURL = "{% url flash_upload %}";
var progressURL = "{% url progress %}";
var captchaURL = "{% url captcha %}";
var captchaKey = "{{ recaptcha_pub_key }}"
var submissionSlug;
var submissionURL;
var flashQueue = 0;
var flashTotalBytes = 0;
var uploadSizeLimit = {{ upload_size_limit }};
var uploadType = "email";
var uploadServerError = 'There was an error processing your request. This might be due to your file(s) exceeding the allowed limit.<br />If you are sure that the file is below the limit, please contact <a href="mailto:{{ reply_email }}">{{ reply_email }}</a> for help.';
var browserError = 'There was an error processing your request with the browser that you are using.  This might be due to an outdated browser.  Please make sure that you are using the latest version of your browser.<br />If you have additional questions, please contact <a href="mailto:{{ reply_email }}">{{ reply_email }}</a> for help.'
var useFlash = "{{ use_flash }}"
var useCaptcha = "{{ use_captcha }}"
var formValid = false;
