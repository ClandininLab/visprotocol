from visprotocol.device.daq import DAQ

import nidaqmx
from nidaqmx.types import CtrTime

class NIUSB6210(DAQ):
    """
    https://www.ni.com/en-us/support/model.usb-6210.html
    """
    def __init__(self, dev='Dev5', trigger_channel='ctr0'):
        super().__init__()  # call the parent class init method
        self.dev = dev
        self.trigger_channel = trigger_channel

    def sendTrigger(self):
        with nidaqmx.Task() as task:
            task.co_channels.add_co_pulse_chan_time('{}/{}'.format(self.dev, self.trigger_channel),
                                                    low_time=0.002,
                                                    high_time=0.001)
            task.start()

    def outputStep(self, output_channel='ctr1', low_time=0.001, high_time=0.100, initial_delay=0.00):
        with nidaqmx.Task() as task:
            task.co_channels.add_co_pulse_chan_time('{}/{}'.format(self.dev, output_channel),
                                                    low_time=low_time,
                                                    high_time=high_time,
                                                    initial_delay=initial_delay)

            task.start()
            task.wait_until_done()
            task.stop()


class NIUSB6001(DAQ):
    """
    https://www.ni.com/en-us/support/model.usb-6001.html
    """
    def __init__(self, dev='Dev1', trigger_channel='port2/line0'):
        super().__init__()  # call the parent class init method
        self.dev = dev
        self.trigger_channel = trigger_channel

    def sendTrigger(self):
        with nidaqmx.Task() as task:
            task.do_channels.add_do_chan('{}/{}'.format(self.dev, self.trigger_channel))
            task.start()
            task.write([True, False])
