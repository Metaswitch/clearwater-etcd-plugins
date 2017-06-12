# @file chronos_plugin.py
#
# Copyright (C) Metaswitch Networks
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

from textwrap import dedent
from metaswitch.clearwater.cluster_manager.plugin_base import SynchroniserPluginBase
from metaswitch.clearwater.cluster_manager.plugin_utils import WARNING_HEADER
from metaswitch.common.alarms import alarm_manager
from metaswitch.clearwater.cluster_manager import pdlogs, alarm_constants, constants
from metaswitch.clearwater.etcd_shared.plugin_utils import run_command, safely_write
import logging

_log = logging.getLogger("chronos_plugin")

def write_chronos_cluster_settings(filename, cluster_view, current_server, instance_id, deployment_id):
    joining = [constants.JOINING_ACKNOWLEDGED_CHANGE,
               constants.JOINING_CONFIG_CHANGED]
    staying = [constants.NORMAL_ACKNOWLEDGED_CHANGE,
               constants.NORMAL_CONFIG_CHANGED,
               constants.NORMAL]
    leaving = [constants.LEAVING_ACKNOWLEDGED_CHANGE,
               constants.LEAVING_CONFIG_CHANGED]

    joining_servers = ([k for k, v in cluster_view.iteritems()
                        if v in joining])
    staying_servers = ([k for k, v in cluster_view.iteritems()
                        if v in staying])
    leaving_servers = ([k for k, v in cluster_view.iteritems()
                        if v in leaving])

    contents = dedent('''\
        {}
        [identity]
        instance_id = {}
        deployment_id = {}

        [cluster]
        localhost = {}
        ''').format(WARNING_HEADER, instance_id, deployment_id, current_server)

    for node in joining_servers:
        contents += 'joining = {}\n'.format(node)
    for node in staying_servers:
        contents += 'node = {}\n'.format(node)
    for node in leaving_servers:
        contents += 'leaving = {}\n'.format(node)

    safely_write(filename, contents)

class ChronosPlugin(SynchroniserPluginBase):
    def __init__(self, params):
        self.local_server = params.ip
        uuid_bytes = params.uuid.bytes

        # Extract a 7-bit instance ID and a three-bit deployment ID from the
        # UUID.
        self.instance_id = ord(uuid_bytes[0]) & 0b0111111
        self.deployment_id = ord(uuid_bytes[1]) & 0b00000111
        if self.instance_id > 127 or self.deployment_id > 7:  # pragma: no cover
            _log.error("instance_id/deployment_id are out of expected range - %d and %d (max should be 127 and 7)", self.instance_id, self.deployment_id)
        self._key = "/{}/{}/{}/clustering/chronos".format(params.etcd_key, params.local_site, params.etcd_cluster_key)
        self._alarm = alarm_manager.get_alarm(
            'cluster-manager',
            alarm_constants.CHRONOS_NOT_YET_CLUSTERED)
        pdlogs.NOT_YET_CLUSTERED_ALARM.log(cluster_desc=self.cluster_description())

    def key(self):  # pragma: no cover
        return self._key

    def files(self):  # pragma: no cover
        return ["/etc/chronos/chronos_cluster.conf"]

    def cluster_description(self):
        return "local Chronos cluster"

    def on_cluster_changing(self, cluster_view):  # pragma: no cover
        self._alarm.set()
        self.write_cluster_settings(cluster_view)

    def on_joining_cluster(self, cluster_view):  # pragma: no cover
        self._alarm.set()
        self.write_cluster_settings(cluster_view)

    def on_new_cluster_config_ready(self, cluster_view):  # pragma: no cover
        self._alarm.set()
        run_command("service chronos resync")
        run_command("service chronos wait-sync")

    def on_stable_cluster(self, cluster_view):  # pragma: no cover
        self.write_cluster_settings(cluster_view)
        self._alarm.clear()
        pdlogs.STABLE_CLUSTER.log(cluster_desc=self.cluster_description())

    def on_leaving_cluster(self, cluster_view):  # pragma: no cover
        pass

    def write_cluster_settings(self, cluster_view):
        write_chronos_cluster_settings("/etc/chronos/chronos_cluster.conf",
                                       cluster_view,
                                       self.local_server,
                                       self.instance_id,
                                       self.deployment_id)
        run_command("service chronos reload")

def load_as_plugin(params):  # pragma: no cover
    _log.info("Loading the Chronos plugin")
    return ChronosPlugin(params)
