
from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class DnsJson(ConfigType):
    name = 'dns_json'
    filetype = 'json'
    # This help_info is used in arg-parsing to give the user some more
    # information on the config files that are available
    help_info = ('dns_json sets up DNS overrides to CNAME records so that you'
                 ' can use a single hostname across the deployment')
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/dns_schema.json'


def load_as_plugin(params):
    return DnsJson(params)
