import numpy as np
import time
from visprotocol.device.daq import DAQ

from labjack import ljm

class LabJackTSeries(DAQ):
    def __init__(self, dev=None, trigger_channel=['FIO4'], init_device=True):
        super().__init__()  # call the parent class init method
        self.serial_number = dev
        self.trigger_channel = trigger_channel

        self.init_device()

    def init_device(self):
        # Initialize ljm T4/T7 handle
        self.handle = ljm.openS("TSERIES", "ANY", "ANY" if self.serial_number is None else self.serial_number)
        self.info = ljm.getHandleInfo(self.handle)
        self.deviceType = self.info[0]
        self.serial_number = self.info[2]

        self.is_open = True

        if self.deviceType == ljm.constants.dtT4:
            # LabJack T4 configuration

            # All analog input ranges are +/-1 V, stream settling is 0 (default) and
            # stream resolution index is 0 (default).
            aNames = ["AIN_ALL_RANGE", "STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX"]
            aValues = [10.0, 0, 0]

            # Configure FIO4 to FIO7 as digital I/O.
            ljm.eWriteName(self.handle, "DIO_INHIBIT", 0xFFF0F)
            ljm.eWriteName(self.handle, "DIO_ANALOG_ENABLE", 0x00000)
        else:
            # LabJack T7 and other devices configuration

            # Ensure triggered stream is disabled.
            ljm.eWriteName(self.handle, "STREAM_TRIGGER_INDEX", 0)

            # Enabling internally-clocked stream.
            ljm.eWriteName(self.handle, "STREAM_CLOCK_SOURCE", 0)

            # All analog input ranges are +/-1 V, stream settling is 6
            # and stream resolution index is 0 (default).
            aNames = ["AIN_ALL_RANGE", "STREAM_SETTLING_US", "STREAM_RESOLUTION_INDEX", "AIN_ALL_NEGATIVE_CH"]
            aValues = [10.0, 6, 0, 199]

        # Write the analog inputs' negative channels (when applicable), ranges,
        # stream settling time and stream resolution configuration.
        numFrames = len(aNames)
        ljm.eWriteNames(self.handle, numFrames, aNames, aValues)

    def set_trigger_channel(self, trigger_channel):
        self.trigger_channel = trigger_channel

    def write(self, names, vals):
        ljm.eWriteNames(self.handle, len(names), names, vals)

    def sendTrigger(self, trigger_channel=None, trigger_duration=0.05):
        if trigger_channel is None:
            trigger_channel = self.trigger_channel
        self.outputStep(output_channel=trigger_channel, low_time=0, high_time=trigger_duration, initial_delay=0)

    def outputStep(self, output_channel=['FIO4'], low_time=0.001, high_time=0.100, initial_delay=0.00):
        if not isinstance(output_channel, list):
            output_channel = [output_channel]

        write_states = np.ones(len(output_channel), dtype=int)
        if initial_delay > 0:
            time.sleep(initial_delay)
        if low_time > 0:
            self.write(output_channel, (write_states*0).tolist())
            time.sleep(low_time)
        if high_time > 0:
            self.write(output_channel, (write_states*1).tolist())
            time.sleep(high_time)
        self.write(output_channel, (write_states*0).tolist())

    def analogOutputStep(self, output_channel='DAC0', pre_time=0.5, step_time=1, tail_time=0.5, step_amp=0.5, dt=0.01):
        """
        Generate a voltage step with defined amplitude
            Step comes on at pre_time and goes off at pre_time+step_time

        output_channel: (str) name of analog output channel on device
        pre_time: (sec) time duration before the step comes on (v=0)
        step_time: (sec) duration that step is on
        tail_time: (sec) duration after step (v=0)
        step_amp: (V) amplitude of output step
        dt: (sec) time step size used to generate waveform

        """

        total_time = pre_time + step_time + tail_time
        t0 = time.time()
        clock_time = time.time() - t0  # sec since t0
        while clock_time < total_time:
            clock_time = time.time() - t0  # sec since t0
            if clock_time < pre_time:
                value = 0
            elif clock_time > pre_time and clock_time <= (pre_time+step_time):
                value = step_amp
            elif clock_time > (pre_time+step_time):
                value = 0
            else:
                value = 0
            ljm.eWriteName(self.handle, output_channel, value)
            time.sleep(dt)

    def setAnalogOutputToZero(self, output_channel='DAC0'):
        ljm.eWriteName(self.handle, output_channel, 0)

    def analogPeriodicOutput(self, output_channel='DAC0', pre_time=0.5, stim_time=1, waveform=[0], scanRate=5000, scansPerRead = 1000):
        """
        Repeat waveform for a defined duration.
            stim comes on at pre_time and goes off at pre_time+stim_time
        
        output_channel: (str) name of analog output channel on device
        pre_time: (sec) time duration before the stim comes on (v=0)
        stim_time: (sec) duration that stim is on
        waveform: (V) waveform to output repeatedly
        scanRate: (Hz) sampling rate of waveform
        scansPerRead: (int) number of samples to read at a time
        """

        ljm.periodicStreamOut(self.handle, ljm.nameToAddress(output_channel)[0], scanRate, len(waveform), waveform)
        time.sleep(pre_time)
        actualScanRate = ljm.eStreamStart(self.handle, scansPerRead, 1, [ljm.nameToAddress("STREAM_OUT0")[0]], scanRate)
        time.sleep(stim_time)
        ljm.eStreamStop(self.handle)
        ljm.eWriteName(self.handle, output_channel, 0)
    
    def squareWave(self, output_channel='DAC0', pre_time=0.5, stim_time=1, freq=100, amp=2.5, scanRate=5000, scansPerRead = 1000):
        """
        Generate a square wave with defined frequency and amplitude
            stim comes on at pre_time and goes off at pre_time+stim_time
        
        output_channel: (str) name of analog output channel on device
        pre_time: (sec) time duration before the stim comes on (v=0)
        stim_time: (sec) duration that stim is on
        freq: (Hz) frequency of output square wave
        amp: (V) amplitude of output square wave
        scanRate: (Hz) sampling rate of waveform
        scansPerRead: (int) number of samples to read at a time
        """

        waveform = np.zeros(int(scanRate/freq))
        waveform[0:int(scanRate/(2*freq))] = amp
        self.analogPeriodicOutput(output_channel=output_channel, pre_time=pre_time, stim_time=stim_time, waveform=waveform, scanRate=scanRate, scansPerRead=scansPerRead)

    def close(self):
        if self.is_open:
            ljm.close(self.handle)
            self.is_open = False

