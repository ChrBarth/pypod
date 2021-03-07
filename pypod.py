#!/usr/bin/env python3

import sys
import time
import mido
import argparse
import line6

parser = argparse.ArgumentParser('pypod.py')
parser.add_argument('-d', '--dump-program', type=str,
                    help='Dumps given Program (e.g. 2B)',
                    dest='program')
parser.add_argument('-x', '--hex', action='store_true',
                    help='display values in hex instead of decimal')
parser.add_argument('-u', '--human-readable', action='store_true', help='display data in human readable format')
group = parser.add_mutually_exclusive_group()
group.add_argument('-s', '--save', type=str, help='Saves Settings to file', dest='tofile')
group.add_argument('-l', '--load', type=str, help='Loads Settings from file', dest='fromfile')
parser.add_argument('-i', '--info', action='store_true', help='Shows info about the POD 2.0')
parser.add_argument('-c', '--channel', type=int, help='Select MIDI-Channel (default: 1)', dest='midichan')

args=parser.parse_args()

if args.midichan:
    MIDI_CH = args.midichan
else:
    MIDI_CH = 1 # the default pod2 midi-channel

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
# global variables that get modified by the callback-function:
msg_bytes = []
program_name = ""
manufacturer_id = ""
product_family = ""
product_family_member = ""
pod_version = ""

# }}}

# {{{ functions:
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
    msg = mido.Message('sysex', data=[0x00, 0x01, 0x0c, 0x01, 0x00, 0x00, line6.PROGRAMS.index(program)])
    midi_port.send(msg)

def udq(midi_port):
    msg = mido.Message('sysex', data=[0x7e, MIDI_CH, 0x06, 0x01])
    midi_port.send(msg)
    time.sleep(1)

def parse_progdump(message):
    global msg_bytes
    msg_bytes = []
    program_name = ""
    offset = 1
    if len(message) == 152:
        offset = 7 # data starts after byte 9
    for x in range(0,72):
        msg_bytes.append(denib(message.bytes()[x*2+offset], message.bytes()[x*2+offset+1]))
        if x > 54:
            # the last 16 bytes are the program name
            program_name = program_name+chr(msg_bytes[x])
    return

def monitor_input(message):
    global msg_bytes
    global program_name
    global manufacturer_id
    global pod_version
    global product_family
    global product_family_member
    #print(message.type)
    # a single program dump is 152 bytes long (9 bytes header, 142 bytes data, &xF7 is the last byte)
    if message.type == 'sysex' and len(message.bytes()) == 152:
        parse_progdump(message)
    elif message.type == 'sysex' and len(message.bytes()) == 17:
        pod_version = "".join([chr(x) for x in message.bytes()[12:16]])
        manufacturer_id = "{:02X} {:02X} {:02X}".format(message.bytes()[5], message.bytes()[6], message.bytes()[7])
        product_family = "{:02X}{:02X}".format(message.bytes()[9], message.bytes()[8])
        product_family_member = "{:02X}{:02X}".format(message.bytes()[11], message.bytes()[10])
    else:
        print("Unknown message:")
        print(message.bytes(), len(message.bytes()))

# }}}

try:
    inport = mido.open_input(MIDI_IN)
except OSError:
    # open default instead:
    inport = mido.open_input()
inport.callback = monitor_input

try:
    outport = mido.open_output(MIDI_OUT)
except OSError:
    outport = mido.open_output()

def get_info():
    # get infos about the device:
    udq(outport)
    time.sleep(1)
    print("POD Version: {}".format(pod_version))
    print("Manufacturer ID: {}".format(manufacturer_id))
    print("Product Family ID: {}".format(product_family))
    print("Product Family Member: {}".format(product_family_member))

