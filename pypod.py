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
    ret_byte = highnibble << 4
    ret_byte = ret_byte | lownibble
    return ret_byte

def nib(in_byte):
    # reverse function of denib, for creating data to be sent to the pod
    highnibble = in_byte >> 4
    lownibble  = in_byte & 0b1111
    return highnibble, lownibble

# testing stuff:

# dump Program 1A
cmd = ['amidi', '-p', 'hw:2,0,0', '-S', 'F0 00 01 0C 01 00 00 00 F7', '-d', '-t', '2']
data = subprocess.check_output(cmd)
b = data.decode("utf-8").replace("\n","").split(" ")
#print(b)
offset = 9 # the first 9 bytes in the response do not count
realbytes = []
name = ""
for x in range(0,71):
    realbytes.append(denib(hextoint(b[x*2+offset]), hextoint(b[x*2+offset+1])))
    if x>54:
        # the last 16 (real) bytes are the patch name:
        name = name + chr(realbytes[x])
#for index in range(len(realbytes)):
#    print(realbytes[index], hex(realbytes[index]))
#print(name)

# test if the nib-function works:
b_recode = []
for index in range(len(realbytes)):
    highnibble, lownibble = nib(realbytes[index])
    b_recode.append(highnibble)
    b_recode.append(lownibble)
    x = denib(highnibble, lownibble)
    if x != realbytes[index]:
        print("ERROR: {} != {}".format(x,realbytes[index]))
    #else:
    #    print("index {:0>2} original: {:02X} recode: {:02X}".format(index, realbytes[index], x))

# let's play around some more and
# actually show what the values mean:
print("Patch Name: {}".format(name))
if realbytes[0] > 63:
    print("Distorton ON")
if realbytes[1] > 63:
    print("Drive ENABLED")
if realbytes[2] > 63:
    print("Presence ENABLED")
if realbytes[3] > 63:
    print("Delay ENABLED")
if realbytes[4] > 63:
    print("Tremolo/Chorus Flange ENABLED")
if realbytes[5] > 63:
    print("Reverb ENABLED")
if realbytes[6] > 63:
    print("Noise Gate ENABLED")
if realbytes[7] > 63:
    print("Bright Switch ON")
print("Amp Type: {}".format(realbytes[8]))
print("Drive: {}".format(realbytes[9]))
print("Drive 2: {}".format(realbytes[10]))
print("Bass: {}".format(realbytes[11]))
print("Mid: {}".format(realbytes[12]))
print("Treble: {}".format(realbytes[13]))
print("Presence: {}".format(realbytes[14]))
print("Channel Volume: {}".format(realbytes[15]))
