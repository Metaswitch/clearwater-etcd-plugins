

from configtype_plugin import ConfigType


class ScscfJson(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/scscf_schema.json'
    name = 's-cscf_json'
    call_general = '/usr/share/clearwater/clearwater-config-manager/scripts/validate_json.py'
    uploadfile = 'upload_scscf_json'
    scripts = script_finder_json()
    help_info = ('s-cscf_json stores the the configuration, capabilities, '
                 'relative weightings and priority of each S-CSCF '
                 'configuration')


def load_as_plugin(params):
    return ScscfJson(params)
