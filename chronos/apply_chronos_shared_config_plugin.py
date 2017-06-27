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

_log = logging.getLogger("apply_chronos_shared_config_plugin")

class ApplyChronosSharedConfigPlugin(QueuePluginBase):
    def __init__(self, _params):
        pass

    # How long to wait for a node to do whatever it does while it's
    # at the front of the queue.
    WAIT_FOR_THIS_NODE = 600
    WAIT_FOR_OTHER_NODE = 600

    def local_alarm(self): # pragma: no cover
        return ((9004, 1, 5, 3),
                "local")

    def global_alarm(self): # pragma: no cover
        return ((9003, 1, 5, 3),
                "global")

    def key(self): # pragma: no cover
        return "apply_chronos_shared_config"

    def at_front_of_queue(self):
        _log.info("Restarting Chronos")
        if run_command("service chronos stop"):
            _log.warning("Unable to stop Chronos successfully")
        if run_command("service chronos wait-sync"):
            _log.warning("Unable to resync Chronos successfully")
        if run_command("/usr/share/clearwater/clearwater-queue-manager/scripts/modify_nodes_in_queue remove_success apply_chronos_shared_config"):
            _log.warning("Unable to remove this node from the resync queue")
        _log.info("Chronos restarted")


def load_as_plugin(params): # pragma: no cover
    return ApplyChronosSharedConfigPlugin(params)
