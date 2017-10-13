
from configtype_plugin import ConfigType


class FallbackIfcsXml(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/fallback_ifcs_schema.xsd'
    name = 'fallback_ifcs'
    uploadfile = 'upload_fallback_ifcs_xml'
    help_info = 'fallback_ifcs is the fallback_ifcs.xml this is for '  # TODO
    scripts = script_finder_xml()  # how to call schema


def load_as_plugin(params):
    return FallbackIfcsXml(params)