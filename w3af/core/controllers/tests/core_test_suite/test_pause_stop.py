"""
test_pause_stop.py

Copyright 2011 Andres Riancho

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
import time
import pprint
from multiprocessing.dummy import Process

from unittest.mock import MagicMock
import pytest

from w4af.core.data.parsers.doc.url import URL
from w4af.core.controllers.w4afCore import w4afCore
from w4af.core.controllers.ci.moth import get_moth_http
import w4af.core.data.kb.knowledge_base as kb
from w4af.core.controllers.misc.factory import factory
from w4af.plugins.tests.helper import create_target_option_list


@pytest.mark.moth
class CountTestMixin(unittest.TestCase):
    PLUGIN = 'w4af.core.controllers.tests.count'
    
    def setUp(self):
        """
        This is a rather complex setUp since I need to create an instance of
        the count.py plugin in memory, without copying it to any plugins
        directory since that would generate issues with other tests.
        """
        self.w4afcore = w4afCore()
        
        target_opts = create_target_option_list(URL(get_moth_http()))
        self.w4afcore.target.set_options(target_opts)

        plugin_inst = factory(self.PLUGIN)
        plugin_inst.set_url_opener(self.w4afcore.uri_opener)
        plugin_inst.set_worker_pool(self.w4afcore.worker_pool)

        self.w4afcore.plugins.plugins['crawl'] = [plugin_inst]
        self.w4afcore.plugins._plugins_names_dict['crawl'] = ['count']
        self.count_plugin = plugin_inst
        
        # Verify env and start the scan
        self.w4afcore.plugins.initialized = True
        self.w4afcore.verify_environment()
        
    def tearDown(self):
        self.w4afcore.quit()
        kb.kb.cleanup()


@pytest.mark.moth
class Testw4afCorePause(CountTestMixin):

    @pytest.mark.ci_fails
    def test_pause_unpause(self):
        """
        Verify that the pause method actually works. In this case, working
        means that the process doesn't send any more HTTP requests, fact
        that is verified with the "fake" count plugin.
        """        
        core_start = Process(target=self.w4afcore.start, name='TestRunner')
        core_start.daemon = True
        core_start.start()
        
        # Let the core start, and the count plugin send some requests.
        time.sleep(5)
        count_before_pause = self.count_plugin.count
        self.assertGreater(self.count_plugin.count, 0)
        
        # Pause and measure
        self.w4afcore.pause(True)
        count_after_pause = self.count_plugin.count
        
        time.sleep(2)
        count_after_sleep = self.count_plugin.count
        
        all_equal = count_before_pause == count_after_pause == count_after_sleep
        
        self.assertTrue(all_equal)

        # Unpause and verify that all requests were sent
        self.w4afcore.pause(False)
        core_start.join()
        
        self.assertEqual(self.count_plugin.count, self.count_plugin.loops)

    @pytest.mark.ci_fails
    def test_pause_stop(self):
        """
        Verify that the pause method actually works. In this case, working
        means that the process doesn't send any more HTTP requests after we,
        pause and that stop works when paused.

        This test seems to be failing @ CircleCI because of a test dependency
        issue. If run alone in your workstation it will PASS, but if run at
        CircleCI the count plugin doesn't seem to start.
        """
        core_start = Process(target=self.w4afcore.start, name='TestRunner')
        core_start.daemon = True
        core_start.start()
        
        # Let the core start, and the count plugin send some requests.
        time.sleep(5)
        count_before_pause = self.count_plugin.count
        self.assertGreater(self.count_plugin.count, 0)
        
        # Pause and measure
        self.w4afcore.pause(True)
        count_after_pause = self.count_plugin.count
        
        time.sleep(2)
        count_after_sleep = self.count_plugin.count
        
        all_equal = count_before_pause == count_after_pause == count_after_sleep
        
        self.assertTrue(all_equal)

        # Unpause and verify that all requests were sent
        self.w4afcore.stop()
        core_start.join()
        
        # No more requests sent after pause
        self.assertEqual(self.count_plugin.count, count_after_sleep)

    @pytest.mark.ci_fails
    def test_stop(self):
        """
        Verify that the stop method actually works. In this case, working
        means that the process doesn't send any more HTTP requests after we
        stop().

        This test seems to be failing @ CircleCI because of a test dependency
        issue. If run alone in your workstation it will PASS, but if run at
        CircleCI the count plugin doesn't seem to start.
        """
        core_start = Process(target=self.w4afcore.start, name='TestRunner')
        core_start.daemon = True
        core_start.start()
        
        # Let the core start, and the count plugin send some requests.
        time.sleep(5)
        count_before_stop = self.count_plugin.count
        self.assertGreater(count_before_stop, 0)
        
        # Stop now,
        self.w4afcore.stop()
        core_start.join()

        count_after_stop = self.count_plugin.count
        
        self.assertEqual(count_after_stop, count_before_stop)

        # TODO: At some point re-active this assertion
        #alive_threads = threading.enumerate()
        #self.assertEqual(len(alive_threads), 0, nice_repr(alive_threads))


class StopCtrlCTest(unittest.TestCase):

    def test_stop_by_keyboardinterrupt(self):
        """
        Verify that the Ctrl+C stops the scan.
        """
        # pylint: disable=E0202
        w4afcore = w4afCore()
        
        mock_call = MagicMock(side_effect=KeyboardInterrupt())
        w4afcore.status.set_current_fuzzable_request = mock_call
        
        target_opts = create_target_option_list(URL(get_moth_http()))
        w4afcore.target.set_options(target_opts)
        
        w4afcore.plugins.set_plugins(['web_spider'], 'crawl')
        #w4afcore.plugins.set_plugins(['console'], 'output')
        
        # Verify env and start the scan
        w4afcore.plugins.init_plugins()
        w4afcore.verify_environment()
        w4afcore.start()


def nice_repr(alive_threads):
    repr_alive = [repr(x) for x in alive_threads][:20]
    repr_alive.sort()
    return pprint.pformat(repr_alive)    