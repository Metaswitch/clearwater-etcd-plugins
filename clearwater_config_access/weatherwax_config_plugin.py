# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

"""This contains the weatherwax subclass of ConfigType"""
from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class WeatherwaxConfig(ConfigType):
    name = 'weatherwax_config'
    filetype = 'weatherwax'
    # This help_info is used in arg-parsing to give the user some more
    # information on the config files that are available
    help_info = ('weatherwax_config stores the data required to allow a SMS'
                 '/SIP gateway on the SPN nodes')


def load_as_plugin(params):
    return WeatherwaxConfig(params)
