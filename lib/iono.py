from machine import Pin
from machine import ADC
from machine import DAC
from machine import I2C
import pycom
import time

__version__ = '0.1.0'

class IonoPin:
    def __init__(self, id, pin, mode, pull=None):
        self._pin = Pin(pin, mode=mode, pull=pull)
        self._iono_id = id

    def __call__(self):
        return self._pin()

    def id(self):
        return self._iono_id

    def __getattr__(self, attr):
        return getattr(self._pin, attr)

class AV:
    def __init__(self, id, channel):
        self._iono_id = id
        self._channel = channel

    def __call__(self):
        return self.voltage()

    def id(self):
        return self._iono_id

    def voltage(self):
        v = int(round(self._channel.voltage() * 13.46240 - 2081.81))
        if v < 0:
            return 0
        return v

    def get_adcchannel(self):
        return self._channel

class AI:
    def __init__(self, id, channel):
        self._iono_id = id
        self._channel = channel

    def __call__(self):
        return self.current()

    def id(self):
        return self._iono_id

    def current(self):
        v = int(round(self._channel.voltage() * 10.31915 - 1595.74))
        if v < 0:
            return 0
        return v

    def get_adcchannel(self):
        return self._channel

class FilteredIn:
    def __init__(self, pin):
        self._pin = pin
        self._value = None
        self._last_value = None
        self._last_ts = None

    def __call__(self):
        return self.value()

    def value(self):
        return self._value

    def id(self):
        return self._pin.id()

class Filter:
    def __init__(self, io, digital_stable_ms=50, analog_stable_ms=50, min_var_mV=100, min_var_uA=100):
        self._io = io
        self._digital_stable_ms = digital_stable_ms
        self._analog_stable_ms = analog_stable_ms
        self._min_var_mV = min_var_mV
        self._min_var_uA = min_var_uA

        if io.DI1:
            self.DI1 = FilteredIn(io.DI1)
            self.AV1 = None
            self.AI1 = None
        else:
            self.AV1 = FilteredIn(io.AV1)
            self.AI1 = FilteredIn(io.AI1)
            self.DI1 = None

        if io.DI2:
            self.DI2 = FilteredIn(io.DI2)
            self.AV2 = None
            self.AI2 = None
        else:
            self.AV2 = FilteredIn(io.AV2)
            self.AI2 = FilteredIn(io.AI2)
            self.DI2 = None

        if io.DI3:
            self.DI3 = FilteredIn(io.DI3)
            self.AV3 = None
            self.AI3 = None
        else:
            self.AV3 = FilteredIn(io.AV3)
            self.AI3 = FilteredIn(io.AI3)
            self.DI3 = None

        if io.DI4:
            self.DI4 = FilteredIn(io.DI4)
            self.AV4 = None
            self.AI4 = None
        else:
            self.AV4 = FilteredIn(io.AV4)
            self.AI4 = FilteredIn(io.AI4)
            self.DI4 = None

        self.DI5 = FilteredIn(io.DI5)
        self.DI6 = FilteredIn(io.DI6)

    def process(self):
        changed = []

        if self.DI1 and self._update_input(self.DI1, self._digital_stable_ms, 0):
            changed.append(self.DI1)

        if self.DI2 and self._update_input(self.DI2, self._digital_stable_ms, 0):
            changed.append(self.DI2)

        if self.DI3 and self._update_input(self.DI3, self._digital_stable_ms, 0):
            changed.append(self.DI3)

        if self.DI4 and self._update_input(self.DI4, self._digital_stable_ms, 0):
            changed.append(self.DI4)

        if self.DI5 and self._update_input(self.DI5, self._digital_stable_ms, 0):
            changed.append(self.DI5)

        if self.DI6 and self._update_input(self.DI6, self._digital_stable_ms, 0):
            changed.append(self.DI6)

        if self.AV1 and self._update_input(self.AV1, self._analog_stable_ms, self._min_var_mV):
            changed.append(self.AV1)

        if self.AV2 and self._update_input(self.AV2, self._analog_stable_ms, self._min_var_mV):
            changed.append(self.AV2)

        if self.AV3 and self._update_input(self.AV3, self._analog_stable_ms, self._min_var_mV):
            changed.append(self.AV3)

        if self.AV4 and self._update_input(self.AV4, self._analog_stable_ms, self._min_var_mV):
            changed.append(self.AV4)

        if self.AI1 and self._update_input(self.AI1, self._analog_stable_ms, self._min_var_uA):
            changed.append(self.AI1)

        if self.AI2 and self._update_input(self.AI2, self._analog_stable_ms, self._min_var_uA):
            changed.append(self.AI2)

        if self.AI3 and self._update_input(self.AI3, self._analog_stable_ms, self._min_var_uA):
            changed.append(self.AI3)

        if self.AI4 and self._update_input(self.AI4, self._analog_stable_ms, self._min_var_uA):
            changed.append(self.AI4)

        return changed

    def _update_input(self, input, stable_ms, min_var):
        val = input._pin()
        ts = time.ticks_ms()

        if val != input._last_value:
            # TODO consider checking if the difference is negligible for analog values
            input._last_value = val
            input._last_ts = ts

        if input._last_ts == None or time.ticks_diff(input._last_ts, ts) >= stable_ms:
            if val != input._value:
                if input._value == None or abs(input._value - val) >= min_var:
                    input._value = val
                    return True

        return False

