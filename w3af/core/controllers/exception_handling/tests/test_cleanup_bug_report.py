"""
test_cleanup_bug_report.py

Copyright 2012 Andres Riancho

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

import w4af.core.data.kb.config as cf
from w4af.core.controllers.exception_handling.cleanup_bug_report import cleanup_bug_report
from w4af.core.data.parsers.doc.url import URL


class TestCleanupBugReport(unittest.TestCase):
    
    def test_cleanup_bug_report_simple(self):
        TESTS = [
                 ('foo', 'foo'),
                 ('start /home/nsa/w4af/ end', 'start /home/user/w4af/ end'),
                 ('start C:\\Documents and Settings\\CIA\\ end',
                  'start C:/user/ end'),
                 ]
        for _input, _expected in TESTS:
            self.assertEqual(cleanup_bug_report(_input), _expected)

    def test_url_cleanup_no_path(self):
    
        target_url = URL('http://www.target.com/')
        cf.cf.save('targets', [target_url,] )
        self.assertEqual(cleanup_bug_report('start http://www.target.com/ end'),
                         'start http://domain/ end')
        
    def test_url_cleanup_with_path(self):
    
        target_url = URL('http://www.target.com/abc/')
        cf.cf.save('targets', [target_url,] )
        self.assertEqual(cleanup_bug_report('start http://www.target.com/abc/def end'),
                         'start http://domain/path/foo/def end')
