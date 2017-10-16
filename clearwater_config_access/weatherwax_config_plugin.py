"""This contains the weatherwax subclass of ConfigType"""
from configtype_plugin import ConfigType


class WeatherwaxConfig(ConfigType):
    scripts = []  # no validation
    name = 'weatherwax_config'
    uploadfile = 'upload_weatherwax_config'
    help_info = ('weatherwax_config stores the data required to allow a SMS'
                 '/SIP gateway on the SPN nodes')


def load_as_plugin(params):
    return WeatherwaxConfig(params)
