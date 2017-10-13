
from configtype_plugin import ConfigType


class DnsJson(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/dns_schema.json'
    name = 'dns_json'
    call_general = 'python /usr/share/clearwater/clearwater-config-manager/scripts/validate_json.py'
    uploadfile = 'upload_dns_json'
    configfile = '/etc/clearwater/dns.json'
    scripts = [[call_general, schema, configfile], ]
    help_info = 'dns_json is for '  # TODO


def load_as_plugin(params):
    return DnsJson(params)
