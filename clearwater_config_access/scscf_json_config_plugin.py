# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

"""This contains the s-cscf json subclass of ConfigType"""

from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class ScscfJson(ConfigType):
    name = 'scscf_json'
    filetype = 'json'
    # file_download_name is used to agree with the current naming system when
    # writing to file.
    file_download_name = 's-cscf.json'

    # This help_info appears as user-visible help text in the usage statement
    # for cw-config.
    help_info = ('''scscf_json - this stores the configuration, capabilities,
              relative weightings and priority of each S-CSCF.''')
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/scscf_schema.json'


def load_as_plugin(params):
    return ScscfJson(params)
