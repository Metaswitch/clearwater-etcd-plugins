
from configtype_plugin import ConfigType


class SharedIfcsXml(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/shared_ifcs_schema.xsd'
    name = 'shared_ifcs'
    uploadfile = 'upload_shared_ifcs_xml'
    configfile = '/etc/clearwater/shared_ifcs.xml'
    help_info = 'shared_ifcs is the shared_ifcs.xml this is for '  # TODO
    scripts = [["""xmllint --format --pretty 1 --load-trace --debug --schema $schema $configfile 2> /tmp/upload-shared-ifcs-xml.stderr.$$ > /tmp/upload-shared-ifcs-xml.stdout.$$
rc=$?"""], ]  # how to call schema


def load_as_plugin(params):
    return SharedIfcsXml(params)
