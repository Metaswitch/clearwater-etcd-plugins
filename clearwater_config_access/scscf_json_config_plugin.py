

from configtype_plugin import ConfigType
# from usr.share.clearwater.clearwater-config-manager.scripts import validate_json


class ScscfJson(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/scscf_schema.json'
    name = 's-cscf_json'
    uploadfile = 'upload_scscf_json'
    configfile = '/etc/clearwater/s-cscf.json'
    scripts = [['validate_json_config', schema, configfile], ]
    help_info = 's-cscf_json is for '  # TODO


def load_as_plugin(params):
    return ScscfJson(params)
