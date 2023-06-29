from django.urls import path, re_path
from . import views, auth
from .app_settings import CONFIG as app_settings

handler500 = views.server_error

urlpatterns = [
    path("feedback/", views.send_feedback, name="feedback"),
    path("413error/", views.error_413, name="error413"),
    path("500error/", views.server_error, name="error500"),
    path("", views.display_index, name="index"),
    path("about/", views.display_about, name="about"),
    path("login/", views.login_user, name="login"),
    path("acs/", auth.acs, name="acs"),
    path("denied/", auth.denied, name="denied"),
    re_path(
        r"^files/(?P<submission_slug>[%s]{%s})/$" % (app_settings.RANDOMSLUG_CHARS, app_settings.RANDOMSLUG_CHAR_NO),
        views.list_files,
        name="files",
    ),
    re_path(
        r"^file-list/(?P<submission_slug>[%s]{%s})/$"
        % (app_settings.RANDOMSLUG_CHARS, app_settings.RANDOMSLUG_CHAR_NO),
        views.list_files,
        name="files-list",
    ),
    path("process/", views.process_submission, name="process"),
    path("upload/", views.upload, name="upload"),
    path("bftvars.js/", views.render_vars),
    re_path(
        r"^(?P<file_slug>[%s]{%s})/$" % (app_settings.RANDOMSLUG_CHARS, app_settings.RANDOMSLUG_CHAR_NO),
        views.get_file,
        name="file",
    ),
    re_path(
        r"^(?P<file_slug>[%s]{%s})/(?P<file_name>.*)$"
        % (app_settings.RANDOMSLUG_CHARS, app_settings.RANDOMSLUG_CHAR_NO),
        views.get_file,
        name="file",
    ),
    re_path(
        r"^file/(?P<file_slug>[%s]{%s})/$" % (app_settings.RANDOMSLUG_CHARS, app_settings.RANDOMSLUG_CHAR_NO),
        views.get_file,
        name="file-old",
    ),
    re_path(
        r"^file/(?P<file_slug>[%s]{%s})/(?P<file_name>.*)$"
        % (app_settings.RANDOMSLUG_CHARS, app_settings.RANDOMSLUG_CHAR_NO),
        views.get_file,
        name="file-old",
    ),
]
