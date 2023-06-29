let submissionSlug;
let flashQueue = 0;
let uploadSizeLimit = "{{ upload_size_limit }}";
let uploadType = "email";
let uploadServerError = 'There was an error processing your request. This might be due to your file(s) exceeding the allowed limit.<br />If you are sure that the file is below the limit, please contact <a href="mailto:{{ reply_email }}">{{ reply_email }}</a> for help.';
let browserError = 'There was an error processing your request with the browser that you are using.  This might be due to an outdated browser.  Please make sure that you are using the latest version of your browser.<br />If you have additional questions, please contact <a href="mailto:{{ reply_email }}">{{ reply_email }}</a> for help.';
let formValid = false;
let csrfToken = "{{ csrf_token_value }}";