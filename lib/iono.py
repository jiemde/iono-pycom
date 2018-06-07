from machine import Pin
from machine import ADC
from machine import DAC
from machine import I2C
import pycom

__version__ = '0.0.0'

class AV:
    def __init__(self, channel):
        self._channel = channel

    def __call__(self):
        return self.voltage()

    def voltage(self):
        v = int(round(self._channel.voltage() * 13.46240 - 2081.81))
        if v < 0:
            return 0
        return v

    def get_adcchannel(self):
        return self._channel

class AI:
    def __init__(self, channel):
        self._channel = channel

    def __call__(self):
        return self.current()

    def current(self):
        v = int(round(self._channel.voltage() * 10.31915 - 1595.74))
        if v < 0:
            return 0
        return v

    def get_adcchannel(self):
        return self._channel

class IO:

    MODE_DIGITAL = const(0)
    MODE_ANALOG = const(1)

    def __init__(self, i1=MODE_DIGITAL, i2=MODE_DIGITAL, i3=MODE_DIGITAL, i4=MODE_DIGITAL):
        self.DO1 = Pin('P21', mode=Pin.OUT)
        self.DO2 = Pin('P23', mode=Pin.OUT)
        self.DO3 = Pin('P8', mode=Pin.OUT)
        self.DO4 = Pin('P11', mode=Pin.OUT)

        if i1 is MODE_DIGITAL:
            self.DI1 = Pin('P14', mode=Pin.IN, pull=None)
        else:
            chan = self._getADC().channel(pin='P14', attn=ADC.ATTN_11DB)
            self.AV1 = AV(chan)
            self.AI1 = AI(chan)

        if i2 is MODE_DIGITAL:
            self.DI2 = Pin('P13', mode=Pin.IN, pull=None)
        else:
            chan = self._getADC().channel(pin='P13', attn=ADC.ATTN_11DB)
            self.AV2 = AV(chan)
            self.AI2 = AI(chan)

        if i3 is MODE_DIGITAL:
            self.DI3 = Pin('P16', mode=Pin.IN, pull=None)
        else:
            chan = self._getADC().channel(pin='P16', attn=ADC.ATTN_11DB)
            self.AV3 = AV(chan)
            self.AI3 = AI(chan)

        if i4 is MODE_DIGITAL:
            self.DI4 = Pin('P15', mode=Pin.IN, pull=None)
        else:
            chan = self._getADC().channel(pin='P15', attn=ADC.ATTN_11DB)
            self.AV4 = AV(chan)
            self.AI4 = AI(chan)

        self.DI5 = Pin('P18', mode=Pin.IN, pull=None)
        self.DI6 = Pin('P17', mode=Pin.IN, pull=None)
        self.AO1 = DAC('P22')

    def _getADC(self):
        if not hasattr(self, '_adc'):
            self._adc = ADC()
        return self._adc
