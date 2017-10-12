
from configtype_plugin import ConfigType
# from usr.share.clearwater.clearwater-config-manager.scripts import validate_json


class BgcfJson(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/bgcf_schema.json'
    name = 'bgcf_json'
    uploadfile = 'upload_bgcf_json'
    configfile = '/etc/clearwater/bgcf.json'
    scripts = [['validate_json_config', schema, configfile], ]
    help_info = 'bgcf_json is for '  # TODO


def load_as_plugin(params):
    return BgcfJson(params)
