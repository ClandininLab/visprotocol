# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 12:09:02 2019

@author: mhturner
"""

import sys
from PyQt5.QtWidgets import QApplication
from lazy5.ui.QtHdfLoad import HdfLoad

app = QApplication(sys.argv)

result = HdfLoad.getFileDataSets(pth='.')
print('Result: {}'.format(result))

sys.exit()