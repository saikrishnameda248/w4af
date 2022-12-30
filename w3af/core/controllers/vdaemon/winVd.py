"""
winVd.py

Copyright 2006 Andres Riancho

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

import time

from w4af.core.controllers.vdaemon.vdaemon import vdaemon
import w4af.core.controllers.output_manager as om

from w4af.core.controllers.intrusion_tools.atHandler import atHandler


class winVd(vdaemon):
    """
    This class represents a windows virtual daemon, a point of entry for metasploit plugins to exploit web applications.

    :author: Andres Riancho (andres.riancho@gmail.com)
    """
    def _clean_up(self):
        """
        Removes the created file and the crontab entry.
        """
        self._exec('del ' + self._remote_filename)
        self._exec('del ' + self._remote_filename + '._')

    def _exec_payload(self):
        """
        This method should be implemented according to the remote operating system. The idea here is to
        execute the payload that was sent using _sendExeToServer and generated by _generateExe . In winVd
        I should add self._filename to the crontab .

        This method should be implemented in winVd and winVd.
        """
        aH = atHandler(self._exec_method)
        if not aH.can_delay():
            om.out.information('Remote user is not allowed to run at! Running command without at, this may cause a timeout.')
            self._exec(self._remote_filename)
        else:
            wait_time = aH.add_to_schedule(self._remote_filename)

            om.out.console('"at" entry successfully added. Waiting for shellcode execution.')
            time.sleep(wait_time + 3)

            om.out.console(
                'Payload successfully executed, restoring old "at".')
            aH.restore_old_schedule()

            om.out.debug(
                'All done, check metasploit handler console for results.')

    def get_os(self):
        return 'windows'
