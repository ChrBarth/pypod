#!/usr/bin/env python3

import subprocess

CH = 1 # the default pod2 midi-channel

# some pod-midi-commands

AMP_MODEL = 12 # get/set amp-model

def hextoint(hexstring):
    # converts the string to the corresponding integer
    # for example: F0 -> 240
    hexstring = "0x" + hexstring
    return int(hexstring, 16)

def denib(highnibble, lownibble):
    # from https://medias.audiofanzine.com/files/lin020-477344.pdf:
    #POD sends and receives Program and Global dump data in High-Low Nibbilized format.
    #ONE POD BYTE (8 bits):0: A7 A6 A5 A4 A3 A2 A1 A0
    #TRANSMITTED and RECEIVED AS:
    #0: 00 00 00 00 A7 A6 A5 A4
    #1: 00 00 00 00 A3 A2 A1 A0
    ret_byte = hextoint(highnibble) << 4
    ret_byte = ret_byte | hextoint(lownibble)
    return ret_byte

# testing stuff:

# dump Program 1A
cmd = ['amidi', '-p', 'hw:2,0,0', '-S', 'F0 00 01 0C 01 00 00 00 F7', '-d', '-t', '1']
data = subprocess.check_output(cmd)
b = data.decode("utf-8").replace("\n","").split(" ")
print(b)
offset = 9 # the first 9 bytes in the response do not count
realbytes = []
name = ""
for x in range(0,71):
    realbytes.append(denib(b[x*2+offset], b[x*2+offset+1]))
    if x>54:
        # the last 16 (real) bytes are the patch name:
        name = name + chr(realbytes[x])
for index in range(len(realbytes)):
    print(realbytes[index], hex(realbytes[index]))
print(name)

