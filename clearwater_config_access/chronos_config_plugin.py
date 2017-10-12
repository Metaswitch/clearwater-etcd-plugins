
from configtype_plugin import ConfigType


class ChronosSharedConfig(ConfigType):
    scripts = []  # no validation
    name = 'chronos_shared'
    uploadfile = 'upload_chronos_shared_config'
    configfile = '/etc/chronos/chronos_shared.conf'
    help_info = 'chronos_config is the chronos_shared.conf this is for '  # TODO


def load_as_plugin(params):
    return ChronosSharedConfig(params)
