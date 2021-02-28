#!/usr/bin/env python3

import subprocess
#import threading
import time
import mido

# {{{ MIDI init:
MIDI_IN  = ""
MIDI_OUT = ""
inputs = mido.get_input_names()
for i in inputs:
    # we want to use the input that has the string "USB Midi Cable" in its name
    if "USB Midi Cable" in i:
        MIDI_IN = i
outputs = mido.get_output_names()
for o in outputs:
    # same goes for the midi output:
    if "USB Midi Cable" in o:
        MIDI_OUT = o
# }}}

# {{{ Some useful POD-Variables

# The Program names:
PROGRAMS = [ "1A", "1B", "1C", "1D",
             "2A", "2B", "2C", "2D",
             "3A", "3B", "3C", "3D",
             "4A", "4B", "4C", "4D",
             "5A", "5B", "5C", "5D",
             "6A", "6B", "6C", "6D",
             "7A", "7B", "7C", "7D",
             "8A", "8B", "8C", "8D",
             "9A", "9B", "9C", "9D" ]

# The Amp Models:
amp_names = [
    'Tube Preamp',
    'POD Clean Line 6',
    'POD Crunch Line 6',
    'POD Drive Line 6',
    'POD Layer Line 6',
    'Small Tweed',
    'Tweed Blues',
    'Black Panel',
    'Modern Class A',
    'Brit Class A',
    'Brit Blues',
    'Brit Classic',
    'Brit Hi Gain',
    'Rectified ’94',
    'Modern Hi Gain',
    'Fuzz Box',
    'Jazz Clean',
    'Boutique #1',
    'Boutique #2',
    'Brit Class A #2',
    'Brit Class A #3',
    'Small Tweed #2',
    'Black Panel #2',
    'Boutique #3',
    'California Crunch #1',
    'California Crunch #2',
    'Rectified #2',
    'Modern Hi Gain #2',
    'Line 6 Twang',
    'Line 6 Crunch #2',
    'Line 6 Blues',
    'Line 6 Insane' ]

# The Cab names:
cab_names = [
    "1x 8 ’60 Fender Tweed Champ",
    "1x12 ’52 Fender Tweed Deluxe",
    "1x12 ’60 Vox AC15",
    "1x12 ’64 Fender Blackface Deluxe",
    "1x12 ’98 Line 6 Flextone",
    "2x12 ’65 Fender Blackface Twin",
    "2x12 ’67 VOX AC30",
    "2x12 ’95 Matchless Chieftain",
    "2x12 ’98 Pod custom 2x12",
    "4x10 ’59 Fender Bassman",
    "4x10 ’98 Pod custom 4x10 cab",
    "4x12 ’96 Marshall with V30s",
    "4x12 ’78 Marshall with 70s",
    "4x12 ’97 Marshall off axis",
    "4x12 ’98 Pod custom 4x12",
    "No Cabinet" ]

# The effect types:
fx_names = [
    "Chorus2",
    "Flanger1",
    "Rotary",
    "Flanger2",
    "Delay/Chorus1",
    "Delay/Tremolo",
    "Delay",
    "Delay/Comp",
    "Chorus1",
    "Tremolo",
    "Bypass",
    "Compressor",
    "Delay/Chorus2",
    "Delay/Flanger1",
    "Delay/Swell",
    "Delay/Flanger2" ]

CH = 1 # the default pod2 midi-channel
# pod-midi-commands (CC)
AMP_MODEL = 12 # get/set amp-model

# }}}

# {{{ general functions:
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

def dump_program(program, midi_port):
    # dump a single program from the pod:
    msg = mido.Message('sysex', data=[0x00, 0x01, 0x0c, 0x01, 0x00, 0x00, PROGRAMS.index(program)])
    midi_port.send(msg)

# }}}
# testing stuff:

### TESTING USING mido:

def monitor_input(message):
    print(message)

inport = mido.open_input(MIDI_IN)
inport.callback = monitor_input
outport = mido.open_output(MIDI_OUT)
#msg = mido.Message('sysex', data=[0x7e, 0x7f, 0x06, 0x01])
#outport.send(msg)
dump_program("1A", outport)
time.sleep(1) # we need some time so the callback-function can grab the response


### TESTING USING amidi:
## dump Program 1A
#cmd = ['amidi', '-p', 'hw:2,0,0', '-S', 'F0 00 01 0C 01 00 00 00 F7', '-d', '-t', '2']
#data = subprocess.check_output(cmd)
#b = data.decode("utf-8").replace("\n","").split(" ")
##print(b)
#offset = 9 # the first 9 bytes in the response do not count
#realbytes = []
#name = ""
#for x in range(0,71):
#    realbytes.append(denib(hextoint(b[x*2+offset]), hextoint(b[x*2+offset+1])))
#    if x>54:
#        # the last 16 (real) bytes are the patch name:
#        name = name + chr(realbytes[x])
##for index in range(len(realbytes)):
##    print(realbytes[index], hex(realbytes[index]))
##print(name)
#
## test if the nib-function works:
#b_recode = []
#for index in range(len(realbytes)):
#    highnibble, lownibble = nib(realbytes[index])
#    b_recode.append(highnibble)
#    b_recode.append(lownibble)
#    x = denib(highnibble, lownibble)
#    if x != realbytes[index]:
#        print("ERROR: {} != {}".format(x,realbytes[index]))
#    #else:
#    #    print("index {:0>2} original: {:02X} recode: {:02X}".format(index, realbytes[index], x))
#
## let's play around some more and
## actually show what the values mean:
#print("Patch Name: {}".format(name))
#if realbytes[0] > 63:
#    print("Distorton ON")
#if realbytes[1] > 63:
#    print("Drive ENABLED")
#if realbytes[2] > 63:
#    print("Presence ENABLED")
#if realbytes[3] > 63:
#    print("Delay ENABLED")
#if realbytes[4] > 63:
#    print("Tremolo/Chorus Flange ENABLED")
#if realbytes[5] > 63:
#    print("Reverb ENABLED")
#if realbytes[6] > 63:
#    print("Noise Gate ENABLED")
#if realbytes[7] > 63:
#    print("Bright Switch ON")
#print("Amp Type: {}".format(realbytes[8]))
#print("Drive: {}".format(realbytes[9]))
#print("Drive 2: {}".format(realbytes[10]))
#print("Bass: {}".format(realbytes[11]))
#print("Mid: {}".format(realbytes[12]))
#print("Treble: {}".format(realbytes[13]))
#print("Presence: {}".format(realbytes[14]))
#print("Channel Volume: {}".format(realbytes[15]))
