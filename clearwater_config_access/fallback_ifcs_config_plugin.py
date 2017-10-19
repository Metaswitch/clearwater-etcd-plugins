
from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class FallbackIfcsXml(ConfigType):
    name = 'fallback_ifcs'
    filetype = 'xml'
    # This help_info is used in arg-parsing to give the user some more
    # information on the config files that are available
    help_info = ('fallback_ifcs is the fallback_ifcs.xml this is a list of'
                 'iFCs that should be used if no relevant iFC can be found for'
                 'a subscriber')
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/fallback_ifcs_schema.xsd'


def load_as_plugin(params):
    return FallbackIfcsXml(params)