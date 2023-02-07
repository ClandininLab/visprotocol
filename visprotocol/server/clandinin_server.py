import signal, sys

from flystim.screen import Screen
from flystim.stim_server import launch_stim_server, StimServer
from visprotocol.device.daq.labjack import LabJackTSeries

class Server():
    def __init__(self, screens=[], loco_class=False, loco_kwargs={}, daq_class=None, daq_kwargs={}):
        if screens:
            self.manager = StimServer(screens=screens, host='', port=60629, auto_stop=False)
        else:
            self.manager = launch_stim_server(Screen(fullscreen=False, server_number=0, id=0, vsync=False))

        self.loco_manager = None
        self.daq_device = None        

        if loco_class is not None:    self.__set_up_loco__(loco_class, **loco_kwargs)
        if daq_class is not None:     self.__set_up_daq__(daq_class, **daq_kwargs)

        self.manager.black_corner_square()
        self.manager.set_idle_background(0)

        def signal_handler(sig, frame):
            print('Closing server after Ctrl+C...')
            self.close()
            sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)

    def loop(self):
        self.manager.loop()

    def close(self):
        if self.loco_manager is not None:
            self.loco_manager.close()
        if self.daq_device is not None:
            self.daq_device.close()
        self.manager.shutdown_flag.set()

    def __set_up_loco__(self, loco_class, **kwargs):
        self.loco_manager = loco_class(fs_manager=self.manager, start_at_init=False, **kwargs)
        self.manager.register_function_on_root(self.loco_manager.set_save_directory, "loco_set_save_directory")
        self.manager.register_function_on_root(self.loco_manager.start, "loco_start")
        self.manager.register_function_on_root(self.loco_manager.close, "loco_close")
        self.manager.register_function_on_root(self.loco_manager.set_pos_0, "loco_set_pos_0")
        self.manager.register_function_on_root(self.loco_manager.write_to_log, "loco_write_to_log")
        self.manager.register_function_on_root(self.loco_manager.loop_start, "loco_loop_start")
        self.manager.register_function_on_root(self.loco_manager.loop_stop, "loco_loop_stop")
        self.manager.register_function_on_root(self.loco_manager.loop_start_closed_loop, "loco_loop_start_closed_loop")
        self.manager.register_function_on_root(self.loco_manager.loop_stop_closed_loop, "loco_loop_stop_closed_loop")
        self.manager.register_function_on_root(self.loco_manager.loop_update_closed_loop_vars, "loco_loop_update_closed_loop_vars")
        # self.manager.register_function_on_root(self.loco_manager.sleep, "loco_sleep")
        # self.manager.register_function_on_root(self.loco_manager.update_pos, "loco_update_pos")
        # self.manager.register_function_on_root(self.loco_manager.update_pos_for, "loco_update_pos_for")

    def __set_up_daq__(self, daq_class, **kwargs):
        self.daq_device = daq_class(**kwargs)
        self.manager.register_function_on_root(self.daq_device.sendTrigger, "daq_sendTrigger")
        self.manager.register_function_on_root(self.daq_device.outputStep, "daq_outputStep")

        if daq_class == LabJackTSeries:
            self.manager.register_function_on_root(self.daq_device.setupPulseWaveStreamOut, "daq_setupPulseWaveStreamOut")
            self.manager.register_function_on_root(self.daq_device.startStream, "daq_startStream")
            self.manager.register_function_on_root(self.daq_device.stopStream, "daq_stopStream")
            self.manager.register_function_on_root(self.daq_device.streamWithTiming, "daq_streamWithTiming")
