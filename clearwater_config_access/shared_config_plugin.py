
from configtype_plugin import ConfigType


class SharedConfig(ConfigType):
    scripts = []  # this does have validation TODO
    # make it run through all files in directory where shared config is
    # this allows users to edit it too
    name = 'shared_config'
    uploadfile = 'upload_shared_config'
    help_info = 'shared_config is for  '  # TODO


def load_as_plugin(params):
    return SharedConfig(params)
