# Copyright (C) Metaswitch Networks
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

from metaswitch.clearwater.config_manager.plugin_base import ConfigPluginBase, FileStatus
from metaswitch.clearwater.etcd_shared.plugin_utils import run_command, safely_write
import logging

_log = logging.getLogger("rph_json_plugin")
_file = "/etc/clearwater/rph.json"
_default_value = """\
{
    "priority_blocks": [
        {
            "priority" : 1,
            "rph_values" : []
        },
        {
            "priority" : 2,
            "rph_values" : []
        },
        {
            "priority" : 3,
            "rph_values" : []
        },
        {
            "priority" : 4,
            "rph_values" : []
        },
        {
            "priority" : 5,
            "rph_values" : []
        },
        {
            "priority" : 6,
            "rph_values" : []
        },
        {
            "priority" : 7,
            "rph_values" : []
        },
        {
            "priority" : 8,
            "rph_values" : []
        },
        {
            "priority" : 9,
            "rph_values" : []
        },
        {
            "priority" : 10,
            "rph_values" : []
        },
        {
            "priority" : 11,
            "rph_values" : []
        },
        {
            "priority" : 12,
            "rph_values" : []
        },
        {
            "priority" : 13,
            "rph_values" : []
        },
        {
            "priority" : 14,
            "rph_values" : []
        },
        {
            "priority" : 15,
            "rph_values" : []
        }
    ]
}"""

class RPHJSONPlugin(ConfigPluginBase):
    def __init__(self, _params):
        pass

    def key(self):  # pragma: no cover
        return "rph_json"

    def file(self):
        return _file

    def default_value(self):
        return _default_value

    def status(self, value):
        try:
            with open(_file, "r") as ifile:
                current = ifile.read()
                if current == value:
                    return FileStatus.UP_TO_DATE
                else:
                    return FileStatus.OUT_OF_SYNC
        except IOError:  # pragma: no cover
            return FileStatus.MISSING

    def on_config_changed(self, value, alarm):
        _log.info("Updating RPH configuration file")

        if self.status(value) != FileStatus.UP_TO_DATE:
            safely_write(_file, value)
            run_command(["/usr/share/clearwater/bin/reload_rph_json"])
            alarm.update_file(_file)

def load_as_plugin(params):  # pragma: no cover
    return RPHJSONPlugin(params)
