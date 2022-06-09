from django.conf import settings
from django.http import HttpResponseServerError, HttpResponse
from django.utils import simplejson

class JsonResponse(HttpResponse):
	def __init__(self, data, status=200):
		HttpResponse.__init__(self,
			content=simplejson.dumps(data),
			content_type='application/json; charset=UTF-8',
			status=status
		)
		
class AJAXExceptionResponse:
	def process_exception(self, request, exception):
		if settings.DEBUG:
			if request.is_ajax():
				import sys, traceback
				(exc_type, exc_info, tb) = sys.exc_info()
				response = "%s\n" % exc_type.__name__
				response += "%s\n\n" % exc_info
				response += "TRACEBACK:\n"	
				for tb in traceback.format_tb(tb):
					response += "%s\n" % tb
				return HttpResponseServerError(response)
