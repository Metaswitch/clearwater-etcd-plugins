# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

"""This contains the chronos subclass of ConfigType"""

from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class ChronosSharedConfig(ConfigType):
    name = 'chronos_shared_config'
    filetype = 'chronos'
    # file_download_name is used to agree with the current naming system when
    # writing to file.
    file_download_name = 'chronos_shared.conf'

    # This help_info appears as user-visible help text in the usage statement
    # for cw-config.
    help_info = ('chronos_shared_config is the chronos_shared.conf this is for'
                 'configuration options that control how the Chronos cluster '
                 'in the local site connects to other clusters for geographic'
                 'redundancy. If you have a single site deployment, this file'
                 'is not required. \n')


def load_as_plugin(params):
    return ChronosSharedConfig(params)
