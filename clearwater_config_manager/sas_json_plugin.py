# Copyright (C) Metaswitch Networks 2018
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

from metaswitch.clearwater.config_manager.plugin_base import ConfigPluginBase, FileStatus
from metaswitch.clearwater.etcd_shared.plugin_utils import run_command, safely_write

import ipaddress
import json
import logging
import os
import subprocess

import dns.resolver

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
        ip_addrs = [subprocess.check_output(['bash', '-c', '. /etc/clearwater/config; echo -n $sas_server'])]
        sas_use_signaling_interface = subprocess.check_output(
            ['bash', '-c', '. /etc/clearwater/config; echo -n $sas_use_signaling_interface'])

        if ip_addrs[0] is not None:
            try:
                ipaddress.ip_address(ip_addrs[0])
            except ValueError:
                ip_addrs = self.resolve_domain_address_in_namespace(ip_addrs[0], sas_use_signaling_interface)

            sas_config = {"sas_servers": [{"ip": addr} for addr in ip_addrs]}
            sas_json = json.dumps(sas_config)
        else:
            sas_json = _default

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
            run_command(["/usr/share/clearwater/bin/reload_sas_json"])
            alarm.update_file(_file)

    def resolve_domain_address(self, addr, dns_server=None):
        ip_addrs = []

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

        if dns_server:
            dns.resolver.restore_system_resolver()
            dns.resolver.reset_default_resolver()

        return ip_addrs

    def resolve_domain_address_in_namespace(self, addr, is_signaling):
        ip_addrs = []
        dns_answers = []

        if is_signaling == 'Y':
            sig_ns = os.environ.get('signaling_namespace')
            sig_dns = os.environ.get('signaling_dns_server')

            if sig_ns:
                with Namespace('/var/run/netns/' + sig_ns, 'net'):
                    dns_answers = self.resolve_domain_address(addr, sig_dns)
            else:
                dns_answers = self.resolve_domain_address(addr, sig_dns)
        else:
            dns_answers = self.resolve_domain_address(addr)

        for dns_answer in dns_answers:
            ip_addrs.append(dns_answer.rdata)

        return ip_addrs




def load_as_plugin(params):  # pragma: no cover
    return SASJSONPlugin(params)
