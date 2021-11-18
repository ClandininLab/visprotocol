#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flystim.screen import Screen, SubScreen
from flystim.draw import draw_screens
from flystim.stim_server import StimServer
from flystim.dlpc350 import make_dlpc350_objects
from math import pi
import matplotlib.pyplot as plt

def main():
    # # Put lightcrafter(s) in pattern mode
    # dlpc350_objects = make_dlpc350_objects()
    # for dlpc350_object in dlpc350_objects:
    #      dlpc350_object.set_current(red=0, green = 0, blue = 1.0)
    #      dlpc350_object.pattern_mode(fps=120)
    #      dlpc350_object.pattern_mode(fps=120)

    test_screen = Screen(subscreens=[SubScreen()], id=0, fullscreen=False, vsync=True, square_size=(0.25, 0.25), square_loc=(-1.0, -1.0), name='Test', horizontal_flip=False)

    draw_screens([test_screen])
    plt.show()

    screens = [test_screen]
    port = 60629
    host = ''

    manager = StimServer(screens=screens, host=host, port=port, auto_stop=False)

    manager.black_corner_square()
    manager.set_idle_background(0)

    manager.loop()

if __name__ == '__main__':
    main()
