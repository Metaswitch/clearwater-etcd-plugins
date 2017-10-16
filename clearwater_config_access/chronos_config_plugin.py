
from configtype_plugin import ConfigType


class ChronosSharedConfig(ConfigType):
    scripts = []  # no validation
    name = 'chronos_shared'
    uploadfile = 'upload_chronos_shared_config'
    help_info = ('chronos_config is the chronos_shared.conf this is for'
                 'configuration options that control how the Chronos cluster '
                 'in the local site connects to other clusters for geographic'
                 'redundancy. If you have a single site deployment, this file'
                 'is not required.')


def load_as_plugin(params):
    return ChronosSharedConfig(params)
