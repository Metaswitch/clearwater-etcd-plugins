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

    CASSANDRA_YAML_TEMPLATE = "/usr/share/clearwater/cassandra/cassandra.yaml.template"
    CASSANDRA_YAML_FILE = "/etc/cassandra/cassandra.yaml"
    CASSANDRA_TOPOLOGY_FILE = "/etc/cassandra/cassandra-rackdc.properties"

    def __init__(self, params):
        self._ip = params.ip
        self._local_site = params.local_site
        self._remote_seeds = params.remote_cassandra_seeds
        self._sig_namespace = params.signaling_namespace
        self._key = "/{}/{}/clustering/cassandra".format(params.etcd_key, params.etcd_cluster_key)
        self._clustering_alarm = alarm_manager.get_alarm(
            'cluster-manager',
            alarm_constants.CASSANDRA_NOT_YET_CLUSTERED)
        pdlogs.NOT_YET_CLUSTERED_ALARM.log(cluster_desc=self.cluster_description())

    # Interface-defined plugin functions

    def key(self):
        return self._key

    def cluster_description(self):
        return "Cassandra cluster"

    def on_startup(self, cluster_view):
        if os.path.exists("/etc/clearwater/force_cassandra_yaml_refresh"):
            seeds = self.get_seeds(cluster_view)
            if seeds:
                self.write_new_cassandra_config(seeds)

    def on_cluster_changing(self, cluster_view):
        _log.debug("Raising Cassandra not-clustered alarm")
        self._clustering_alarm.set()

    def on_joining_cluster(self, cluster_view):
        _log.debug("Raising Cassandra not-clustered alarm")
        self._clustering_alarm.set()
        self.join_cassandra_cluster(cluster_view)

        if (self._ip == sorted(cluster_view.keys())[0]):
            _log.debug("Adding schemas")
            run_command("/usr/share/clearwater/infrastructure/scripts/cassandra_schemas/run_cassandra_schemas")

    def on_new_cluster_config_ready(self, cluster_view):
        _log.debug("Raising Cassandra not-clustered alarm")
        self._clustering_alarm.set()

    def on_stable_cluster(self, cluster_view):
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
        with open(self.CASSANDRA_YAML_TEMPLATE) as f:
            doc = yaml.load(f)

        # Fill in the correct listen_address and seeds values in the yaml
        # document.
        doc["listen_address"] = self._ip

        # Set the thrift listen address to the IPv4 or IPv6 loopback address
        # as appropriate. Note we can't use 0.0.0.0 in both cases because in
        # a pure IPv6 namespace clients will only try to connect to IPv6
        # addresses. Ideally, we'd listen on both addresses.
        if ip_is_v6:
            rpc_address = '::0'
        else:
            rpc_address = '0.0.0.0'

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

        contents = WARNING_HEADER + "\n" + yaml.dump(doc)
        topology = WARNING_HEADER + "\n" + "dc={}\nrack=RAC1\n".format(self._local_site)

        # Restart Cassandra and make sure it picks up the new list of seeds.
        _log.info("Restarting Cassandra")

        # Remove the cassandra.yaml file first - Cassandra won't start up while
        # it's missing, so this keeps it stopped while we're clearing out its
        # database
        if os.path.exists(self.CASSANDRA_YAML_FILE):
            os.remove(self.CASSANDRA_YAML_FILE)
        
        # Stop Cassandra directly rather than going through any 'service'
        # commands - this should mean that supervisord keeps restarting
        # Cassandra when running in Docker.
        #
        # Note that we can't use the init.d script here, because cassandra.yaml
        # doesn't exist so it immediately exits.
        run_command("start-stop-daemon -K -p /var/run/cassandra/cassandra.pid -R TERM/30/KILL/5")
        
        _log.info("Stopped Cassandra while changing config files")

        if destructive_restart:
            _log.warn("Deleting /var/lib/cassandra - this is normal on initial clustering")
            run_command("rm -rf /var/lib/cassandra/")
            run_command("mkdir -m 755 /var/lib/cassandra")
            run_command("chown -R cassandra /var/lib/cassandra")

        # Write back to cassandra.yaml - this allows Cassandra to start again.
        safely_write(self.CASSANDRA_TOPOLOGY_FILE, topology)
        safely_write(self.CASSANDRA_YAML_FILE, contents)
        self.wait_for_cassandra()

        if os.path.exists("/etc/clearwater/force_cassandra_yaml_refresh"):
            os.remove("/etc/clearwater/force_cassandra_yaml_refresh")

    def get_seeds(self, cluster_view):
        seeds_list = []

        for seed, state in cluster_view.items():
            if (state == constants.NORMAL_ACKNOWLEDGED_CHANGE or
                state == constants.NORMAL_CONFIG_CHANGED or
                state == constants.NORMAL):
                seeds_list.append(seed)

        if len(seeds_list) == 0:
            for seed, state in cluster_view.items():
                if (state == constants.JOINING_ACKNOWLEDGED_CHANGE or
                    state == constants.JOINING_CONFIG_CHANGED):
                    seeds_list.append(seed)
            seeds_list = seeds_list + self._remote_seeds
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
        rc = run_command("/usr/share/clearwater/bin/poll_cassandra.sh --no-grace-period", log_error=False)
        return (rc == 0)

    def leave_cassandra_cluster(self):
        # We need Cassandra to be running so that we can connect on port 9160 and
        # decommission it. Check if we can connect on port 9160.
        if not self.can_contact_cassandra():
            self.wait_for_cassandra()

        # Remove the cassandra.yaml file first - Cassandra won't start up while
        # it's missing, so this prevents monit or supervisord from
        # auto-restarting it after decommissioning.
        if os.path.exists(self.CASSANDRA_YAML_FILE):
            os.remove(self.CASSANDRA_YAML_FILE)
 
        run_command("nodetool decommission", self._sig_namespace)

    def wait_for_cassandra(self):
        # Don't start Cassandra, just rely on monit or supervisord to start it
        # - this avoids race conditions where both we and monit start it at the
        # same time and two copies start up.

        _log.info("Waiting for Cassandra to come up...")
        # Wait until we can connect on port 9160 - i.e. Cassandra is running.
        attempts = 0;
        while not self.can_contact_cassandra():
            # Sleep so we don't tight loop
            time.sleep(1)
            attempts += 1
            if ((attempts % 10) == 0):
                _log.info("Still waiting for Cassandra to come up...")

        _log.info("Finished waiting for Cassandra to come up")
        # Restart clearwater-infrastructure so any necessary schema creation
        # scripts get run
        run_command("sudo service clearwater-infrastructure restart")


def load_as_plugin(params):
    return CassandraPlugin(params)
