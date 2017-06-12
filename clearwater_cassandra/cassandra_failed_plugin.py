# Copyright (C) Metaswitch Networks
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

from metaswitch.clearwater.cluster_manager.plugin_base import SynchroniserPluginBase
from metaswitch.clearwater.etcd_shared.plugin_utils import run_command
import subprocess
import logging

_log = logging.getLogger("cassandra_failed_plugin")

class CassandraFailedPlugin(SynchroniserPluginBase):

    # This plugin has a different set of parameters to all of the
    # other SynchroniserPluginBase subclasses.  This is currently
    # necessary as mark_node_failed does not yet plumb through the
    # information needed to run a normal plugin.
    def __init__(self, key, ip):
        self._key = key
        self._ip = ip

    def key(self):  # pragma: no coverage
        return self._key

    def on_cluster_changing(self, cluster_view):  # pragma: no coverage
        pass

    def on_joining_cluster(self, cluster_view):  # pragma: no coverage
        pass

    def on_new_cluster_config_ready(self, cluster_view):  # pragma: no coverage
        pass

    def on_stable_cluster(self, cluster_view):  # pragma: no coverage
        pass

    def on_leaving_cluster(self, cluster_view):

        # Cassandra commands need to be run in the signaling network
        # namespace in split network systems.
        #
        # This function means that there are now two ways of running a
        # command in the signaling namespace - this function, and the
        # namespace parameter to run_command.  This plugin does not have
        # access to the signaling namespace name, so we use this function
        # as a tactical workaround.
        def in_sig_namespace(command):
            prefix = "/usr/share/clearwater/bin/run-in-signaling-namespace "
            return prefix + command

        # We must remove the node from the cassandra cluster. Get the node's ID
        # from nodetool status, then remove it with nodetool remove
        try:
            status_command = "nodetool status | grep " + self._ip
            output = subprocess.check_output(in_sig_namespace(status_command),
                                             shell=True,
                                             stderr=subprocess.STDOUT)
            _log.debug("Nodetool status succeeded and printed output {!r}".
                       format(output))
        except subprocess.CalledProcessError:  # pragma: no coverage
            _log.debug("hit error")

        if output != "":
            # Pull the UUID from the output
            for value in output.split():
                if "-" in value:
                    remove_command = "nodetool removenode " + value
                    run_command(in_sig_namespace(remove_command))
                    break
