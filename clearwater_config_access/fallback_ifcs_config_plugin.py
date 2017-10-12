
from configtype_plugin import ConfigType


class FallbackIfcsXml(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/fallback_ifcs_schema.xsd'
    name = 'fallback_ifcs'
    uploadfile = 'upload_fallback_ifcs_xml'
    configfile = '/etc/clearwater/fallback_ifcs.xml'
    help_info = 'fallback_ifcs is the fallback_ifcs.xml this is for '  # TODO
    scripts = [["""xmllint --format --pretty 1 --load-trace --debug --schema $schema $configfile 2> /tmp/upload-fallback-ifcs-xml.stderr.$$ > /tmp/upload-fallback-ifcs-xml.stdout.$$
rc=$?"""], ]  # how to call schema


def load_as_plugin(params):
    return FallbackIfcsXml(params)