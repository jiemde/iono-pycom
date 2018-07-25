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

    def __call__(self, val=None):
        if val is None:
            return self._pin()
        else:
            self._pin(val)

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

class AO:
    def __init__(self, id, dac):
        self._iono_id = id
        self._dac = dac
        self._value = 0

    def __call__(self, val=None):
        if val is None:
            return self._value
        else:
            self._dac.write(val / 10000)
            self._value = val

    def id(self):
        return self._iono_id

    def get_dac(self):
        return self._dac

class FilteredPin:
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

        self.DO1 = FilteredPin(io.DO1)
        self.DO2 = FilteredPin(io.DO2)
        self.DO3 = FilteredPin(io.DO3)
        self.DO4 = FilteredPin(io.DO4)

        self.all = [self.DO1, self.DO2, self.DO3, self.DO4]

        if io.DI1:
            self.DI1 = FilteredPin(io.DI1)
            self.AV1 = None
            self.AI1 = None
            self.all.append(self.DI1)
        elif io.AV1:
            self.AV1 = FilteredPin(io.AV1)
            self.AI1 = None
            self.DI1 = None
            self.all.append(self.AV1)
        else:
            self.AI1 = FilteredPin(io.AI1)
            self.AV1 = None
            self.DI1 = None
            self.all.append(self.AI1)

        if io.DI2:
            self.DI2 = FilteredPin(io.DI2)
            self.AV2 = None
            self.AI2 = None
            self.all.append(self.DI2)
        elif io.AV2:
            self.AV2 = FilteredPin(io.AV2)
            self.AI2 = None
            self.DI2 = None
            self.all.append(self.AV2)
        else:
            self.AI2 = FilteredPin(io.AI2)
            self.AV2 = None
            self.DI2 = None
            self.all.append(self.AI2)

        if io.DI3:
            self.DI3 = FilteredPin(io.DI3)
            self.AV3 = None
            self.AI3 = None
            self.all.append(self.DI3)
        elif io.AV3:
            self.AV3 = FilteredPin(io.AV3)
            self.AI3 = None
            self.DI3 = None
            self.all.append(self.AV3)
        else:
            self.AI3 = FilteredPin(io.AI3)
            self.AV3 = None
            self.DI3 = None
            self.all.append(self.AI3)

        if io.DI4:
            self.DI4 = FilteredPin(io.DI4)
            self.AV4 = None
            self.AI4 = None
            self.all.append(self.DI4)
        elif io.AV4:
            self.AV4 = FilteredPin(io.AV4)
            self.AI4 = None
            self.DI4 = None
            self.all.append(self.AV4)
        else:
            self.AI4 = FilteredPin(io.AI4)
            self.AV4 = None
            self.DI4 = None
            self.all.append(self.AI4)

        self.DI5 = FilteredPin(io.DI5)
        self.DI6 = FilteredPin(io.DI6)
        self.AO1 = FilteredPin(io.AO1)

        self.all.append(self.DI5)
        self.all.append(self.DI6)
        self.all.append(self.AO1)

    def process(self):
        changed = []

        if self._update_input(self.DO1, 0, 0):
            changed.append(self.DO1)

        if self._update_input(self.DO2, 0, 0):
            changed.append(self.DO2)

        if self._update_input(self.DO3, 0, 0):
            changed.append(self.DO3)

        if self._update_input(self.DO4, 0, 0):
            changed.append(self.DO4)

        if self.DI1 and self._update_input(self.DI1, self._digital_stable_ms, 0):
            changed.append(self.DI1)

        if self.DI2 and self._update_input(self.DI2, self._digital_stable_ms, 0):
            changed.append(self.DI2)

        if self.DI3 and self._update_input(self.DI3, self._digital_stable_ms, 0):
            changed.append(self.DI3)

        if self.DI4 and self._update_input(self.DI4, self._digital_stable_ms, 0):
            changed.append(self.DI4)

        if self._update_input(self.DI5, self._digital_stable_ms, 0):
            changed.append(self.DI5)

        if self._update_input(self.DI6, self._digital_stable_ms, 0):
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

        if self._update_input(self.AO1, 0, 0):
            changed.append(self.AO1)

        return changed

    def _update_input(self, input, stable_ms, min_var):
        val = input._pin()
        ts = time.ticks_ms()

        if input._value != val:
            if input._value == None or abs(input._value - val) >= min_var:
                if input._value == None or time.ticks_diff(input._last_ts, ts) >= stable_ms:
                    input._value = val
                    input._last_ts = ts
                    return True
            else:
                input._last_ts = ts
        else:
            input._last_ts = ts

        return False

