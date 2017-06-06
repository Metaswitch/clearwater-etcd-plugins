# Project Clearwater - IMS in the Cloud
# Copyright (C) 2016  Metaswitch Networks Ltd
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version, along with the "Special Exception" for use of
# the program along with SSL, set forth below. This program is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details. You should have received a copy of the GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
# The author can be reached by email at clearwater@metaswitch.com or by
# post at Metaswitch Networks Ltd, 100 Church St, Enfield EN2 6BQ, UK
#
# Special Exception
# Metaswitch Networks Ltd  grants you permission to copy, modify,
# propagate, and distribute a work formed by combining OpenSSL with The
# Software, or a work derivative of such a combination, even if such
# copying, modification, propagation, or distribution would otherwise
# violate the terms of the GPL. You must comply with the GPL in all
# respects for all of the code used other than OpenSSL.
# "OpenSSL" means OpenSSL toolkit software distributed by the OpenSSL
# Project and licensed under the OpenSSL Licenses, or a work based on such
# software and licensed under the OpenSSL Licenses.
# "OpenSSL Licenses" means the OpenSSL License and Original SSLeay License
# under which the OpenSSL Project distributes the OpenSSL toolkit software,
# as those licenses appear in the file LICENSE-OPENSSL.

from metaswitch.clearwater.queue_manager.plugin_base import QueuePluginBase
from metaswitch.clearwater.etcd_shared.plugin_utils import run_command, safely_write
import logging
import os
import imp

PACKAGES = "cassandra clearwater-cassandra homestead-cassandra homestead-prov-cassandra homer-cassandra memento-cassandra"
SOURCES_FILE = "/etc/apt/sources.list.d/clearwater.list"
UPGRADE_SCRIPT = "/usr/share/clearwater/clearwater-queue-manager/scripts/upgrade_cassandra.py"
VERSION_FILE = "/etc/clearwater/cassandra_version"

_log = logging.getLogger("cassandra_upgrade_plugin")

class CassandraUpgradePlugin(QueuePluginBase):
    def __init__(self, params):
        self._wait_plugin_complete = params.wait_plugin_complete

    def key(self):  # pragma: no cover
        return "cassandra_upgrade"

    def at_front_of_queue(self):
        if os.path.exists(UPGRADE_SCRIPT):
            cass_upgrade = imp.load_source("cass_upgrade", UPGRADE_SCRIPT)
            result = cass_upgrade.do_upgrade()
            if result:
                if self._wait_plugin_complete != "N":
                    _log.info("Checking service health")
                    if run_command("/usr/share/clearwater/clearwater-queue-manager/scripts/check_node_health.py"):
                        _log.info("Services failed to restart successfully")
                        run_command("/usr/share/clearwater/clearwater-queue-manager/scripts/modify_nodes_in_queue remove_failure cassandra_upgrade")
                    else:
                        _log.info("Services restarted successfully")
                        run_command("/usr/share/clearwater/clearwater-queue-manager/scripts/modify_nodes_in_queue remove_success cassandra_upgrade")
                else:
                    _log.info("Not checking service health")
                    run_command("/usr/share/clearwater/clearwater-queue-manager/scripts/modify_nodes_in_queue remove_success cassandra_upgrade")
            else:
                _log.error("Upgrade failed")
                run_command("/usr/share/clearwater/clearwater-queue-manager/scripts/modify_nodes_in_queue remove_failure cassandra_upgrade")
        else:
            _log.info("Nothing to do")
            run_command("/usr/share/clearwater/clearwater-queue-manager/scripts/modify_nodes_in_queue remove_success cassandra_upgrade")


def load_as_plugin(params):  # pragma: no cover
    return CassandraUpgradePlugin(params)
