# Copyright (C) Metaswitch Networks 2018
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

"""This contains the sas json subclass of ConfigType"""

from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class SasJson(ConfigType):
    name = 'sas_json'
    filetype = 'json'
    # file_download_name is used to agree with the current naming system when
    # writing to file.
    file_download_name = 'sas.json'

    # This help_info appears as user-visible help text in the usage statement
    # for cw-config.
    help_info = ('''sas_json - contains the list of configured SAS servers to which
              SAS logs are sent.''')
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/sas_schema.json'


def load_as_plugin(params):   # pragma: no cover
    return SasJson(params)
