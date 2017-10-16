"""The contains the shared config subclass of config type"""
from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class SharedConfig(ConfigType):
    scripts = []  # this does have validation TODO
    # make it run through all files in directory where shared config is
    # this allows users to edit it too
    name = 'shared_config'
    uploadfile = 'upload_shared_config'
    filetype = 'shared'
    help_info = ('shared_config contains core options(required in most'
                 ' clearwater deployments), advanced options(optional settings'
                 ' whose needs depend on the deployment configuration), and '
                 'OAN configuration(only required if One-time-password access '
                 'Nodes are being deployed)')

def load_as_plugin(params):
    return SharedConfig(params)
