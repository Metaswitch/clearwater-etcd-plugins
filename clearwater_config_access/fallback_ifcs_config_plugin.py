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
    # file_download_name is used to agree with the current naming system when
    # writing to file.
    file_download_name = 'fallback_ifcs.xml'

    # This help_info appears as user-visible help text in the usage statement
    # for cw-config.
    help_info = ('''fallback_ifcs - this is the xml file which is used if no
              relevant iFC can be found for a subscriber.''')
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/fallback_ifcs_schema.xsd'


def load_as_plugin(params):  # pragma: no cover
    return FallbackIfcsXml(params)