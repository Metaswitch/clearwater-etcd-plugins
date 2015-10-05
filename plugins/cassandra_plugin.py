#@file cassandra_plugin.py
#
# Project Clearwater - IMS in the Cloud
# Copyright (C) 2015  Metaswitch Networks Ltd
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

from metaswitch.clearwater.cluster_manager.plugin_base import SynchroniserPluginBase
from metaswitch.clearwater.etcd_shared.plugin_utils import run_command
from metaswitch.clearwater.cluster_manager.alarms import issue_alarm
from metaswitch.clearwater.cluster_manager import pdlogs, alarm_constants, constants
from metaswitch.clearwater.cluster_manager.plugin_utils import WARNING_HEADER
import logging
import time
import yaml
import os

_log = logging.getLogger("cassandra_plugin")

def join_cassandra_cluster(cluster_view,
                           cassandra_yaml_file,
                           cassandra_topology_file,
                           ip,
                           site_name):
    seeds_list = []

    for seed, state in cluster_view.items():
        if (state == constants.NORMAL_ACKNOWLEDGED_CHANGE or
            state == constants.NORMAL_CONFIG_CHANGED):
            seeds_list.append(seed)

    if len(seeds_list) == 0:
        for seed, state in cluster_view.items():
            if (state == constants.JOINING_ACKNOWLEDGED_CHANGE or
                state == constants.JOINING_CONFIG_CHANGED):
                seeds_list.append(seed)

    if len(seeds_list) > 0:
        seeds_list_str = ','.join(map(str, seeds_list))
        _log.info("Cassandra seeds list is {}".format(seeds_list_str))
    
        # Read cassandra.yaml.
        with open(cassandra_yaml_file) as f:
            doc = yaml.load(f)

        # Fill in the correct listen_address and seeds values in the yaml
        # document.
        doc["listen_address"] = ip
        doc["seed_provider"][0]["parameters"][0]["seeds"] = seeds_list_str
        doc["endpoint_snitch"] = "GossipingPropertyFileSnitch"

        # Write back to cassandra.yaml.
        with open(cassandra_yaml_file, "w") as f:
            f.write(WARNING_HEADER + "\n")
            yaml.dump(doc, f)

        topology = WARNING_HEADER + "\n" + "dc={}\nrack=RAC1\n".format(site_name)

        with open(cassandra_topology_file, "w") as f:
            f.write(topology)

        # Restart Cassandra and make sure it picks up the new list of seeds.
        _log.debug("Restarting Cassandra")
        run_command("monit unmonitor -g cassandra")
        run_command("service cassandra stop")
        run_command("killall $(cat /var/lib/cassandra/cassandra.pid)", log_error=False)
        run_command("rm -rf /var/lib/cassandra/")
        run_command("mkdir -m 755 /var/lib/cassandra")
        run_command("chown -R cassandra /var/lib/cassandra")

        start_cassandra()

        _log.debug("Cassandra node successfully clustered")

    else:
        # Something has gone wrong - the local node should be WAITING_TO_JOIN in
        # etcd (at the very least).
        _log.warning("No Cassandra cluster defined in etcd - unable to join")
        pass

def can_contact_cassandra():
    if os.path.exists("/var/run/cassandra/cassandra.pid"):
        rc = run_command("/usr/share/clearwater/bin/poll_cassandra.sh --no-grace-period")
        return (rc == 0)
    else:
        # Cassandra isn't even running, let alone contactable
        return False

def leave_cassandra_cluster(namespace=None):
    # We need Cassandra to be running so that we can connect on port 9160 and
    # decommission it. Check if we can connect on port 9160.
    if not can_contact_cassandra():
        start_cassandra()

    run_command("monit unmonitor -g cassandra")
    run_command("nodetool decommission", namespace)


def start_cassandra():
    cassandra_not_monitored = True

    # Wait until we can connect on port 9160 - i.e. Cassandra is running.
    while True:
        if cassandra_not_monitored:
            # The monit command can fail because monit is still processing
            # the unmonitor command from before (even though it has
            # finished unmonitoring cassandra)
            rc = run_command("monit monitor -g cassandra")
            cassandra_not_monitored = (rc != 0)
        elif can_contact_cassandra():
            break

        # Sleep so we don't tight loop
        time.sleep(1)

class CassandraPlugin(SynchroniserPluginBase):
    def __init__(self, params):
        self._ip = params.ip
        self._local_site = params.local_site
        self._sig_namespace = params.signaling_namespace
        self._key = "/{}/{}/clustering/cassandra".format(params.etcd_key, params.etcd_cluster_key)
        _log.debug("Raising Cassandra not-clustered alarm")
        issue_alarm(alarm_constants.CASSANDRA_NOT_YET_CLUSTERED_MAJOR)
        pdlogs.NOT_YET_CLUSTERED_ALARM.log(cluster_desc=self.cluster_description())

    def key(self):
        return self._key

    def cluster_description(self):
        return "Cassandra cluster"

    def on_cluster_changing(self, cluster_view):
        pass

    def on_joining_cluster(self, cluster_view):
        join_cassandra_cluster(cluster_view,
                               "/etc/cassandra/cassandra.yaml",
                               "/etc/cassandra/cassandra-rackdc.properties",
                               self._ip,
                               self._local_site)

        if (self._ip == sorted(cluster_view.keys())[0]):
            _log.debug("Adding schemas")
            run_command("/usr/share/clearwater/infrastructure/scripts/cassandra_schemas/run_cassandra_schemas")

        _log.debug("Clearing Cassandra not-clustered alarm")
        issue_alarm(alarm_constants.CASSANDRA_NOT_YET_CLUSTERED_CLEARED)

    def on_new_cluster_config_ready(self, cluster_view):
        pass

    def on_stable_cluster(self, cluster_view):
        pass

    def on_leaving_cluster(self, cluster_view):
        issue_alarm(alarm_constants.CASSANDRA_NOT_YET_DECOMMISSIONED_MAJOR)
        leave_cassandra_cluster(self._sig_namespace)
        issue_alarm(alarm_constants.CASSANDRA_NOT_YET_DECOMMISSIONED_CLEARED)

    def files(self):
        return ["/etc/cassandra/cassandra.yaml"]


def load_as_plugin(params):
    return CassandraPlugin(params)
