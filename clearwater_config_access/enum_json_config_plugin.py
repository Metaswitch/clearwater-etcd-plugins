# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

"""This contains the enum json subclass of ConfigType"""

from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class EnumJson(ConfigType):
    name = 'enum'
    filetype = 'json'
    # filename is used to agree with the current naming system when finding or
    # writing to files
    filename = 'enum.json'
    # This help_info appears as user-visible help text in the usage statement
    # for cw-config.
    help_info = ('enum.json is for storing dialled telephone numbers into '
                 'internet addresses(URI)')
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/enum_schema.json'


def load_as_plugin(params):
    return EnumJson(params)
