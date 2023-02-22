from owrx.config import ConfigError
from configparser import ConfigParser
import os
import re
from glob import glob


class CoreConfig(object):
    defaults = {
        "core": {
            "data_directory": "/var/lib/openwebrx",
            "temporary_directory": "/tmp",
        },
        "web": {
            "port": 8073,
        },
        "aprs": {
            "symbols_path": "/usr/share/aprs-symbols/png"
        }
    }

    def __init__(self):
        config = ConfigParser()
        # set up config defaults
        config.read_dict(CoreConfig.defaults)
        # check for overrides
        overrides_dir = "/etc/openwebrx/openwebrx.conf.d"
        if os.path.exists(overrides_dir) and os.path.isdir(overrides_dir):
            overrides = glob(overrides_dir + "/*.conf")
        else:
            overrides = []
        # sequence things together
        config.read(["./openwebrx.conf", "/etc/openwebrx/openwebrx.conf"] + overrides)
        self.data_directory = config.get("core", "data_directory")
        CoreConfig.checkDirectory(self.data_directory, "data_directory")
        self.temporary_directory = config.get("core", "temporary_directory")
        CoreConfig.checkDirectory(self.temporary_directory, "temporary_directory")
        self.web_port = config.getint("web", "port")
        self.aprs_symbols_path = config.get("aprs", "symbols_path")

    @staticmethod
    def checkDirectory(dir, key):
        if not os.path.exists(dir):
            raise ConfigError(key, "{dir} doesn't exist".format(dir=dir))
        if not os.path.isdir(dir):
            raise ConfigError(key, "{dir} is not a directory".format(dir=dir))
        if not os.access(dir, os.W_OK):
            raise ConfigError(key, "{dir} is not writable".format(dir=dir))

    # Get list of stored files, sorted in reverse alphabetic order
    # (so that newer files appear first)
    def getStoredFiles(self):
        dir = self.get_temporary_directory()
        files = [f for f in os.listdir(dir) if re.match(r"SSTV-[0-9]+-[0-9]+\.bmp", f)]
        return sorted(files, reverse=True)

    # Delete all stored files except for <keepN> newest ones
    def cleanStoredFiles(self, keepN):
        dir = self.get_temporary_directory()
        files = self.getFileList()
        for f in files[keepN:]:
            try:
                os.unlink(dir + "/" + f)
            except Exception:
                pass

    def get_web_port(self):
        return self.web_port

    def get_data_directory(self):
        return self.data_directory

    def get_temporary_directory(self):
        return self.temporary_directory

    def get_aprs_symbols_path(self):
        return self.aprs_symbols_path

