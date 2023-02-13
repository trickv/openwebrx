from csdr.module import ThreadModule
from pycsdr.types import Format
import base64
import pickle

import logging

logger = logging.getLogger(__name__)

class SstvParser(ThreadModule):
    def __init__(self):
        self.data   = bytearray(b'')
        self.width  = 0
        self.height = 0
        self.line   = 0
        super().__init__()

    def getInputFormat(self) -> Format:
        return Format.CHAR

    def getOutputFormat(self) -> Format:
        return Format.CHAR

    def run(self):
        # Run while there is input data
        while self.doRun:
            # Read input data
            inp = self.reader.read()
            # Terminate if no input data
            if inp is None:
                self.doRun = False
                break
            # Add read data to the buffer
            self.data = self.data + inp.tobytes()
            # Process buffer contents
            out = self.process()
            # Keep processing while there is input to parse
            while out is not None:
                self.writer.write(pickle.dumps(out))
                out = self.process()

    def process(self):
        try:
            # Parse bitmap (BMP) file header starting with 'BM'
            if len(self.data)>=54 and self.data[0]==ord(b'B') and self.data[1]==ord(b'M'):
                # BMP height value is negative
                self.width  = self.data[18] + (self.data[19]<<8) + (self.data[20]<<16) + (self.data[21]<<24)
                self.height = self.data[22] + (self.data[23]<<8) + (self.data[24]<<16) + (self.data[25]<<24)
                self.height = 0x100000000 - self.height
                self.line   = 0
                logger.warning("@@@ IMAGE %d x %d" % (self.width, self.height))
                # Remove parsed data
                del self.data[0:54]
                # Return parsed values
                return {
                    "mode": "SSTV",
                    "width": self.width,
                    "height": self.height
                }

            # Parse debug messages enclosed in ' [...]'
            elif len(self.data)>=2 and self.data[0]==ord(b' ') and self.data[1]==ord(b'['):
                # Wait until we find the closing bracket
                w = self.data.find(b']')
                if w>=0:
                    logger.warning("@@@ MESSAGE = '%s'" % str(self.data[0:w+1]))
                    # Compose result
                    out = {
                        "mode": "SSTV",
                        "message": self.data[0:w+1].decode()
                    }
                    # Remove parsed data
                    del self.data[0:w+1]
                    # Return parsed values
                    return out

            # Parse bitmap file data (scanlines)
            elif self.width>0 and len(self.data)>=self.width*3:
                logger.warning("@@@ LINE %d/%d..." % (self.line+1, self.height))
                w = self.width * 3
                # Compose result
                out = {
                    "mode":   "SSTV",
                    "pixels": base64.b64encode(self.data[0:w]).decode(),
                    "line":   self.line,
                    "width":  self.width,
                    "height": self.height
                }
                # Advance scanline
                self.line = self.line + 1
                # If we reached the end of frame, finish scan
                if self.line>=self.height:
                    self.width  = 0
                    self.height = 0
                    self.line   = 0
                # Remove parsed data
                del self.data[0:w]
                # Return parsed values
                return out

            # Could not parse input data (yet)
            return None

        except Exception:
            logger.exception("Exception while parsing SSTV data")
