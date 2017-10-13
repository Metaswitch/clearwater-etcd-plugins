

from configtype_plugin import ConfigType


class EnumJson(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/enum_schema.json'
    name = 'enum_json'
    call_general = '/usr/share/clearwater/clearwater-config-manager/scripts/validate_json.py'
    uploadfile = 'upload_enum_json'
    scripts = script_finder_json()
    help_info = 'enum.json is for '  # TODO


def load_as_plugin(params):
    return EnumJson(params)
