

from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class MmfTargetsJson(ConfigType):
    name = 'mmf_targets_json'
    filetype = 'json'
    # This help_info is used in arg-parsing to give the user some more
    # information on the config files that are available
    help_info = ('mmf_targets_json stores the application servers for which '
                 'MMF should be invoked and when MMF should be invoked')
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/mmf_targets_schema.json'


def load_as_plugin(params):
    return MmfTargetsJson(params)
