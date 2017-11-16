# Copyright (C) Metaswitch Networks
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

from sprout_json_plugin import SproutJsonPlugin
import logging
import os
import sys

sys.path.append(os.path.dirname(__file__))

_log = logging.getLogger("sprout_rph_json_plugin")


class SproutRPHJsonPlugin(SproutJsonPlugin):
    def __init__(self, _params):
        super(SproutRPHJsonPlugin, self).__init__("/etc/clearwater/rph.json",
                                                  "rph_json")
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


def load_as_plugin(params):
    return SproutRPHJsonPlugin(params)
