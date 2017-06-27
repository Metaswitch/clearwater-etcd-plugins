# Copyright (C) Metaswitch Networks
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

from metaswitch.clearwater.config_manager.plugin_base import ConfigPluginBase, FileStatus
from metaswitch.clearwater.etcd_shared.plugin_utils import run_command, safely_write
from time import sleep
import logging
import shutil
import os

_log = logging.getLogger("chronos_shared_config_plugin")
_file = "/etc/chronos/chronos_shared.conf"
_default_value = """\
######################################################################
# No Chronos shared Config has been provided
# Replace this file with the Chronos shared config for your deployment
######################################################################"""

class ChronosSharedConfigPlugin(ConfigPluginBase):
    def __init__(self, _params):
        pass

    def key(self): # pragma: no cover
        return "chronos_shared_config"

    def file(self):
        return _file

    def default_value(self): # pragma: no cover
        return _default_value

    def status(self, value):
        try:
            with open(_file, "r") as ifile:
                current = ifile.read()
                if current == value:  # pragma: no cover
                    return FileStatus.UP_TO_DATE
                else:
                    return FileStatus.OUT_OF_SYNC
        except IOError:  # pragma: no cover
            return FileStatus.MISSING

    def on_config_changed(self, value, alarm):
        _log.info("Updating Chronos shared configuration file")

        if self.status(value) != FileStatus.UP_TO_DATE:
            safely_write(_file, value)
            run_command("/usr/share/clearwater/clearwater-queue-manager/scripts/modify_nodes_in_queue add apply_chronos_shared_config")

def load_as_plugin(params): # pragma: no cover
    return ChronosSharedConfigPlugin(params)
