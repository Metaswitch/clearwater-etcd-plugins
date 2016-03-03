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
from metaswitch.clearwater.etcd_shared.plugin_utils import run_command, safely_write
from metaswitch.common.alarms import alarm_manager
from metaswitch.clearwater.cluster_manager import pdlogs, alarm_constants, constants
from metaswitch.clearwater.cluster_manager.plugin_utils import WARNING_HEADER
import logging
import time
import yaml
import os
import subprocess
import ipaddress

_log = logging.getLogger("cassandra_plugin")


class CassandraPlugin(SynchroniserPluginBase):

    cassandra_yaml_template = "/usr/share/clearwater/cassandra/cassandra.yaml.template"
    cassandra_yaml_file = "/etc/cassandra/cassandra.yaml"
    cassandra_topology_file = "/etc/cassandra/cassandra-rackdc.properties"

    def __init__(self, params):
        self._ip = params.ip
        self._local_site = params.local_site
        self._sig_namespace = params.signaling_namespace
        self._key = "/{}/{}/clustering/cassandra".format(params.etcd_key, params.etcd_cluster_key)
        _log.debug("Raising Cassandra not-clustered alarm")
        self._clustering_alarm = alarm_manager.get_alarm(
            'cluster-manager',
            alarm_constants.CASSANDRA_NOT_YET_CLUSTERED)
        self._clustering_alarm.set()
        pdlogs.NOT_YET_CLUSTERED_ALARM.log(cluster_desc=self.cluster_description())

    # Interface-defined plugin functions

    def key(self):
        return self._key

    def cluster_description(self):
        return "Cassandra cluster"

    def on_cluster_changing(self, cluster_view):
        pass

    def on_joining_cluster(self, cluster_view):
        self.join_cassandra_cluster(cluster_view)

        if (self._ip == sorted(cluster_view.keys())[0]):
            _log.debug("Adding schemas")
            run_command("/usr/share/clearwater/infrastructure/scripts/cassandra_schemas/run_cassandra_schemas")

    def on_new_cluster_config_ready(self, cluster_view):
        pass

    def on_stable_cluster(self, cluster_view):
        if os.path.exists("/etc/clearwater/force_cassandra_yaml_refresh"):
            self.write_new_cassandra_config(self.get_seeds(cluster_view, self._ip))

        _log.debug("Clearing Cassandra not-clustered alarm")
        self._clustering_alarm.clear()

    def on_leaving_cluster(self, cluster_view):
        decommission_alarm = alarm_manager.get_alarm(
            'cluster-manager',
            alarm_constants.CASSANDRA_NOT_YET_DECOMMISSIONED)
        decommission_alarm.set()
        self.leave_cassandra_cluster()
        decommission_alarm.clear()

    def files(self):
        return ["/etc/cassandra/cassandra.yaml"]

    # Specific methods for handling Cassandra

    def write_new_cassandra_config(self, seeds_list, destructive_restart=False):
        ip_is_v6 = (ipaddress.ip_address(self._ip).version == 6)
        seeds_list_str = ','.join(map(str, seeds_list))
        _log.info("Cassandra seeds list is {}".format(seeds_list_str))

        # Read cassandra.yaml template.
        with open(self.cassandra_yaml_template) as f:
            doc = yaml.load(f)

        # Fill in the correct listen_address and seeds values in the yaml
        # document.
        doc["listen_address"] = self._ip

        # Set the thrift listen address to the IPv4 or IPv6 loopback address
        # as appropriate. Note we can't use 127.0.0.1 in both cases because in
        # a pure IPv6 namespace clients will only try to connect to IPv6
        # addresses.
        if ip_is_v6:
            rpc_address = '::1'
        else:
            rpc_address = '127.0.0.1'

        doc['rpc_address'] = rpc_address

        doc["seed_provider"][0]["parameters"][0]["seeds"] = seeds_list_str
        doc["endpoint_snitch"] = "GossipingPropertyFileSnitch"

        # Work out the timeout from the target_latency_us value (assuming
        # 100000 if it isn't set)
        get_latency_cmd = "target_latency_us=100000; . /etc/clearwater/config; echo -n $target_latency_us"
        latency = subprocess.check_output(get_latency_cmd,
                                          shell=True,
                                          stderr=subprocess.STDOUT)

        try:
            # We want the timeout value to be 4/5ths the maximum acceptable time
            # of a HTTP request (which is 5 * target latency)
            timeout = (int(latency) / 1000) * 4
        except ValueError:
            timeout = 400

        doc["read_request_timeout_in_ms"] = timeout

        # Write back to cassandra.yaml.
        contents = WARNING_HEADER + "\n" + yaml.dump(doc)
        topology = WARNING_HEADER + "\n" + "dc={}\nrack=RAC1\n".format(self._local_site)

        safely_write(self.cassandra_yaml_file, contents)
        safely_write(self.cassandra_topology_file, topology)

        # Restart Cassandra and make sure it picks up the new list of seeds.
        _log.debug("Restarting Cassandra")
        run_command("monit unmonitor -g cassandra")
        run_command("service cassandra stop")
        run_command("killall $(cat /var/lib/cassandra/cassandra.pid)", log_error=False)

        if destructive_restart:
            run_command("rm -rf /var/lib/cassandra/")
            run_command("mkdir -m 755 /var/lib/cassandra")
            run_command("chown -R cassandra /var/lib/cassandra")

        self.start_cassandra()
        os.remove("/etc/clearwater/force_cassandra_yaml_refresh")

    def get_seeds(self, cluster_view):
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
        return seeds_list

    def join_cassandra_cluster(self, cluster_view):
        seeds_list = self.get_seeds(cluster_view)
        if len(seeds_list) > 0:
            self.write_new_cassandra_config(seeds_list,
                                            destructive_restart=True)

            _log.debug("Cassandra node successfully clustered")

        else:
            # Something has gone wrong - the local node should be WAITING_TO_JOIN in
            # etcd (at the very least).
            _log.warning("No Cassandra cluster defined in etcd - unable to join")
            pass

    def can_contact_cassandra(self):
        if os.path.exists("/var/run/cassandra/cassandra.pid"):
            rc = run_command("/usr/share/clearwater/bin/poll_cassandra.sh --no-grace-period")
            return (rc == 0)
        else:
            # Cassandra isn't even running, let alone contactable
            return False

    def leave_cassandra_cluster(self):
        # We need Cassandra to be running so that we can connect on port 9160 and
        # decommission it. Check if we can connect on port 9160.
        if not self.can_contact_cassandra():
            self.start_cassandra()

        run_command("monit unmonitor -g cassandra")
        run_command("nodetool decommission", self._sig_namespace)

    def start_cassandra(self):
        cassandra_not_monitored = True

        # Wait until we can connect on port 9160 - i.e. Cassandra is running.
        while True:
            if cassandra_not_monitored:
                # The monit command can fail because monit is still processing
                # the unmonitor command from before (even though it has
                # finished unmonitoring cassandra)
                rc = run_command("monit monitor -g cassandra")
                cassandra_not_monitored = (rc != 0)
            elif self.can_contact_cassandra():
                break

            # Sleep so we don't tight loop
            time.sleep(1)


def load_as_plugin(params):
    return CassandraPlugin(params)
