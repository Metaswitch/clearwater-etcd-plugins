
from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class SharedIfcsXml(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/shared_ifcs_schema.xsd'
    name = 'shared_ifcs'
    uploadfile = 'upload_shared_ifcs_xml'
    help_info = ('shared_ifcs is the shared_ifcs.xml this is a list of iFCs'
                 'that are common to many subscribers. This is identified by a'
                 'Shared iFC set ID ')
    filetype = 'xml'
    scripts = self.script_finder_xml()  # how to call schema


def load_as_plugin(params):
    return SharedIfcsXml(params)
