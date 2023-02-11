from csdr.module import ThreadModule
from pycsdr.types import Format
from io import BytesIO
import base64
import pickle

import logging

logger = logging.getLogger(__name__)

class SstvParser(ThreadModule):
    def __init__(self):
        self.width = 0
        self.height = 0
        self.line = 0
        super().__init__()

    def getInputFormat(self) -> Format:
        return Format.CHAR

    def getOutputFormat(self) -> Format:
        return Format.CHAR

    def run(self):
        while self.doRun:
            data = self.reader.read()
            if data is None:
                self.doRun = False
                break
            out = self.process(data.tobytes())
            self.writer.write(pickle.dumps(out))

    def process(self, data):
        try:
            out = { "mode": "SSTV" }

            if len(data)==54 and data[0]==ord(b'B') and data[1]==ord(b'M'):
                self.width  = data[18] + (data[19]<<8) + (data[20]<<16) + (data[21]<<24)
                self.height = data[22] + (data[23]<<8) + (data[24]<<16) + (data[25]<<24)
                self.line   = 0
            elif self.width>0 and len(data)==self.width*3:
                out["pixels"] = base64.b64encode(data).decode('utf-8')
                out["line"]   = self.line
                self.line     = self.line + 1
            elif data[0]==ord(b' ') and data[1]==ord(b'['):
                out["message"] = data.decode()

            out["width"]  = self.width
            out["height"] = self.height
            return out

        except Exception:
            logger.exception("Exception while parsing SSTV data")
