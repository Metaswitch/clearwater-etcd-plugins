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
        # We must remove the node from the cassandra cluster.
        self.remove_node()

    def remove_node(self):   # pragma: no cover
        try:
            args = ["/usr/share/clearwater/bin/run-in-signaling-namespace",
                    "nodetool", "status"]
            process_nodetool = subprocess.Popen(args, stdout=subprocess.PIPE)
            process_grep = subprocess.Popen(['grep', self._ip], 
                    stdin=process_nodetool.stdout, stdout=subprocess.PIPE)

            process_nodetool.stdout.close()
            output = process_grep.communicate()[0]
            _log.debug("Nodetool status succeeded and printed output {!r}".
                       format(output))
        except subprocess.CalledProcessError:  # pragma: no coverage
            _log.debug("hit error")

        if output != "":
            # Pull the UUID from the output
            for value in output.split():
                if "-" in value:
                    remove_command = ["/usr/share/clearwater/bin/run-in-signaling-namespace", "nodetool", "removenode", value]
                    run_command(remove_command)
                    break
