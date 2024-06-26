import os
import socket, select
import threading
import json
from math import degrees
from time import time, sleep

class LocoManager():
    def __init__(self) -> None:
        pass

class LocoSocketManager():
    def __init__(self, host, port, udp=True) -> None:
        self.host = host
        self.port = port
        self.udp = udp

        self.sock = None
        self.sock_buffer = ""
        self.data_prev = []

    def connect(self):
        '''
        Open / connect to socket
        '''
        if self.udp:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.host, self.port))
            self.sock.setblocking(0)
        else: # TCP
            # TODO: Maybe need to listen for connection? This should be a server, receiving requests from locomotion source (e.g. Fictrac)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))

    def close(self):
        if self.sock is not None:
            self.sock.close()

    def get_line(self, wait_for=None):
        '''
        Assumes that lines are separated by '\n'
        '''
        if self.sock is None:
            return
        
        ##
        # if wait_for is None:
        #     ready = select.select([self.sock], [], [])[0]
        # else:
        #     ready = select.select([self.sock], [], [], wait_for)[0]

        # if ready:
        #     new_data = self.sock.recv(4096)
        # else:
        #     return self.get_line(wait_for=wait_for)
        ##

        ##
        ready = []
        while not ready:
            if self.sock == -1:
                print('\nSocket disconnected.')
                return None
            if wait_for is None:
                ready = select.select([self.sock], [], [])[0]
            else:
                ready = select.select([self.sock], [], [], wait_for)[0]
        new_data = self.sock.recv(4096)
        ##

        if not new_data and not self.udp: # TCP and blank new_data...
            print('\nDisconnected from TCP server.')
            return None

        # Decode received data
        self.sock_buffer += new_data.decode('UTF-8')

        # Find the first frame of data
        endline = self.sock_buffer.find("\n")
        if endline == -1:
            return self.get_line(wait_for=wait_for)
        line = self.sock_buffer[:endline]       # copy first frame
        self.sock_buffer = self.sock_buffer[endline+1:]     # delete first frame

        return line

