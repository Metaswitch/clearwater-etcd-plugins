
from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class SharedIfcsXml(ConfigType):
    name = 'shared_ifcs'
    filetype = 'xml'
    # This help_info is used in arg-parsing to give the user some more
    # information on the config files that are available
    help_info = ('shared_ifcs is the shared_ifcs.xml this is a list of iFCs'
                 'that are common to many subscribers. This is identified by a'
                 'Shared iFC set ID ')
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/shared_ifcs_schema.xsd'


def load_as_plugin(params):
    return SharedIfcsXml(params)
