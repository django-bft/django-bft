from saml2 import (
    BINDING_HTTP_POST,
    BINDING_HTTP_REDIRECT,
    entity,
)
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config

from django import get_version
from pkg_resources import parse_version
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme


if parse_version(get_version()) >= parse_version("1.7"):
    from django.utils.module_loading import import_string
else:
    from django.utils.module_loading import import_by_path as import_string


def _default_next_url():
    if "DEFAULT_NEXT_URL" in settings.SAML2_AUTH:
        return settings.SAML2_AUTH["DEFAULT_NEXT_URL"]
    # Lazily evaluate this in case we don't have admin loaded.
    return get_reverse("index")


def get_current_domain(request):
    if "ASSERTION_URL" in settings.SAML2_AUTH:
        return settings.SAML2_AUTH["ASSERTION_URL"]
    return "{scheme}://{host}".format(
        scheme="https" if request.is_secure() else "http",
        host=request.get_host(),
    )


def get_reverse(objs):
    """In order to support different django version, I have to do this"""
    if parse_version(get_version()) >= parse_version("2.0"):
        from django.urls import reverse
    else:
        from django.core.urlresolvers import reverse
    if objs.__class__.__name__ not in ["list", "tuple"]:
        objs = [objs]

    for obj in objs:
        try:
            return reverse(obj)
        except Exception:
            pass
    raise Exception("We got a URL reverse issue." % str(objs))


def _get_metadata():
    if "METADATA_LOCAL_FILE_PATH" in settings.SAML2_AUTH:
        return {"local": [settings.SAML2_AUTH["METADATA_LOCAL_FILE_PATH"]]}
    else:
        return {
            "remote": [
                {
                    "url": settings.SAML2_AUTH["METADATA_AUTO_CONF_URL"],
                },
            ]
        }


def _get_saml_client(domain):
    acs_url = domain + get_reverse([acs, "acs", "acs"])
    metadata = _get_metadata()

    saml_settings = {
        "metadata": metadata,
        "service": {
            "sp": {
                "endpoints": {
                    "assertion_consumer_service": [
                        (acs_url, BINDING_HTTP_REDIRECT),
                        (acs_url, BINDING_HTTP_POST),
                    ],
                },
                "allow_unsolicited": True,
                "authn_requests_signed": False,
                "logout_requests_signed": True,
                "want_assertions_signed": True,
                "want_response_signed": False,
            },
        },
    }

    if "ENTITY_ID" in settings.SAML2_AUTH:
        saml_settings["entityid"] = settings.SAML2_AUTH["ENTITY_ID"]

    if "NAME_ID_FORMAT" in settings.SAML2_AUTH:
        saml_settings["service"]["sp"]["name_id_format"] = settings.SAML2_AUTH["NAME_ID_FORMAT"]

    spConfig = Saml2Config()
    spConfig.load(saml_settings)
    spConfig.allow_unknown_attributes = True
    saml_client = Saml2Client(config=spConfig)
    return saml_client


def denied(request):
    messages.add_message(request, messages.ERROR, "Authentication unsuccessful.")
    return redirect("login")


@csrf_exempt
def acs(request):
    saml_client = _get_saml_client(get_current_domain(request))
    resp = request.POST.get("SAMLResponse", None)
    next_url = request.session.get("login_next_url", _default_next_url())
    # If relayState params is passed, use that else consider the previous 'next_url'
    next_url = request.POST.get('RelayState', next_url)
    if not resp:
        return HttpResponseRedirect(get_reverse([denied, "denied", "denied"]))

    authn_response = saml_client.parse_authn_request_response(resp, entity.BINDING_HTTP_POST)
    if authn_response is None:
        return HttpResponseRedirect(get_reverse([denied, "denied", "denied"]))

    user_identity = authn_response.get_identity()
    if user_identity is None:
        return HttpResponseRedirect(get_reverse([denied, "denied", "denied"]))

    user_name = user_identity[settings.SAML2_AUTH.get("ATTRIBUTES_MAP", {}).get("username", "UserName")][0]

    request.session["bft_auth"] = user_name
    return HttpResponseRedirect(next_url)


def signin(request):
    import urllib.parse as _urlparse
    from urllib.parse import unquote

    next_url = request.GET.get("next", _default_next_url())

    try:
        if "next=" in unquote(next_url):
            next_url = _urlparse.parse_qs(_urlparse.urlparse(unquote(next_url)).query)["next"][0]
    except Exception:
        next_url = request.GET.get("next", _default_next_url())

    # Only permit signin requests where the next_url is a safe URL
    if parse_version(get_version()) >= parse_version("2.0"):
        url_ok = url_has_allowed_host_and_scheme(next_url, None)
    else:
        url_ok = url_has_allowed_host_and_scheme(next_url)

    if not url_ok:
        return HttpResponseRedirect(get_reverse([denied, "denied", "denied"]))

    request.session["login_next_url"] = next_url
    saml_client = _get_saml_client(get_current_domain(request))
    _, info = saml_client.prepare_for_authenticate(relay_state=next_url)

    redirect_url = None

    for key, value in info["headers"]:
        if key == "Location":
            redirect_url = value
            break
    print(f"redirect: {redirect_url}")
    return HttpResponseRedirect(redirect_url)


def signout(request):
    logout(request)
    return redirect("logout")
