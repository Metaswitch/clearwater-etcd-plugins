# Copyright (C) Metaswitch Networks
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

from metaswitch.clearwater.cluster_manager.plugin_base import SynchroniserPluginBase
from metaswitch.clearwater.etcd_shared.plugin_utils import run_command
from metaswitch.common.alarms import alarm_manager
from metaswitch.clearwater.cluster_manager import pdlogs, alarm_constants
import logging

from os import sys, path
sys.path.append(path.dirname(path.abspath(__file__)))
from memcached_utils import write_memcached_cluster_settings

_log = logging.getLogger("memcached_plugin")


class MemcachedPlugin(SynchroniserPluginBase):
    def __init__(self, params):
        pdlogs.NOT_YET_CLUSTERED_ALARM.log(cluster_desc=self.cluster_description())
        self._alarm = alarm_manager.get_alarm(
            'cluster-manager',
            alarm_constants.MEMCACHED_NOT_YET_CLUSTERED)
        self._key = "/{}/{}/{}/clustering/memcached".format(params.etcd_key, params.local_site, params.etcd_cluster_key)

    def key(self):  # pragma: no cover
        return self._key

    def files(self):  # pragma: no cover
        return ["/etc/clearwater/cluster_settings"]

    def cluster_description(self):  # pragma: no cover
        return "local Memcached cluster"

    def on_cluster_changing(self, cluster_view):  # pragma: no cover
        self._alarm.set()
        self.write_cluster_settings(cluster_view)

    def on_joining_cluster(self, cluster_view):  # pragma: no cover
        self._alarm.set()
        self.write_cluster_settings(cluster_view)

    def on_new_cluster_config_ready(self, cluster_view):  # pragma: no cover
        self._alarm.set()
        run_command(["service", "astaire", "reload"])
        run_command(["service", "astaire", "wait-sync"])

    def on_stable_cluster(self, cluster_view):  # pragma: no cover
        self.write_cluster_settings(cluster_view)
        self._alarm.clear()
        pdlogs.STABLE_CLUSTER.log(cluster_desc=self.cluster_description())

    def on_leaving_cluster(self, cluster_view):  # pragma: no cover
        pass

    def write_cluster_settings(self, cluster_view):
        write_memcached_cluster_settings("/etc/clearwater/cluster_settings",
                                         cluster_view)
        run_command(["/usr/share/clearwater/bin/reload_memcached_users"])

def load_as_plugin(params):  # pragma: no cover
    _log.info("Loading the Memcached plugin")
    return MemcachedPlugin(params)
