
from configtype_plugin import ConfigType


class SharedConfig(ConfigType):
    scripts = []  # this does have validation
    name = 'shared_config'
    uploadfile = 'upload_shared_config'
    configfile = '/etc/clearwater/shared_config'
    help_info = 'shared_config is for  '  # TODO


def load_as_plugin(params):
    return SharedConfig(params)
