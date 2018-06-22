#!/usr/bin/env python3

# Example server program for one screen.
# Please start this program first before launching client.py.  You can exit the server by pressing Ctrl+C.

# In order to display perspective-corrected stimuli, you will need to modify this program so that the Screen
# object is instantiated with the right screen dimensions, and you should also set fullscreen=True.

from flystim.launch import launch
from flystim.screen import Screen

def main(port=62632):
    w = 14.2e-2; h = 9e-2; # m of image at projection plane, screen only shows 9x9 of this
    zDistToScreen = 5.36e-2; # m

    screens = [Screen(width=w, height=h, rotation=None, offset=(0, zDistToScreen, 0), id=0, fullscreen=False, vsync=None,
                 square_side=0e-2, square_loc='lr')]
    launch(screens=screens, port=port)

if __name__ == '__main__':
    main()
