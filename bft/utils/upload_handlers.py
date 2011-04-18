from django.core.files.uploadhandler import FileUploadHandler, StopUpload
from django.core.cache import cache
from bft import app_settings

#make django validate when file uploads exceed the max upload size
#you can set this to false when you want your web server (APACHE)
# to validate the size of the upload ie-
#  LimitRequestBody 1073741824
#  ErrorDocument 413 http://servername/413error/ 


class UploadProgressCachedHandler(FileUploadHandler):
	"""
	Tracks progress for file uploads.
	The http post request must contain a header or query parameter, 'X-Progress-ID'
	which should contain a unique string to identify the upload to be tracked.
	"""
	
	def __init__(self, request=None):
		super(UploadProgressCachedHandler, self).__init__(request)
		self.progress_id = None
		self.cache_key = None
		self.total_upload = 0

	def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
		self.content_length = content_length
		# FIXME: This doesn't work very well.
		# For right now it is way better to enforce size restriction
		# using apache.  See comment above.
		if app_settings.VALIDATE_UPLOAD_SIZE:
			if self.content_length > app_settings.MAX_UPLOAD_SIZE:
				self.request.META['upload_size_error'] = True
				raise StopUpload(connection_reset=True)
		
		if 'X-Progress-ID' in self.request.GET :
			self.progress_id = self.request.GET['X-Progress-ID']
		elif 'X-Progress-ID' in self.request.META:
			self.progress_id = self.request.META['X-Progress-ID']
		
		if self.progress_id:
			
			self.cache_key = "%s_%s" % (self.request.META['REMOTE_ADDR'], self.progress_id )
			cache.set(self.cache_key, {
				'state': 'uploading',
				'size': self.content_length,
				'received' : 0
			})

	def new_file(self, field_name, file_name, content_type, content_length, charset=None):
		pass

	def receive_data_chunk(self, raw_data, start):
		if self.cache_key:
			data = cache.get(self.cache_key)
			if data:
				data['received'] += self.chunk_size
				cache.set(self.cache_key, data)
		
		return raw_data
	
	def file_complete(self, file_size):
		pass

	def upload_complete(self):
		if self.cache_key:
			data = cache.get(self.cache_key)
			if data:
				data['state'] = 'done'
				cache.set(self.cache_key, data)
