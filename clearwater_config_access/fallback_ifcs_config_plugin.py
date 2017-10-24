# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

"""This contains the fallback ifcs subclass of ConfigType"""

from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class FallbackIfcsXml(ConfigType):
    name = 'fallback_ifcs'
    filetype = 'xml'
    # This help_info appears as user-visible help text in the usage statement
    # for cw-config.
    help_info = ('fallback_ifcs is the fallback_ifcs.xml this is a list of'
                 'iFCs that should be used if no relevant iFC can be found for'
                 'a subscriber')
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/fallback_ifcs_schema.xsd'


def load_as_plugin(params):
    return FallbackIfcsXml(params)