def dump(prog_name):
    print(f"Program: {prog_name}")
    print(f"Program name: {program_name}")
    if msg_bytes[1] > 63:
        print("Distorton ON")
    if msg_bytes[2] > 63:
        print("Drive ENABLED")
    if msg_bytes[3] > 63:
        print("Presence ENABLED")
    if msg_bytes[4] > 63:
        print("Delay ENABLED")
    if msg_bytes[5] > 63:
        print("Tremolo/Chorus Flange ENABLED")
    if msg_bytes[6] > 63:
        print("Reverb ENABLED")
    if msg_bytes[7] > 63:
        print("Noise Gate ENABLED")
    if msg_bytes[8] > 63:
        print("Bright Switch ON")
    print("Amp Type: {}".format(line6.amp_names[msg_bytes[9]]))
    print("Cab Type: {}".format(line6.cab_names[msg_bytes[45]]))
    print("AIR: {}".format(msg_bytes[46]))
    print("Drive: {}".format(msg_bytes[10]))
    print("Drive 2: {}".format(msg_bytes[11]))
    print("Bass: {}".format(msg_bytes[12]))
    print("Mid: {}".format(msg_bytes[13]))
    print("Treble: {}".format(msg_bytes[14]))
    print("Presence: {}".format(msg_bytes[15]))
    print("Channel Volume: {}".format(msg_bytes[16]))
    print("Noise Gate Threshhold: {}".format(msg_bytes[17]))
    print("Noise Gate Decay Time: {}".format(msg_bytes[18]))
    #19-25: Wah and Volume Pedal - since I don't have either, I will keep this out for now
    d_type = "Mono"
    if msg_bytes[26]>63:
        d_type = "Stereo"
    print("Delay Type: {}".format(d_type))
    # bytes 27-34: Delay L/R time (17 bits each) ???
    print("      L Feedback: {}".format(msg_bytes[35]))
    print("      L Level: {}".format(msg_bytes[37]))
    if d_type == "Stereo":
        print("      R Level: {}".format(msg_bytes[38]))
        print("      R Feedback: {}".format(msg_bytes[36]))
    r_type = "Hall"
    if msg_bytes[39]> 63:
        r_type = "Spring"
    print("Reverb Type: {}".format(r_type))
    print("Reverb Decay: {}".format(msg_bytes[40]))
    print("Reverb Tone: {}".format(msg_bytes[41]))
    print("Reverb Diffusion: {}".format(msg_bytes[42]))
    print("Reverb Density: {}".format(msg_bytes[43]))
    print("Reverb Level: {}".format(msg_bytes[44]))
    print("FX: {}".format(line6.fx_names[msg_bytes[47]]))
    print("FX Tweak: {}".format(msg_bytes[48]))
    comp = "OFF"
    if msg_bytes[47] == 7 or msg_bytes[47] == 11:
        if msg_bytes[49] == 1:
            comp = "1.4:1"
        if msg_bytes[49] == 2:
            comp = "2:1"
        if msg_bytes[49] == 3:
            comp = "3:1"
        if msg_bytes[49] == 4:
            comp = "6:1"
        if msg_bytes[49] == 5:
            comp = "INF:1"
        print("Compressor Ratio: {}".format(comp))

def dump_raw(**kwargs):
    if 'filename' in kwargs:
        # if filename is given, dump to syx file:
        # 0xf0 is the first byte of a sysex-command
        message = [0xf0]
        for m in msg_bytes[:]:
            h,l = nib(m)
            message.append(h)
            message.append(l)
        # 0xf7 is the last byte of a sysex-command
        message.append(0xf7)
        # generate mido.Message from message[:]
        msg = mido.Message.from_bytes(message[:])
        mido.write_syx_file(kwargs['filename'], (msg,))
    else:    
        print(*msg_bytes)

def dump_hex():
    # print values as hex
    hexbytes = []
    for b in msg_bytes[:]:
        hexbytes.append("{:02X}".format(b))
    print(*hexbytes)

def load_syx(filename):
    print(f"Reading from {filename}")
    messages = mido.read_syx_file(filename)
    message = mido.Message('sysex', data=messages[0].data)
    print(message)
    parse_progdump(message)
    dump_hex()

# parse arguments:
if args.info == True:
    get_info()

if args.fromfile:
    load_syx(args.fromfile)

if args.program:
    prog = str(args.program)
    try:
        dump_program(prog, outport)
        time.sleep(1)
    except ValueError:
        print("{} is not a valid POD Program name!".format(prog))
        sys.exit(1)

    if args.human_readable == True:
        dump(prog)
    else:
        if args.hex == True:
            dump_hex()
        else:
            if args.tofile:
                dump_raw(filename=args.tofile)
            else:
                dump_raw()
