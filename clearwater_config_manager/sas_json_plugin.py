# Copyright (C) Metaswitch Networks 2018
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

from metaswitch.clearwater.config_manager.plugin_base import ConfigPluginBase, FileStatus
from metaswitch.clearwater.etcd_shared.plugin_utils import run_command, safely_write
from nsenter import Namespace

import dns.resolver
import ipaddress
import json
import logging
import os
import subprocess

_log = logging.getLogger("sas_json_plugin")
_file = "/etc/clearwater/sas.json"
_default_value = """\
{
  "sas_servers": [
  ]
}"""

class SASJSONPlugin(ConfigPluginBase):
    def __init__(self, _params):
        pass

    def key(self):  # pragma: no cover
        return "sas_json"

    def file(self):
        return _file

    def default_value(self):
        # If a value is set for sas_server, we should resolve it and set that as the default
        is_signaling = False
        ip_addrs = [subprocess.check_output(['bash', '-c', '. /etc/clearwater/config; echo -n $sas_server'])]
        sas_use_signaling_interface_var = subprocess.check_output(
            ['bash', '-c', '. /etc/clearwater/config; echo -n $sas_use_signaling_interface'])

        if sas_use_signaling_interface_var == "Y": # pragma: no cover
            is_signaling = True

        if ip_addrs[0]: # pragma: no cover
            try:
                # Check if it's an IP address
                ipaddress.ip_address(ip_addrs[0])
            except ValueError:
                # It's not an IP address, so try and resolve as a domain address.
                ip_addrs = resolve_domain_address_in_namespace(ip_addrs[0], is_signaling)

            sas_config = {"sas_servers": [{"ip": addr} for addr in ip_addrs]}
            sas_json = json.dumps(sas_config)
        else:
            # No value set for sas_server, so returning an empty config file.
            sas_json = _default_value

        return sas_json

    def status(self, value):
        try:
            with open(_file, "r") as ifile:
                current = ifile.read()
                if current == value:
                    return FileStatus.UP_TO_DATE
                else:
                    return FileStatus.OUT_OF_SYNC
        except IOError:  # pragma: no cover
            return FileStatus.MISSING

    def on_config_changed(self, value, alarm):
        _log.info("Updating SAS configuration file")

        if self.status(value) != FileStatus.UP_TO_DATE:
            safely_write(_file, value)

            run_command(["/usr/share/clearwater/infrastructure/scripts/sas_socket_factory"])
            apply_config_key = subprocess.check_output(["/usr/share/clearwater/clearwater-queue-manager/scripts/get_apply_config_key"])
            run_command(["/usr/share/clearwater/clearwater-queue-manager/scripts/modify_nodes_in_queue",
                         "add", apply_config_key])

            alarm.update_file(_file)

def resolve_domain_address(addr, dns_server=None): # pragma: no cover
    ip_addrs = []

    # Ensure we're using the correct dns server.
    if dns_server:
        dns.resolver.override_system_resolver()
        dns.resolver.get_default_resolver().nameservers = dns_server.split(',')

    try:
        resolver = dns.resolver.get_default_resolver()

        # timeout is the time spent waiting for each DNS server.
        # lifetime is the time spent waiting for a response overall.
        # By setting timeout to 2 and lifetime to 4, we allow time for us to
        # check at least 2 of our DNS servers before we give up.
        resolver.timeout = 2.0
        resolver.lifetime = 4.0
        ip_addrs = resolver.query(addr)
    except Exception:
        # If something goes wrong, we can't resolve the address so we'll
        # just return an empty list.
        pass

    # Revert changes to the dns server
    if dns_server:
        dns.resolver.restore_system_resolver()
        dns.resolver.reset_default_resolver()

    return ip_addrs

def resolve_domain_address_in_namespace(addr, is_signaling): # pragma: no cover
    dns_answers = []

    if is_signaling:
        sig_ns = os.environ.get('signaling_namespace')
        sig_dns = os.environ.get('signaling_dns_server')

        if sig_ns:
            with Namespace('/var/run/netns/' + sig_ns, 'net'):
                dns_answers = resolve_domain_address(addr, sig_dns)
        else:
            dns_answers = resolve_domain_address(addr, sig_dns)
    else:
        dns_answers = resolve_domain_address(addr)

    ip_addrs = [ip.address for ip in dns_answers]
    return ip_addrs

def load_as_plugin(params):  # pragma: no cover
    return SASJSONPlugin(params)
