# Copyright (C) Metaswitch Networks
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

from metaswitch.clearwater.config_manager.plugin_base import ConfigPluginBase, FileStatus
from metaswitch.clearwater.etcd_shared.plugin_utils import run_command, safely_write
import logging

_log = logging.getLogger("sprout_json_plugin")

class SproutJsonPlugin(ConfigPluginBase):
    def __init__(self, file, key):
        self._file = file
        self._key = key

    def key(self):
        return self._key

    def file(self):
        return self._file

    def default_value(self):
        return self._default_value

    def status(self, value):
        try:
            with open(self._file, "r") as ifile:
                current = ifile.read()
                if current == value:
                    return FileStatus.UP_TO_DATE
                else:
                    return FileStatus.OUT_OF_SYNC
        except IOError:
            return FileStatus.MISSING

    def on_config_changed(self, value, alarm):
        _log.info("Updating {}".format(self._file))

        safely_write(self._file, value)

        run_command(["service", "sprout", "reload"])

        alarm.update_file(self._file)