class IO:

    MODE_D = const(0)
    MODE_V = const(1)
    MODE_I = const(2)

    def __init__(self, i1=MODE_D, i2=MODE_D, i3=MODE_D, i4=MODE_D):
        self.DO1 = IonoPin('DO1', 'P21', mode=Pin.OUT)
        self.DO2 = IonoPin('DO2', 'P23', mode=Pin.OUT)
        self.DO3 = IonoPin('DO3', 'P8', mode=Pin.OUT)
        self.DO4 = IonoPin('DO4', 'P11', mode=Pin.OUT)

        self.all = [self.DO1, self.DO2, self.DO3, self.DO4]

        if i1 is MODE_V:
            chan = self._getADC().channel(pin='P14', attn=ADC.ATTN_11DB)
            self.AV1 = AV('AV1', chan)
            self.AI1 = None
            self.DI1 = None
            self.all.append(self.AV1)
        elif i1 is MODE_I:
            chan = self._getADC().channel(pin='P14', attn=ADC.ATTN_11DB)
            self.AI1 = AV('AI1', chan)
            self.AV1 = None
            self.DI1 = None
            self.all.append(self.AI1)
        else:
            self.DI1 = IonoPin('DI1', 'P14', mode=Pin.IN, pull=None)
            self.AV1 = None
            self.AI1 = None
            self.all.append(self.DI1)

        if i2 is MODE_V:
            chan = self._getADC().channel(pin='P13', attn=ADC.ATTN_11DB)
            self.AV2 = AV('AV2', chan)
            self.AI2 = None
            self.DI2 = None
            self.all.append(self.AV2)
        elif i2 is MODE_I:
            chan = self._getADC().channel(pin='P13', attn=ADC.ATTN_11DB)
            self.AI2 = AV('AI2', chan)
            self.AV2 = None
            self.DI2 = None
            self.all.append(self.AI2)
        else:
            self.DI2 = IonoPin('DI2', 'P13', mode=Pin.IN, pull=None)
            self.AV2 = None
            self.AI2 = None
            self.all.append(self.DI2)

        if i3 is MODE_V:
            chan = self._getADC().channel(pin='P16', attn=ADC.ATTN_11DB)
            self.AV3 = AV('AV3', chan)
            self.AI3 = None
            self.DI3 = None
            self.all.append(self.AV3)
        elif i3 is MODE_I:
            chan = self._getADC().channel(pin='P16', attn=ADC.ATTN_11DB)
            self.AI3 = AV('AI3', chan)
            self.AV3 = None
            self.DI3 = None
            self.all.append(self.AI3)
        else:
            self.DI3 = IonoPin('DI3', 'P16', mode=Pin.IN, pull=None)
            self.AV3 = None
            self.AI3 = None
            self.all.append(self.DI3)

        if i4 is MODE_V:
            chan = self._getADC().channel(pin='P15', attn=ADC.ATTN_11DB)
            self.AV4 = AV('AV4', chan)
            self.AI4 = None
            self.DI4 = None
            self.all.append(self.AV4)
        elif i4 is MODE_I:
            chan = self._getADC().channel(pin='P15', attn=ADC.ATTN_11DB)
            self.AI4 = AV('AI4', chan)
            self.AV4 = None
            self.DI4 = None
            self.all.append(self.AI4)
        else:
            self.DI4 = IonoPin('DI4', 'P15', mode=Pin.IN, pull=None)
            self.AV4 = None
            self.AI4 = None
            self.all.append(self.DI4)

        self.DI5 = IonoPin('DI5', 'P18', mode=Pin.IN, pull=None)
        self.DI6 = IonoPin('DI6', 'P17', mode=Pin.IN, pull=None)
        self.AO1 = AO('AO1', DAC('P22'))

        self.all.append(self.DI5)
        self.all.append(self.DI6)
        self.all.append(self.AO1)

    def _getADC(self):
        if not hasattr(self, '_adc'):
            self._adc = ADC()
        return self._adc

    def filter(self, digital_stable_ms=50, analog_stable_ms=50, min_var_mV=100, min_var_uA=100):
        return Filter(self, digital_stable_ms, analog_stable_ms, min_var_mV, min_var_uA)
