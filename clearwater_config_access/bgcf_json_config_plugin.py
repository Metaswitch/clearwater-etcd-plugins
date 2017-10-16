
from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class BgcfJson(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/bgcf_schema.json'
    name = 'bgcf_json'
    call_general = '/usr/share/clearwater/clearwater-config-manager/scripts/validate_json.py'
    uploadfile = 'upload_bgcf_json'
    filetype = 'json'
    scripts = self.script_finder_json()
    help_info = ('bgcf_json stores the system configuration of BGCF and '
                 'defines how your deployment will handle calls that are '
                 'routed to the BGCF')


def load_as_plugin(params):
    return BgcfJson(params)
