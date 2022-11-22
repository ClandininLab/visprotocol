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
        t0 = time.time()  # TODO: remove
        total_time = pre_time + step_time + tail_time
        for t in np.arange(0, total_time, dt):
            if t < pre_time:
                value = 0
            elif t > pre_time and t <= (pre_time+step_time):
                value = step_amp
            elif t > (pre_time+step_time):
                value = 0
            else:
                value = 0
            ljm.eWriteName(self.handle, self.output_channel, value)

        print('dt={:3f}'.format(time.time()-t0))  # TODO: remove

    def close(self):
        if self.is_open:
            ljm.close(self.handle)
            self.is_open = False
