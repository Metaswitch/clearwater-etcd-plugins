
from configtype_plugin import ConfigType


class SharedIfcsXml(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/shared_ifcs_schema.xsd'
    name = 'shared_ifcs'
    uploadfile = 'upload_shared_ifcs_xml'
    help_info = ('shared_ifcs is the shared_ifcs.xml this is a list of iFCs'
                 'that are common to many subscribers. This is identified by a'
                 'Shared iFC set ID ')
    scripts = script_finder_xml()  # how to call schema


def load_as_plugin(params):
    return SharedIfcsXml(params)
