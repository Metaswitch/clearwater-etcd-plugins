# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

from metaswitch.clearwater.config_manager.plugin_base import ConfigPluginBase, FileStatus
from metaswitch.clearwater.etcd_shared.plugin_utils import run_command, safely_write
import logging

_log = logging.getLogger("fallback_ifcs_xml_plugin")
_file = "/etc/clearwater/fallback_ifcs.xml"

_default_value = """\
<?xml version="1.0" encoding="UTF-8"?>
<FallbackIFCsSet>
</FallbackIFCsSet>"""

class FallbackIFCsXMLPlugin(ConfigPluginBase):
    def __init__(self, _params):
        pass

    def key(self):  # pragma: no cover
        return "fallback_ifcs"

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
        _log.info("Updating the fallback iFCs configuration file")

        if self.status(value) != FileStatus.UP_TO_DATE:
            safely_write(_file, value)
            run_command(["/usr/share/clearwater/bin/reload_fallback_ifcs_xml"])
            alarm.update_file(_file)

def load_as_plugin(params):  # pragma: no cover
    return FallbackIFCsXMLPlugin(params)
