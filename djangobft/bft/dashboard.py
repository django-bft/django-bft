"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'djangobft.dashboard.CustomIndexDashboard'
"""

# from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from grappelli.dashboard import modules, Dashboard

# from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        # site_name = get_admin_site_name(context)

        # append an app list module for "Administration"
        self.children.append(
            modules.ModelList(
                _("BFT Administration"),
                column=1,
                collapsible=False,
                models=("bft.*",),
            )
        )

        # append an app list module for "Administration"
        self.children.append(
            modules.ModelList(
                _("User Administration"),
                column=1,
                collapsible=False,
                models=("django.contrib.*",),
            )
        )

        # append another link list module for "support".
        self.children.append(
            modules.LinkList(
                _("Log Reporting"),
                column=2,
                collapsible=False,
                children=[
                    {
                        "title": _("BFT Logs"),
                        "url": "/admin/log/",
                        "external": True,
                    },
                ],
            )
        )

        # append another link list module for "support".
        self.children.append(
            modules.LinkList(
                _("Media Management"),
                column=2,
                collapsible=False,
                children=[
                    {
                        "title": _("FileBrowser"),
                        "url": "/admin/filebrowser/browse/",
                        "external": False,
                    },
                ],
            )
        )

        # append a recent actions module
        self.children.append(
            modules.RecentActions(
                _("Recent Actions"),
                limit=5,
                collapsible=False,
                column=2,
            )
        )
