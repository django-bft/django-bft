from django.conf.urls.defaults import *
import app_settings

handler500 = 'bft.views.server_error'

urlpatterns = patterns('bft.views',
    url(r'^feedback/$', 'send_feedback', name='feedback'),
    url(r'^413error/$', 'error_413', name='error413'),
    url(r'^500error/$', 'server_error', name='error500'),

    url(r'^$', 'display_index', name='index'),
    url(r'^noflash/$', 'display_index', { 'use_flash': False }, name='noflash'),

    url(r'^about/$', 'display_about', name='about'),
    
    url(r'^files/(?P<submission_slug>[%s]{%s})/$' % (
        app_settings.RANDOMSLUG_CHARS, 
        app_settings.RANDOMSLUG_CHAR_NO), 
        'list_files', 
        name='files'
    ),
    url(r'^process/$', 'process_submission', name='process'),
    
    url(r'^flash/upload/$', 'upload_flash', name='flash_upload'),
    url(r'^captcha/$', 'submit_captcha', name='captcha'),
    url(r'^progress/$', 'html_progress', name='progress'),

    url(r'^bftvars.js/$', 'render_vars'),

    url(r'^(?P<file_slug>[%s]{%s})/$' % (
        app_settings.RANDOMSLUG_CHARS, 
        app_settings.RANDOMSLUG_CHAR_NO), 
        'get_file', 
        name='file'
    ),
    url(r'^(?P<file_slug>[%s]{%s})/(?P<file_name>.*)$' % (
        app_settings.RANDOMSLUG_CHARS, 
        app_settings.RANDOMSLUG_CHAR_NO), 
        'get_file', 
        name='file'
    ),
)
