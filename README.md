# visprotocol
**visprotocol** is a python package for experimental acquisition and metadata handling in visual neuroscience experiments. It is designed to act as a relatively stable core package which can run on its own with very limited, demonstrative functionality. Functionality can be greatly expanded by using a lab or user-specific package, which should be maintained as a separate repository. Check out the wiki for instructions on how to build your own lab or user-specific package, and how to configure visprotocol for your use.

## Installation
Installation requires python3.9 or greater

First, install [flystim](https://github.com/ClandininLab/flystim) and [flyrpc](https://github.com/ClandininLab/flyrpc)

I recommend using a conda or other virtual environment, for example:

`conda create -n visprotocol python=3.9`

`conda activate visprotocol`

To install, cd to the top-level visprotocol directory, where setup.py lives, and run:

`pip install -e .`

## Getting started

The easiest entry point to explore visprotocol and test it out is to run the gui

cd to /gui and run

`python ExperimentGUI.py`

When you first run visprotocol, before configuring it, the experimental control window will pop up alongside a small stimulus presentation screen.

This includes very limited animal metadata options and only a couple very basic visual stimulus protocols, and stimuli are rendered into that small display window. To configure and extend visprotocol, check out the [wiki](https://github.com/ClandininLab/visprotocol/wiki).


