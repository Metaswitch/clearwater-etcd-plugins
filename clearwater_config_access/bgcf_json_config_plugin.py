
from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class BgcfJson(ConfigType):
    name = 'bgcf_json'
    filetype = 'json'
    # This help_info is used in arg-parsing to give the user some more
    # information on the config files that are available
    help_info = ('bgcf_json stores the system configuration of BGCF and '
                 'defines how your deployment will handle calls that are '
                 'routed to the BGCF')
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/bgcf_schema.json'


def load_as_plugin(params):
    return BgcfJson(params)
