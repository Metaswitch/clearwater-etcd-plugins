
from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType


class DnsJson(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/dns_schema.json'
    name = 'dns_json'
    call_general = '/usr/share/clearwater/clearwater-config-manager/scripts/validate_json.py'
    uploadfile = 'upload_dns_json'
    scripts = script_finder_json()
    help_info = ('dns_json sets up DNS overrides to CNAME records so that you'
                 ' can use a single hostname across the deployment')


def load_as_plugin(params):
    return DnsJson(params)
