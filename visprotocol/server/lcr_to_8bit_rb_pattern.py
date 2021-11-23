# -*- coding: utf-8 -*-

import lightcrafter as lcr
import time

# Generate lightcrafter object and try to connect to it
dev = lcr.Lightcrafter(_isCheckOnly=False, _logLevel=3)
res = dev.connect()
if res[0] is not lcr.ERROR.OK:
  # No connection
  exit()

# Set LED enables (ON/OFF)
# See method in lightcrafter pkg to use
dev.setLEDEnabled([True, False, True], _enableSeqCtrl=True)

# Set LED currents [r, g, b], on [0, 255]
# Default=[104, 135, 130]
# WARNING: don't set these too high for now...
dev.setLEDCurrents([104, 0, 130])

# Print report and video signal status
dev.getFirmwareVersion()
dev.getHardwareStatus()
dev.getMainStatus()
dev.getSystemStatus()
dev.getVideoSignalDetectStatus()

dev.stopPatternSequence()

# Select pattern sequence mode
dev.setDisplayMode(lcr.DispMode.Pattern)

# Select the 24bit RGB stream as input
dev.setPatternDisplayDataInputSource(lcr.SourcePat.Parallel)

# Setup LUT:
# 2 LUT entries, repeat sequence, 2 patterns/sequence, n/a
dev.setPatternDispLUTControl(2, True, 2, 1)

# Set trigger mode to VSYNC
dev.setPatternTriggerMode(lcr.PatTrigMode.Vsync_fixedExposure)

# Set exposure time, frame rate (in usec)
dev.setPatternExpTimeFrPer(16666, 16666)

# Open LUT mailbox for pattern sequence mode (external input)
dev.setPatternDispLUTAccessControl(lcr.MailboxCmd.OpenPat)

# LUT entry #0 ...
dev.setPatternDispLUTOffsetPointer(0)
# Pattern R0-R7, internal trigger, 8 bit, red LED
dev.setPatternDispLUTData(lcr.MailboxPat.R76543210,
                          lcr.MailboxTrig.ExternalPos,
                          8, lcr.MailboxLED.Red)
# LUT entry #1 ...
dev.setPatternDispLUTOffsetPointer(1)
# Pattern B0-B7, internal trigger, 8 bit, blue LED, trigger out 1 stays high
# to share time with previous pattern
dev.setPatternDispLUTData(lcr.MailboxPat.B76543210,
                          lcr.MailboxTrig.None_,
                          8, lcr.MailboxLED.Blue,
                          _trigOut1High=True)

# Close LUT mailbox
dev.setPatternDispLUTAccessControl(lcr.MailboxCmd.Close)

# Validate pattern sequence
res = dev.validateDataCommandResponse()

if res[0] == lcr.ERROR.OK: # and res[1]:
  dev.getHardwareStatus()
  dev.getMainStatus()
  time.sleep(1)
  dev.startPatternSequence()
  time.sleep(1)

dev.getMainStatus()
dev.getSystemStatus()

dev.disconnect()
