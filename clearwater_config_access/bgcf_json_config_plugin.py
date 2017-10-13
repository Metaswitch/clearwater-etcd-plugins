
from configtype_plugin import ConfigType


class BgcfJson(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/bgcf_schema.json'
    name = 'bgcf_json'
    call_general = 'python /usr/share/clearwater/clearwater-config-manager/scripts/validate_json.py'
    uploadfile = 'upload_bgcf_json'
    configfile = '/etc/clearwater/bgcf.json'
    scripts = [[call_general, schema, configfile], ]
    help_info = 'bgcf_json is for '  # TODO


def load_as_plugin(params):
    return BgcfJson(params)
