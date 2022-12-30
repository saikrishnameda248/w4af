"""
header_link_extract.py

Copyright 2015 Andres Riancho

This file is part of w4af, http://w4af.org/ .

w4af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w4af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w4af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
import re

import w4af.core.controllers.output_manager as om

from w4af.core.data.parsers.doc.cookie_parser import parse_cookie
from w4af.core.data.misc.encoding import smart_unicode

LINK_HEADER_RE = re.compile('<(.*?)>.*')


def extract_link_from_header_simple(http_response, header_name, header_value):
    """
    Extract links from HTTP response headers which have the header value set to
    a link.

    Example headers we can parse:
        x-pingback: http://w4af.org/xmlrpc.php
        location: /foo/

    :param http_response: The http response object
    :param header_name: The http response header name
    :param header_value: The http response header value (where the URL lives)
    :return: Yield URL instances
    :see: https://github.com/andresriancho/w4af/issues/9493
    """
    if not header_value:
        return

    try:
        yield http_response.get_url().url_join(header_value)
    except ValueError:
        msg = ('The application sent a "%s" header that w4af'
               ' failed to correctly parse as an URL, the header'
               ' value was: "%s"')
        om.out.debug(msg % (header_name, header_value))


def extract_link_from_link_header(http_response, header_name, header_value):
    """
    Extract links from HTTP response headers which have the header value set to
    a "wordpress link"

    Example headers we can parse:
        link: <http://w4af.org/?p=4758>; rel=shortlink

    :param http_response: The http response object
    :param header_name: The http response header name
    :param header_value: The http response header value (where the URL lives)
    :return: Yield URL instances
    :see: https://github.com/andresriancho/w4af/issues/9493
    """
    re_match = LINK_HEADER_RE.search(header_value)
    if re_match:
        try:
            url_str = re_match.group(1)
        except IndexError:
            return

        if not url_str:
            return

        try:
            yield http_response.get_url().url_join(url_str)
        except ValueError:
            msg = ('The application sent a "%s" header that w4af'
                   ' failed to correctly parse as an URL, the header'
                   ' value was: "%s"')
            om.out.debug(msg % (header_name, header_value))


def extract_link_from_set_cookie_header(http_response, header_name, header_value):
    """
    Extract links from the "path" key of a cookie

    Example headers we can parse:
        set-cookie: __cfduid=...; path=/; domain=.w4af.org; HttpOnly

    :param http_response: The http response object
    :param header_name: The http response header name
    :param header_value: The http response header value (where the URL lives)
    :return: Yield URL instances
    :see: https://github.com/andresriancho/w4af/issues/9493
    """
    try:
        cookie = parse_cookie(header_value)
    except:
        return

    for key in list(cookie.keys()):
        try:
            path = cookie[key]['path']
        except KeyError:
            continue

        if path:
            try:
                yield http_response.get_url().url_join(path)
            except ValueError:
                msg = ('The application sent a "%s" header that w4af'
                       ' failed to correctly parse as an URL, the header'
                       ' value was: "%s"')
                om.out.debug(msg % (header_name, header_value))


URL_HEADERS = {extract_link_from_header_simple: {'location',
                                                 'uri',
                                                 'content-location',
                                                 'x-pingback'},
               extract_link_from_link_header: {'link'},
               extract_link_from_set_cookie_header: {'set-cookie'}}


def headers_url_generator(resp, fuzzable_req):
    """
    Yields tuples containing:
        * Newly found URL
        * The FuzzableRequest instance passed as parameter
        * The HTTPResponse generated by the FuzzableRequest
        * Boolean indicating if we trust this reference or not

    The newly found URLs are extracted from the http response headers such
    as "Location".

    :param resp: HTTP response object
    :param fuzzable_req: The HTTP request that generated the response
    """
    resp_headers = resp.get_headers()

    for parser, header_names in URL_HEADERS.items():
        for header_name in header_names:

            header_value, _ = resp_headers.iget(header_name, None)
            if header_value is not None:

                header_value = smart_unicode(header_value,
                                             encoding=resp.charset)

                for ref in parser(resp, header_name, header_value):
                    yield ref, fuzzable_req, resp, False
