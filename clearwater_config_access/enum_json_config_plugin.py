

from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class EnumJson(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/enum_schema.json'
    name = 'enum_json'
    call_general = '/usr/share/clearwater/clearwater-config-manager/scripts/validate_json.py'
    uploadfile = 'upload_enum_json'
    filetype = 'json'
    scripts = self.script_finder_json()
    help_info = ('enum.json is for storing dialled telephone numbers into '
                 'internet addresses(URI)')


def load_as_plugin(params):
    return EnumJson(params)
