

from configtype_plugin import ConfigType
# from usr.share.clearwater.clearwater-config-manager.scripts import validate_json

class MmfTargetsJson(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/mmf_targets_schema.json'
    name = 'mmf_targets_json'
    uploadfile = 'upload_mmf_targets_json'
    configfile = '/etc/clearwater/mmf_targets.json'
    scripts = [['validate_json_config', schema, configfile], ]
    help_info = 'mmf_targets_json is for '  # TODO


def load_as_plugin(params):
    return MmfTargetsJson(params)
