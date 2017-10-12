

from configtype_plugin import ConfigType
# from usr.share.clearwater.clearwater-config-manager.scripts import validate_json


class EnumJson(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/enum_schema.json'
    name = 'enum_json'
    uploadfile = 'upload_enum_json'
    configfile = '/etc/clearwater/enum.json'
    scripts = [['validate_json_config', schema, configfile], ]
    help_info = 'enum.json is for '  # TODO


def load_as_plugin(params):
    return EnumJson(params)
