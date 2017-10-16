

from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class MmfTargetsJson(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/mmf_targets_schema.json'
    name = 'mmf_targets_json'
    call_general = '/usr/share/clearwater/clearwater-config-manager/scripts/validate_json.py'
    uploadfile = 'upload_mmf_targets_json'
    json = True
    scripts = self.script_finder_json()
    help_info = ('mmf_targets_json stores the application servers for which '
                 'MMF should be invoked and when MMF should be invoked')


def load_as_plugin(params):
    return MmfTargetsJson(params)
