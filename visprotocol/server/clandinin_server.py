import signal, sys

from flystim.screen import Screen
from flystim.stim_server import launch_stim_server, StimServer

from ftutil.ft_managers import FtClosedLoopManager

from visprotocol.device import daq

class Server():
    def __init__(self, screens=[], do_fictrac=False, fictrac_kwargs={}, daq_class=None, daq_kwargs={}):
        if screens:
            self.manager = StimServer(screens=screens, host='', port=60629, auto_stop=False)
        else:
            self.manager = launch_stim_server(Screen(fullscreen=False, server_number=0, id=0, vsync=False))
        
        if do_fictrac:                self.__set_up_fictrac__(**fictrac_kwargs)
        if daq_class is not None:     self.__set_up_daq__(daq_class, **daq_kwargs)

        self.manager.black_corner_square()
        self.manager.set_idle_background(0)

        def signal_handler(sig, frame):
            print('Closing server after Ctrl+C...')
            self.close()
            # sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)

    def loop(self):
        self.manager.loop()

    def close(self):
        self.manager.shutdown_flag.set()
        self.ft_manager.close()
        self.daq_device.close()

    def __set_up_fictrac__(self, **kwargs):
        self.ft_manager = FtClosedLoopManager(fs_manager=self.manager, start_at_init=False, **kwargs)
        self.manager.register_function_on_root(self.ft_manager.set_cwd, "ft_set_cwd")
        self.manager.register_function_on_root(self.ft_manager.start, "ft_start")
        self.manager.register_function_on_root(self.ft_manager.close, "ft_close")
        self.manager.register_function_on_root(self.ft_manager.set_pos_0, "ft_set_pos_0")
        self.manager.register_function_on_root(self.ft_manager.loop_start, "ft_loop_start")
        self.manager.register_function_on_root(self.ft_manager.loop_stop, "ft_loop_stop")
        self.manager.register_function_on_root(self.ft_manager.loop_start_closed_loop, "ft_loop_start_closed_loop")
        self.manager.register_function_on_root(self.ft_manager.loop_stop_closed_loop, "ft_loop_stop_closed_loop")
        self.manager.register_function_on_root(self.ft_manager.loop_update_closed_loop_vars, "ft_loop_update_closed_loop_vars")
        # self.manager.register_function_on_root(self.ft_manager.sleep, "ft_sleep")
        # self.manager.register_function_on_root(self.ft_manager.update_pos, "ft_update_pos")
        # self.manager.register_function_on_root(self.ft_manager.update_pos_for, "ft_update_pos_for")

    def __set_up_daq__(self, daq_class=daq.LabJackTSeries, **kwargs):
        self.daq_device = daq_class(**kwargs)
        self.manager.register_function_on_root(self.daq_device.sendTrigger, "daq_sendTrigger")
        self.manager.register_function_on_root(self.daq_device.outputStep, "daq_outputStep")

