#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flystim.launch import StimManager, stim_server
from flystim.screen import Screen
from sys import platform


def main():
    screens = [Screen()]

    # # # Parameters for the screen # # # 
    if platform == "darwin": #OSX (laptop, for dev.)
        FullScreen = False
        ScreenID = 0
    elif platform == "win32": #Windows (rig computer)
        FullScreen = True
        ScreenID = 1
     
    # Define screen(s) for the rig you use
    w = 14.2e-2; h = 9e-2; # meters of image at projection plane, screen only shows 9x9 of this
    zDistToScreen = 5.36e-2; # meters
    screens = [Screen(width=w, height=h, rotation=None, offset=(0, zDistToScreen, 0), id=ScreenID, fullscreen=FullScreen, vsync=None,
                 square_side=2e-2, square_loc='lr')]
    
    manager = StimManager(screens)
    manager.black_corner_square()
    manager.set_idle_background(0)
    stim_server(manager)

if __name__ == '__main__':
    main()
