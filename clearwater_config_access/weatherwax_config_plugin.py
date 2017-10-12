"""This contains the weatherwax subclass of ConfigType"""
from configtype_plugin import ConfigType


class WeatherwaxConfig(ConfigType):
    scripts = []  # no validation
    name = 'weatherwax_config'
    uploadfile = 'upload_weatherwax_config'
    configfile = '/etc/clearwater/weatherwax_config'
    help_info = 'weatherwax_config is for '  # TODO


def load_as_plugin(params):
    return WeatherwaxConfig(params)
