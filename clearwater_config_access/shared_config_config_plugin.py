"""The contains the shared config subclass of config type"""
from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class SharedConfig(ConfigType):
    """This is the subclass describing shared_config"""
    name = 'shared_config'
    filetype = 'shared_config'
    # This help_info is used in arg-parsing to give the user some more
    # information on the config files that are available
    help_info = ('shared_config contains core options(required in most'
                 ' clearwater deployments), advanced options(optional settings'
                 ' whose needs depend on the deployment configuration), and '
                 'OAN configuration(only required if One-time-password access '
                 'Nodes are being deployed)')

def load_as_plugin(params):
    return SharedConfig(params)
