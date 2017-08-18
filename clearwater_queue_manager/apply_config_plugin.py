# Copyright (C) Metaswitch Networks
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

from metaswitch.clearwater.queue_manager.plugin_base import QueuePluginBase
from metaswitch.clearwater.etcd_shared.plugin_utils import run_command
import logging
import os
import subprocess

_log = logging.getLogger("apply_config_plugin")

class ApplyConfigPlugin(QueuePluginBase):
    def __init__(self, params):
        self._wait_plugin_complete = params.wait_plugin_complete
        output = subprocess.check_output(["/usr/share/clearwater/clearwater-queue-manager/scripts/get_apply_config_key"])
        self._key = output.decode('utf-8')

    def key(self):  # pragma: no cover
        return self._key

    def at_front_of_queue(self):
        _log.info("Restarting clearwater-infrastructure")
        run_command(["service", "clearwater-infrastructure", "restart"])

        if os.path.exists("/usr/share/clearwater/infrastructure/scripts/restart"):
            _log.info("Restarting services")
            for restart_script in os.listdir("/usr/share/clearwater/infrastructure/scripts/restart"):
                run_command(["/usr/share/clearwater/infrastructure/scripts/restart/"
                    + restart_script])
 
        if self._wait_plugin_complete != "N":
            _log.info("Checking service health")
            if run_command(["/usr/share/clearwater/clearwater-queue-manager/scripts/check_node_health.py"]):
                _log.info("Services failed to restart successfully")
                run_command(["/usr/share/clearwater/clearwater-queue-manager/scripts/modify_nodes_in_queue",
                "remove_failure", self._key])
            else:
                _log.info("Services restarted successfully")
                run_command(["/usr/share/clearwater/clearwater-queue-manager/scripts/modify_nodes_in_queue",
                "remove_success", self._key])
        else:
            _log.info("Not checking service health")
            run_command(["/usr/share/clearwater/clearwater-queue-manager/scripts/modify_nodes_in_queue",
            "remove_success", self._key])

def load_as_plugin(params):  # pragma: no cover
    return ApplyConfigPlugin(params)
