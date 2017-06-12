# Copyright (C) Metaswitch Networks
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

from metaswitch.clearwater.config_manager.plugin_base import \
    ConfigPluginBase
from metaswitch.clearwater.etcd_shared.plugin_utils import \
    run_command
import logging
import sys
import os

sys.path.append(os.path.dirname(__file__))
from sprout_json_plugin import SproutJsonPlugin

_log = logging.getLogger("sprout_bgcf_json_plugin")

class SproutBGCFJsonPlugin(SproutJsonPlugin):
    def __init__(self, _params):
        super(SproutBGCFJsonPlugin, self).__init__("/etc/clearwater/bgcf.json", "bgcf_json")

    _default_value = """\
{
    "routes" : [
    ]
}"""

def load_as_plugin(params):
    return SproutBGCFJsonPlugin(params)