class LocoClosedLoopManager():
    def __init__(self, fs_manager, host, port, save_directory=None, start_at_init=False, udp=True) -> None:
        super().__init__()
        self.fs_manager = fs_manager
        self.socket_manager = LocoSocketManager(host=host, port=port, udp=udp)
        
        self.save_directory = save_directory
        self.log_file = None

        self.data_prev = []
        self.pos_0 = {'theta': 0, 'x': 0, 'y': 0, 'z': 0}

        self.loop_attrs = {
            'thread': None,
            'looping': False,
            'closed_loop': False,
            'update_theta': True,
            'update_x': False,
            'update_y': False,
            'update_z': False
        }

        if start_at_init:
            self.start()
        
    def set_save_directory(self, save_directory):
        self.save_directory = save_directory
        
    def start(self):
        self.socket_manager.connect()
        
        if self.save_directory is not None:
            os.makedirs(self.save_directory, exist_ok=True)
            log_path = os.path.join(self.save_directory, 'log.txt')
            self.log_file = open(log_path, "a")

        self.started = True

    def close(self):
        if self.is_looping():
            self.loop_stop()

        self.socket_manager.close()
        
        if self.log_file is not None:
            self.log_file.flush()
            self.log_file.close()
            self.log_file = None
            
        self.started = False

    def get_data(self, wait_for=None):
        line = self.socket_manager.get_line(wait_for=wait_for)
        
        data = self._parse_line(line)
        self.data_prev = data

        return data
    
    def _parse_line(self, line):
        # TODO: Check line and parse line

        toks = line.split(", ")
        
        print("Please implement __parse_line in the inheriting class!")

        theta = 0
        x = 0
        y = 0
        z = 0
        frame_num = 0
        ts = 0
        
        return {'theta': theta, 'x': x, 'y': y, 'z': z, 'frame_num': frame_num, 'ts': ts}
  
    def set_pos_0(self, theta_0=None, x_0=0, y_0=0, z_0=0, use_data_prev=True, write_log=False):
        '''
        Sets position 0 for flystim manager.
        
        theta_0, x_0, y_0, z_0: 
            if None, the current value is acquired from socket.
        '''
        self.fs_manager.set_global_theta_offset(0) #radians
        self.fs_manager.set_global_fly_pos(0, 0, 0)

        if None in [theta_0, x_0, y_0, z_0]:
            if use_data_prev and len(self.data_prev)!=0:
                data = self.data_prev
            else:
                data = self.get_data()

            if theta_0 is None: theta_0 = float(data['theta'])
            if     x_0 is None:     x_0 = float(data['x'])
            if     y_0 is None:     y_0 = float(data['y'])
            if     z_0 is None:     z_0 = float(data['z'])
        
            frame_num = int(data['frame_num'])
            ts = float(data['ts'])
        else:
            frame_num = -1
            ts = None

        self.pos_0['theta'] = theta_0
        self.pos_0['x']     = x_0
        self.pos_0['y']     = y_0
        self.pos_0['z']     = z_0
        
        if write_log and self.log_file is not None:
            if ts is None:
                ts = time()
            log_line = json.dumps({'set_pos_0': {'frame_num': frame_num, 'theta': theta_0, 'x': x_0, 'y': y_0, 'z': z_0}, 'ts': ts})
            self.write_to_log(log_line)
    
    def write_to_log(self, string):
        if self.log_file is not None:
            self.log_file.write(str(string) + "\n")

    def update_pos(self, update_theta=True, update_x=False, update_y=False, update_z=False):
        data = self.get_data()

        data_to_return = {}
        
        if update_theta:
            theta = float(data['theta']) - self.pos_0['theta']
            self.fs_manager.set_global_theta_offset(degrees(theta))
            data_to_return['theta'] = theta #radians

        if update_x:
            x = float(data['x']) - self.pos_0['x']
            self.fs_manager.set_global_fly_x(x)
            data_to_return['x'] = x

        if update_y:
            y = float(data['y']) - self.pos_0['y']
            self.fs_manager.set_global_fly_y(y)
            data_to_return['y'] = y

        if update_z:
            z = float(data['z']) - self.pos_0['z']
            self.fs_manager.set_global_fly_z(z)
            data_to_return['z'] = z

        return data_to_return

    def is_looping(self):
        return self.loop_attrs['looping']

    def loop_start(self):
        def loop_helper():
            self.loop_attrs['looping'] = True
            while self.loop_attrs['looping']:
                if self.loop_attrs['closed_loop']:
                    _ = self.update_pos(update_theta = self.loop_attrs['update_theta'], 
                                        update_x     = self.loop_attrs['update_x'], 
                                        update_y     = self.loop_attrs['update_y'],
                                        update_z     = self.loop_attrs['update_z'])
                else:
                    _ = self.get_data()

        if self.loop_attrs['looping']:
            print("Already looping")
        else:
            self.loop_attrs['thread'] = threading.Thread(target=loop_helper, daemon=True)
            self.loop_attrs['thread'].start()

    def loop_stop(self):
        self.loop_attrs['looping'] = False
        self.loop_attrs['closed_loop'] = False
        if self.loop_attrs['thread'] is not None:
            self.loop_attrs['thread'].join(timeout=5)
            self.loop_attrs['thread'] = None

    def loop_start_closed_loop(self):
        self.loop_attrs['closed_loop'] = True

    def loop_stop_closed_loop(self):
        self.loop_attrs['closed_loop'] = False

    def loop_update_closed_loop_vars(self, update_theta=True, update_x=False, update_y=False, update_z=False):
        self.loop_attrs['update_theta'] = update_theta
        self.loop_attrs['update_x']     = update_x
        self.loop_attrs['update_y']     = update_y
        self.loop_attrs['update_z']     = update_z