class IO:

    MODE_DIGITAL = const(0)
    MODE_ANALOG = const(1)

    def __init__(self, i1=MODE_DIGITAL, i2=MODE_DIGITAL, i3=MODE_DIGITAL, i4=MODE_DIGITAL):
        self.DO1 = IonoPin(id='DO1', pin='P21', mode=Pin.OUT, pull=None)
        self.DO2 = IonoPin('DO2', 'P23', mode=Pin.OUT)
        self.DO3 = IonoPin('DO3', 'P8', mode=Pin.OUT)
        self.DO4 = IonoPin('DO4', 'P11', mode=Pin.OUT)

        if i1 is MODE_DIGITAL:
            self.DI1 = IonoPin('DI1', 'P14', mode=Pin.IN, pull=None)
            self.AV1 = None
            self.AI1 = None
        else:
            chan = self._getADC().channel(pin='P14', attn=ADC.ATTN_11DB)
            self.AV1 = AV('AV1', chan)
            self.AI1 = AI('AI1', chan)
            self.DI1 = None

        if i2 is MODE_DIGITAL:
            self.DI2 = IonoPin('DI2', 'P13', mode=Pin.IN, pull=None)
            self.AV2 = None
            self.AI2 = None
        else:
            chan = self._getADC().channel(pin='P13', attn=ADC.ATTN_11DB)
            self.AV2 = AV('AV2', chan)
            self.AI2 = AI('AI2', chan)
            self.DI2 = None

        if i3 is MODE_DIGITAL:
            self.DI3 = IonoPin('DI3', 'P16', mode=Pin.IN, pull=None)
            self.AV3 = None
            self.AI3 = None
        else:
            chan = self._getADC().channel(pin='P16', attn=ADC.ATTN_11DB)
            self.AV3 = AV('AV3', chan)
            self.AI3 = AI('AI3', chan)
            self.DI3 = None

        if i4 is MODE_DIGITAL:
            self.DI4 = IonoPin('DI4', 'P15', mode=Pin.IN, pull=None)
            self.AV4 = None
            self.AI4 = None
        else:
            chan = self._getADC().channel(pin='P15', attn=ADC.ATTN_11DB)
            self.AV4 = AV('AV4', chan)
            self.AI4 = AI('AI4', chan)
            self.DI4 = None

        self.DI5 = IonoPin('DI5', 'P18', mode=Pin.IN, pull=None)
        self.DI6 = IonoPin('DI6', 'P17', mode=Pin.IN, pull=None)
        self.AO1 = DAC('P22')

    def _getADC(self):
        if not hasattr(self, '_adc'):
            self._adc = ADC()
        return self._adc

    def filter(self, digital_stable_ms=50, analog_stable_ms=50, min_var_mV=100, min_var_uA=100):
        return Filter(self, digital_stable_ms, analog_stable_ms, min_var_mV, min_var_uA)
