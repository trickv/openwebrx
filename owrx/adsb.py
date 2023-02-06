from owrx.audio import AudioChopperProfile, StaticProfileSource
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
    def getInterval(self):
        return 60

    def getFileTimestampFormat(self):
        return "%y%m%d_%H%M%S"

    def decoder_commandline(self, file):
        return ["dump1090-mutability", "--ifile", file, "--iformat", "SC16"]

    def getMode(self):
        return "ADSB"


class AdsbProfileSource(StaticProfileSource):
    def __init__(self):
        super().__init__([AdsbProfile()])


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
