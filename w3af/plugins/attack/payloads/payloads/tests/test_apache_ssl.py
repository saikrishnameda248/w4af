"""
test_apache_ssl.py

Copyright 2012 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import pytest

from w3af.plugins.attack.payloads.payloads.tests.apache_payload_test_helper import ApachePayloadTestHelper
from w3af.plugins.attack.payloads.payload_handler import exec_payload


class test_apache_ssl(ApachePayloadTestHelper):

    @pytest.mark.ci_fails
    @pytest.mark.w3af_moth
    def test_apache_ssl(self):
        result = exec_payload(self.shell, 'apache_ssl', use_api=True)
        self.assertEqual(1, len(result['apache_ssl_certificate']))
        self.assertIn('/etc/ssl/certs/ssl-cert-snakeoil.pem', result['apache_ssl_certificate'])
        self.assertEqual(1, len(result['apache_ssl_key']))
        self.assertIn('/etc/ssl/certs/ssl-cert-snakeoil.pem', result['apache_ssl_certificate'])
