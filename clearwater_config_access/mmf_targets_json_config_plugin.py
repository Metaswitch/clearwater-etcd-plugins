

from configtype_plugin import ConfigType

class MmfTargetsJson(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/mmf_targets_schema.json'
    name = 'mmf_targets_json'
    call_general = '/usr/share/clearwater/clearwater-config-manager/scripts/validate_json.py'
    uploadfile = 'upload_mmf_targets_json'
    scripts = script_finder_json()
    help_info = 'mmf_targets_json is for '  # TODO


def load_as_plugin(params):
    return MmfTargetsJson(params)
