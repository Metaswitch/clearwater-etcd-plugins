# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

"""The contains the shared config subclass of config type"""
from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class SharedConfig(ConfigType):
    """This is the subclass describing shared_config"""
    name = 'shared_config'
    filetype = 'shared_config'
    # This help_info is used in arg-parsing to give the user some more
    # information on the config files that are available
    help_info = ('shared_config contains core options(required in most'
                 ' clearwater deployments), advanced options(optional settings'
                 ' whose needs depend on the deployment configuration), and '
                 'OAN configuration(only required if One-time-password access '
                 'Nodes are being deployed)')

def load_as_plugin(params):
    return SharedConfig(params)
