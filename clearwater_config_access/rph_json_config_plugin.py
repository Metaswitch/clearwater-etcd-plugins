# Copyright (C) Metaswitch Networks 2017
# If license terms are provided to you in a COPYING file in the root directory
# of the source code repository by which you are accessing this code, then
# the license outlined in that COPYING file applies to your use.
# Otherwise no rights are granted except for those provided to you by
# Metaswitch Networks in a separate written agreement.

"""This contains the rph json subclass of ConfigType"""

import subprocess
import logging
from metaswitch.clearwater.config_manager.config_type_class_plugin import ConfigType
LOG_DIR = "/var/log/clearwater-config-manager"
log = logging.getLogger("cw-config.validate")


class RphJson(ConfigType):
    def __init__(self, configpath):
        """ Initialise the class variables. """
        self.configfile = configpath

        self.name = 'rph_json'
        self.filetype = 'json'

        # file_download_name is used to agree with the current naming system
        # when writing to file
        self.file_download_name = 'rph.json'

        # This help_info appears as user-visible help text in the usage
        # statement for cw-config.
        self.help_info = ('''rph_json - maps different resource priority header
              values to an internal priority value.''')

        self.schema = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/rph_schema.json'
        self.validation_file = '/usr/share/clearwater/clearwater-config-manager/scripts/config_validation/rph_validation.py'

    def validate(self):
        """ Validate using custom validation script. """
        validate_script = ['python', self.validation_file, self.schema,
                           self.configfile]
        failed_scripts = []
        error_lines = []

        try:
            log.debug("Running validation script rph_validation.py")
            subprocess.check_output(validate_script, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            log.error("Validation script rph_validation.py failed")
            log.error("Reasons for failure:")

            errors = exc.output.splitlines()
            error_lines.extend(errors)

            for line in errors:
                log.error(line)

            failed_scripts.append('rph_validation.py')

        return failed_scripts, error_lines


def load_as_plugin(params):  # pragma: no cover
    return RphJson(params)
