
from configtype_plugin import ConfigType
# from usr.share.clearwater.clearwater-config-manager.scripts import validate_json


class DnsJson(ConfigType):
    schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/dns_schema.json'
    name = 'dns_json'
    uploadfile = 'upload_dns_json'
    configfile = '/etc/clearwater/dns.json'
    scripts = [['validate_json_config', schema, configfile], ]
    help_info = 'dns_json is for '  # TODO


def load_as_plugin(params):
    return DnsJson(params)
