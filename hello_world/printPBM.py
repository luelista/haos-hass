#!/usr/bin/env python3
from ptouch import PTouch
import config
import sys
import random, string, math
from subprocess import check_call


pt = PTouch(config.serialPort)

args = sys.argv[1:]
with open(args[0], "r") as f:
    pt.readBufferPBM(f)

if not pt.showBufferTk():
	sys.exit(1)
    

pt.printBuffer()
pt.print(True)



