"""
test_content_sniffing.py

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
import unittest

import w4af.core.data.kb.knowledge_base as kb
from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.request.fuzzable_request import FuzzableRequest
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.dc.headers import Headers
from w4af.core.controllers.misc.temp_dir import create_temp_dir
from w4af.plugins.grep.content_sniffing import content_sniffing


class TestContentSniffingSecurity(unittest.TestCase):

    def setUp(self):
        create_temp_dir()
        self.plugin = content_sniffing()

    def tearDown(self):
        self.plugin.end()
        kb.kb.cleanup()

    def test_has_content_sniffing_header(self):
        body = ''
        url = URL('http://www.w4af.com/')
        headers = Headers([('content-type', 'text/html'),
                           ('X-Content-Type-Options', 'nosniff')])
        request = FuzzableRequest(url, method='GET')
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        self.plugin.grep(request, resp)
        self.assertEqual(len(kb.kb.get('content_sniffing',
                                        'content_sniffing')), 0)

    def test_no_content_sniffing(self):
        body = ''
        url = URL('https://www.w4af.com/')
        headers = Headers([('content-type', 'text/html')])
        request = FuzzableRequest(url, method='GET')
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        self.plugin.grep(request, resp)

        findings = kb.kb.get('content_sniffing', 'content_sniffing')
        self.assertEqual(len(findings), 1, findings)

        info_set = findings[0]
        expected_desc = 'The remote web application sent 1 HTTP responses' \
                        ' which do not contain the X-Content-Type-Options' \
                        ' header. The first ten URLs which did not send the' \
                        ' header are:\n - https://www.w4af.com/\n'

        self.assertEqual(info_set.get_id(), [1])
        self.assertEqual(info_set.get_desc(), expected_desc)
        self.assertEqual(info_set.get_name(),
                         'Missing X-Content-Type-Options header')

    def test_no_content_sniffing_group_by_domain(self):
        body = ''
        url = URL('https://www.w4af.com/1')
        headers = Headers([('content-type', 'text/html')])
        request = FuzzableRequest(url, method='GET')
        resp = HTTPResponse(200, body, headers, url, url, _id=1)

        self.plugin.grep(request, resp)

        body = ''
        url = URL('https://www.w4af.com/2')
        headers = Headers([('content-type', 'text/html')])
        request = FuzzableRequest(url, method='GET')
        resp = HTTPResponse(200, body, headers, url, url, _id=2)

        self.plugin.grep(request, resp)

        findings = kb.kb.get('content_sniffing',
                             'content_sniffing')
        self.assertEqual(len(findings), 1, findings)

        info_set = findings[0]
        expected_desc = 'The remote web application sent 2 HTTP responses' \
                        ' which do not contain the X-Content-Type-Options' \
                        ' header. The first ten URLs which did not send the' \
                        ' header are:\n - https://www.w4af.com/1\n' \
                        ' - https://www.w4af.com/2\n'

        self.assertEqual(info_set.get_id(), [1, 2])
        self.assertEqual(info_set.get_desc(), expected_desc)
        self.assertEqual(info_set.get_name(),
                         'Missing X-Content-Type-Options header')
