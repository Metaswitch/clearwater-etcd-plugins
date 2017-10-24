# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

"""This contains the mmf targets json subclass of ConfigType"""

from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class MmfTargetsJson(ConfigType):
    name = 'mmf_targets_json'
    filetype = 'json'
    # This help_info appears as user-visible help text in the usage statement
    # for cw-config.
    help_info = ('mmf_targets_json stores the application servers for which '
                 'MMF should be invoked and when MMF should be invoked')
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/mmf_targets_schema.json'


def load_as_plugin(params):
    return MmfTargetsJson(params)
