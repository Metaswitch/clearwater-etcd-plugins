

from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class ScscfJson(ConfigType):
    name = 's-cscf_json'
    filetype = 'json'
    # This help_info is used in arg-parsing to give the user some more
    # information on the config files that are available
    help_info = ('s-cscf_json stores the the configuration, capabilities, '
                 'relative weightings and priority of each S-CSCF '
                 'configuration')
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/scscf_schema.json'


def load_as_plugin(params):
    return ScscfJson(params)
