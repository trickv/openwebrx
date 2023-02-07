from csdr.chain.demodulator import ServiceDemodulator, SecondaryDemodulator, DialFrequencyReceiver, SecondarySelectorChain
from owrx.audio.chopper import AudioChopper, AudioChopperParser
from owrx.aprs.kiss import KissDeframer
from owrx.aprs import Ax25Parser, AprsParser
from pycsdr.modules import Convert, FmDemod, Agc, TimingRecovery, DBPskDecoder, VaricodeDecoder, CwDecoder, RttyDecoder, SstvDecoder, Shift
from pycsdr.types import Format
from owrx.aprs.module import DirewolfModule


class AudioChopperDemodulator(ServiceDemodulator, DialFrequencyReceiver):
    def __init__(self, mode: str, parser: AudioChopperParser):
        self.chopper = AudioChopper(mode, parser)
        workers = [Convert(Format.FLOAT, Format.SHORT), self.chopper]
        super().__init__(workers)

    def getFixedAudioRate(self):
        return 12000

    def setDialFrequency(self, frequency: int) -> None:
        self.chopper.setDialFrequency(frequency)


class PacketDemodulator(ServiceDemodulator, DialFrequencyReceiver):
    def __init__(self, service: bool = False):
        self.parser = AprsParser()
        workers = [
            FmDemod(),
            Convert(Format.FLOAT, Format.SHORT),
            DirewolfModule(service=service),
            KissDeframer(),
            Ax25Parser(),
            self.parser,
        ]
        super().__init__(workers)

    def supportsSquelch(self) -> bool:
        return False

    def getFixedAudioRate(self) -> int:
        return 48000

    def setDialFrequency(self, frequency: int) -> None:
        self.parser.setDialFrequency(frequency)


class PskDemodulator(SecondaryDemodulator, SecondarySelectorChain):
    def __init__(self, baudRate: float):
        self.baudRate = baudRate
        # this is an assumption, we will adjust in setSampleRate
        self.sampleRate = 12000
        secondary_samples_per_bits = int(round(self.sampleRate / self.baudRate)) & ~3
        workers = [
            Agc(Format.COMPLEX_FLOAT),
            TimingRecovery(secondary_samples_per_bits, 0.5, 2, useQ=True),
            DBPskDecoder(),
            VaricodeDecoder(),
        ]
        super().__init__(workers)

    def getBandwidth(self):
        return self.baudRate

    def setSampleRate(self, sampleRate: int) -> None:
        if sampleRate == self.sampleRate:
            return
        self.sampleRate = sampleRate
        secondary_samples_per_bits = int(round(self.sampleRate / self.baudRate)) & ~3
        self.replace(1, TimingRecovery(secondary_samples_per_bits, 0.5, 2, useQ=True))


class CwDemodulator(SecondaryDemodulator, SecondarySelectorChain):
    def __init__(self, baudRate: float):
        self.baudRate = baudRate
        self.sampleRate = 12000
        workers = [
            Shift(800.0 / self.sampleRate),
            Agc(Format.COMPLEX_FLOAT),
            CwDecoder(self.sampleRate, 800, int(self.baudRate)),
        ]
        super().__init__(workers)

    def getBandwidth(self):
        return self.baudRate

    def setSampleRate(self, sampleRate: int) -> None:
        if sampleRate == self.sampleRate:
            return
        self.sampleRate = sampleRate
        self.replace(0, Shift(800.0 / sampleRate))
        self.replace(2, CwDecoder(sampleRate, 800, int(self.baudRate)))


class RttyDemodulator(SecondaryDemodulator, SecondarySelectorChain):
    def __init__(self, targetWidth: float, baudRate: float, reverse: bool):
        self.sampleRate = 12000
        self.targetWidth = targetWidth
        self.baudRate = baudRate
        self.reverse = reverse
        workers = [
            Shift((self.targetWidth/2 + 550) / self.sampleRate),
            Agc(Format.COMPLEX_FLOAT),
            RttyDecoder(self.sampleRate, 550, int(self.targetWidth), self.baudRate, self.reverse),
        ]
        super().__init__(workers)

    def getBandwidth(self):
        return self.targetWidth + 100.0

    def setSampleRate(self, sampleRate: int) -> None:
        if sampleRate == self.sampleRate:
            return
        self.sampleRate = sampleRate
        self.replace(0, Shift((self.targetWidth/2 + 550) / sampleRate))
        self.replace(2, RttyDecoder(sampleRate, 550, int(self.targetWidth), self.baudRate, self.reverse))


class SstvDemodulator(SecondaryDemodulator, SecondarySelectorChain):
    def __init__(self, targetWidth: float):
        self.sampleRate = 12000
        self.targetWidth = targetWidth
        workers = [
            Shift((self.targetWidth/2) / self.sampleRate),
            Agc(Format.COMPLEX_FLOAT),
            SstvDecoder(self.sampleRate, int(self.targetWidth)),
        ]
        super().__init__(workers)

    def getBandwidth(self):
        return self.targetWidth

    def setSampleRate(self, sampleRate: int) -> None:
        if sampleRate == self.sampleRate:
            return
        self.sampleRate = sampleRate
        self.replace(0, Shift((self.targetWidth/2) / sampleRate))
        self.replace(2, SstvDecoder(sampleRate, int(self.targetWidth)))

