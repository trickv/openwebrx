from owrx.audio import AudioChopperProfile, ConfigWiredProfileSource
from owrx.audio.chopper import AudioChopperParser
import re
from owrx.map import Map, LocatorLocation
from owrx.metrics import Metrics, CounterMetric
from owrx.config import Config
from abc import ABCMeta, abstractmethod
from owrx.reporting import ReportingEngine
from owrx.bands import Bandplan
from typing import List

import logging

logger = logging.getLogger(__name__)


class AdsbProfile(AudioChopperProfile, metaclass=ABCMeta):
    def getFileTimestampFormat(self):
        return "%y%m%d_%H%M%S"

    def decoder_commandline(self, file):
        return ["dump1090-mutability", "--ifile", "-", "--iformat", "SC16", ">", file]

    @abstractmethod
    def get_sub_mode(self):
        pass


class AdsbProfileSource(ConfigWiredProfileSource):
    def getPropertiesToWire(self) -> List[str]:
        return ["adsb_enabled_profiles"]

    def getProfiles(self) -> List[AudioChopperProfile]:
        config = Config.get()
        profiles = config["adsb_enabled_profiles"] if "adsb_enabled_profiles" in config else []
        return [self._loadProfile(p) for p in profiles]

    def _loadProfile(self, profileName):
        className = "AdsbProfile"
        return globals()[className]()


class AdsbParser(AudioChopperParser):
    decoderRegex = re.compile(" ?<Decode(Started|Debug|Finished)>")

    def parse(self, profile: AudioChopperProfile, freq: int, raw_msg: bytes):
        try:
            band = None
            if freq is not None:
                band = Bandplan.getSharedInstance().findBand(freq)

            msg = raw_msg.decode().rstrip()
            if AdsbParser.decoderRegex.match(msg):
                return
            if msg.startswith(" EOF on input file"):
                return

        except Exception:
            logger.exception("error while parsing ADSB message")
        pass
