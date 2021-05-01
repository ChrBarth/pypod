#!/usr/bin/env python3

import sys
import time
import mido
import argparse
import line6
import logging
import json
import os


# {{{ the class:
class pyPOD:

    midi_channel = 1
    msg_bytes = []
    manufacturer_id = ""
    pod_version = ""
    product_family = ""
    product_family_member = ""
    inport = mido.open_input()
    outport = mido.open_output()
    logger = logging.getLogger("pyPod")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s -  %(name)s -  %(levelname)s - %(funcName)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    def __init__(self):
        self.logger.debug('init pyPOD')
        self.inport.callback = self.monitor_input
        self.load_config()

    def load_config(self):
        self.logger.debug('looking for config')
        rcfile = "/.pypodrc"
        homerc = os.environ['HOME'] + rcfile
        pwdrc  = os.environ['PWD'] + rcfile
        rcfile = ""
        config = ""
        if os.path.isfile(homerc):
            self.logger.debug(f"found {homerc}")
            rcfile = homerc
        elif os.path.isfile(pwdrc):
            self.logger.debug(f"found {pwdrc}")
            rcfile = pwdrc
        else:
            self.logger.info("no config file found")
        if rcfile != "":
            with open(rcfile, "r") as fd:
                config = json.load(fd)
            if 'MIDI_IN' in config.keys():
                self.logger.debug(f"MIDI_IN: {config['MIDI_IN']}")
                self.connect_input(config['MIDI_IN'])
            if 'MIDI_OUT' in config.keys():
                self.logger.debug(f"MIDI_OUT: {config['MIDI_OUT']}")
                self.connect_output(config['MIDI_OUT'])
            if 'MIDI_CHAN' in config.keys():
                self.logger.debug(f"MIDI_CHAN: {config['MIDI_CHAN']}")
                self.midi_channel = int(config['MIDI_CHAN'])

    def connect_input(self, midi_in):
        self.logger.info(f"connecting to input {midi_in}")
        try:
            self.inport = mido.open_input(midi_in)
        except OSError:
            # open default instead:
            self.logger.warning("error opening input, using default")
            self.inport = mido.open_input()
        self.inport.callback = self.monitor_input

    def connect_output(self, midi_out):
        self.logger.info(f"connecting to output {midi_out}")
        try:
            self.outport = mido.open_output(midi_out)
        except OSError:
            self.logger.warning("error opening output, using default")
            self.outport = mido.open_output()

    def show_midiports(self):
        # a little helper-function for the command line
        # run this script with the -o parameter --show-midiports
        # and put the name of the connected midi-port in the config
        inports = mido.get_input_names()
        outports = mido.get_output_names()
        return inports, outports

    def denib(self, highnibble, lownibble):
        # from https://medias.audiofanzine.com/files/lin020-477344.pdf:
        #POD sends and receives Program and Global dump data in High-Low Nibbilized format.
        #ONE POD BYTE (8 bits):0: A7 A6 A5 A4 A3 A2 A1 A0
        #TRANSMITTED and RECEIVED AS:
        #0: 00 00 00 00 A7 A6 A5 A4
        #1: 00 00 00 00 A3 A2 A1 A0
        ret_byte = highnibble << 4
        ret_byte = ret_byte | lownibble
        return ret_byte

    def nib(self, in_byte):
        # reverse function of denib, for creating data to be sent to the pod
        highnibble = in_byte >> 4
        lownibble  = in_byte & 0b1111
        return highnibble, lownibble
    
    def dump_editbuffer(self):
        self.logger.info("dumping edit bufer")
        msg = mido.Message('sysex', data=[0x00, 0x01, 0x0c, 0x01, 0x00, 0x01])
        self.outport.send(msg)

    def dump_program(self, program):
        # dump a single program from the pod:
        self.logger.info(f"Dumping program {program} from pod")
        msg = mido.Message('sysex', data=[0x00, 0x01, 0x0c, 0x01, 0x00, 0x00, line6.PROGRAMS.index(program)])
        self.outport.send(msg)

    def upload_editbuffer(self, message):
        self.logger.info("Upload edit buffer")
        msg = mido.Message('sysex', data=[0x00, 0x01, 0x0c, 0x01, 0x01, 0x01])
        msg.data += message.data[1:]
        self.outport.send(msg)

    def upload_program(self, program):
        self.logger.info(f"Upload program {program}")
        # uploads a single program to the pod:
        msg = mido.Message('sysex', data=[0x00, 0x01, 0x0c, 0x01, 0x01, 0x00, line6.PROGRAMS.index(program)])
        # somehow we have to cut the first element, I have no idea why
        # found out because uploading did not work and compared data-dumps
        # from jsynthlib with mine and found out I transmitted one extra byte...
        message = mido.Message('sysex')
        for byte in self.msg_bytes:
            message.data += self.nib(byte)
        msg.data += message.data[1:]
        self.logger.debug(len(message.data))
        self.logger.debug(msg.data)
        self.logger.debug(len(msg.data))
        self.outport.send(msg)

    def udq(self):
        msg = mido.Message('sysex', data=[0x7e, self.midi_channel, 0x06, 0x01])
        self.outport.send(msg)
        time.sleep(1)

    def parse_progdump(self, message):
        self.msg_bytes = []
        offset = 1
        if len(message) == 152:
            offset = 7 # data starts after byte 9
        for x in range(0,72):
            self.msg_bytes.append(self.denib(message.bytes()[x*2+offset], message.bytes()[x*2+offset+1]))
        return

    def get_program_name(self):
        return "".join(map(chr,self.msg_bytes[56:]))

    def monitor_input(self, message):
        # a single program dump is 152 bytes long (9 bytes header, 142 bytes data, &xF7 is the last byte)
        if message.type == 'sysex' and len(message.bytes()) == 152:
            self.logger.info(f"Received sysex (program dump)")
            self.parse_progdump(message)
        elif message.type == 'sysex' and len(message.bytes()) == 17:
            self.pod_version = "".join([chr(x) for x in message.bytes()[12:16]])
            self.manufacturer_id = "{:02X} {:02X} {:02X}".format(message.bytes()[5], message.bytes()[6], message.bytes()[7])
            self.product_family = "{:02X}{:02X}".format(message.bytes()[9], message.bytes()[8])
            self.product_family_member = "{:02X}{:02X}".format(message.bytes()[11], message.bytes()[10])
            self.logger.info("Received sysex (device info)")
        elif message.type == 'sysex' and len(message.bytes()) == 151:
            # the editbuffer-dump is one byte shorter than a regular program dump
            dummymsg = mido.Message('sysex', data = [ 0 ])
            message.data = dummymsg.data + message.data
            self.parse_progdump(message)
            self.logger.info("Received sysex (edit buffer)")
        elif message.type == 'program_change' and len(message.bytes()) == 2:
            prog = "Edit Buffer" if message.bytes()[1] == 0 else line6.PROGRAMS[message.bytes()[1]-1]
            self.logger.info(f"Received program_change message: {prog}")
        else:
            self.logger.warning(f"Unknown message type {message.type}: {message.bytes()} ({len(message.bytes())}) bytes:")

    def get_info(self):
        # get infos about the device:
        self.udq()
        time.sleep(1)
        print("POD Version: {}".format(self.pod_version))
        print("Manufacturer ID: {}".format(self.manufacturer_id))
        print("Product Family ID: {}".format(self.product_family))
        print("Product Family Member: {}".format(self.product_family_member))

    def dump_raw(self, **kwargs):
        if 'filename' in kwargs:
            # if filename is given, dump to syx file:
            # update: create sysex-message so we don't have to manually add the 
            # first and last byte
            message = []
            for m in self.msg_bytes[:]:
                h,l = self.nib(m)
                message.append(h)
                message.append(l)
            msg = mido.Message('sysex', data=message)
            mido.write_syx_file(kwargs['filename'], (msg,))
        else:    
            print(*self.msg_bytes)

    def dump_hex(self):
        # print values as hex
        hexbytes = []
        for b in self.msg_bytes[:]:
            hexbytes.append("{:02X}".format(b))
        print(*hexbytes)

    def load_syx(self, filename):
        messages = mido.read_syx_file(filename)
        message = mido.Message('sysex', data=messages[0].data)
        self.parse_progdump(message)

    def change_name(self, new_name):
        """changes the name string of a patch"""
        if len(new_name) > 16:
            # the maximum length is 16 characters
            new_name = new_name[:16]
        if len(new_name) < 16:
            # fill it up with spaces:
            new_name = new_name + (" "*(16-len(new_name)))
        # create a list of ascii-values
        self.logger.info(f"Changing Program name to {new_name}")
        self.msg_bytes[56:] = list(map(ord,new_name))

    def send_cc(self, control, value):
        msg = mido.Message('control_change')
        msg.control = control
        msg.value = value
        self.outport.send(msg)
    
    def get_midioutputs(self):
        # helper function for the gui app
        return mido.get_output_names()

    def get_midiinputs(self):
        # helper function for the gui app
        return mido.get_input_names()
    # }}}

    # {{{ dump human readable
    def dump(self, prog_name):
        # TODO: Format the output so it can be used as a simple menu
        # (enter a number to change certain parameters, save, load,...)
        p_name = self.get_program_name()
        print(f"Program: {prog_name}")
        print(f"Program name: {p_name}")
        if self.msg_bytes[1] > 63:
            print("Distorton ON")
        if self.msg_bytes[2] > 63:
            print("Drive ENABLED")
        if self.msg_bytes[3] > 63:
            print("Presence ENABLED")
        if self.msg_bytes[4] > 63:
            print("Delay ENABLED")
        if self.msg_bytes[5] > 63:
            print("Tremolo/Chorus Flange ENABLED")
        if self.msg_bytes[6] > 63:
            print("Reverb ENABLED")
        if self.msg_bytes[7] > 63:
            print("Noise Gate ENABLED")
        if self.msg_bytes[8] > 63:
            print("Bright Switch ON")
        print("Amp Type: {}".format(line6.amp_names[self.msg_bytes[9]]))
        print("Cab Type: {}".format(line6.cab_names[self.msg_bytes[45]]))
        print("AIR: {}".format(self.msg_bytes[46]))
        print("Drive: {}".format(self.msg_bytes[10]))
        print("Drive 2: {}".format(self.msg_bytes[11]))
        print("Bass: {}".format(self.msg_bytes[12]))
        print("Mid: {}".format(self.msg_bytes[13]))
        print("Treble: {}".format(self.msg_bytes[14]))
        print("Presence: {}".format(self.msg_bytes[15]))
        print("Channel Volume: {}".format(self.msg_bytes[16]))
        print("Noise Gate Threshhold: {}".format(self.msg_bytes[17]))
        print("Noise Gate Decay Time: {}".format(self.msg_bytes[18]))
        #19-25: Wah and Volume Pedal - since I don't have either, I will keep this out for now
        # FIXME: Since I added Wah info to the CC-Commands I will also add it here
        d_type = "Mono"
        if self.msg_bytes[26]>63:
            d_type = "Stereo"
        print("Delay Type: {}".format(d_type))
        # bytes 27-34: Delay L/R time (17 bits each) ???
        # POD 2.0 says something about double precision of the delay time
        # for CC 62, we have to experiment with that so see what it means
        # or just fire up jsynthlib and see what it does ;)
        print("      L Feedback: {}".format(self.msg_bytes[35]))
        print("      L Level: {}".format(self.msg_bytes[37]))
        if d_type == "Stereo":
            print("      R Level: {}".format(self.msg_bytes[38]))
            print("      R Feedback: {}".format(self.msg_bytes[36]))
        r_type = "Hall"
        if self.msg_bytes[39]> 63:
            r_type = "Spring"
        print("Reverb Type: {}".format(r_type))
        print("Reverb Decay: {}".format(self.msg_bytes[40]))
        print("Reverb Tone: {}".format(self.msg_bytes[41]))
        print("Reverb Diffusion: {}".format(self.msg_bytes[42]))
        print("Reverb Density: {}".format(self.msg_bytes[43]))
        print("Reverb Level: {}".format(self.msg_bytes[44]))
        print("FX: {}".format(line6.fx_names[self.msg_bytes[47]]))
        print("FX Tweak: {}".format(self.msg_bytes[48]))
        comp = "OFF"
        if self.msg_bytes[47] == 7 or self.msg_bytes[47] == 11:
            if self.msg_bytes[49] == 1:
                comp = "1.4:1"
            if self.msg_bytes[49] == 2:
                comp = "2:1"
            if self.msg_bytes[49] == 3:
                comp = "3:1"
            if self.msg_bytes[49] == 4:
                comp = "6:1"
            if self.msg_bytes[49] == 5:
                comp = "INF:1"
            print("Compressor Ratio: {}".format(comp))
# }}}

# {{{ __main__
if __name__ == '__main__':
    # argparse:
    parser = argparse.ArgumentParser('pypod.py')
    parser.add_argument('-d', '--dump-program', type=str,
                        help='Dumps given Program (e.g. 2B)',
                        dest='program')
    parser.add_argument('-e', '--dump-editbuffer', action='store_true',
                        help='Dumps the edit buffer', dest='dumpedit')
    parser.add_argument('-x', '--hex', action='store_true',
                        help='display values in hex instead of decimal')
    parser.add_argument('-u', '--human-readable', action='store_true', help='display data in human readable format')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--save', type=str, help='Saves program data to file', dest='tofile')
    group.add_argument('-l', '--load', type=str, help='Loads program data from file', dest='fromfile')
    parser.add_argument('-p', '--put', type=str, help='Uploads program data (from file) to pod', dest='dest_program')
    parser.add_argument('-i', '--info', action='store_true', help='Shows info about the POD 2.0')
    parser.add_argument('-o', '--show-midiports', action='store_true', help='shows available MIDI-ports')
    parser.add_argument('-c', '--channel', type=int, help='Select MIDI-Channel (default: 1)', dest='midichan')
    parser.add_argument('-n', '--name', type=str, help='Renames the Program to NAME', dest='progname')
    parser.add_argument('-m', '--midicc', type=str, help="Send MIDI CC (needs value!)")
    parser.add_argument('-v', '--value', type=str, help="the value to be sent with the CC command")

    args=parser.parse_args()

    pp = pyPOD()
    prog = ""

    if args.show_midiports:
        inports, outports = pp.show_midiports()
        print("\n*** available MIDI Inputs: ***")
        for p in inports:
            print(f"\t{p}")
        print("\n*** available MIDI Outputs: ***")
        for p in outports:
            print(f"\t{p}")

    if args.midichan:
        pp.midi_channel = args.midichan

    if (args.midicc and args.value):
        pp.send_cc(int(args.midicc), int(args.value))

    # parse arguments:
    if args.info == True:
        pp.get_info()

    if args.fromfile:
        pp.load_syx(args.fromfile)
        if args.dest_program:
            if args.progname:
                pp.change_name(args.progname)
            pp.upload_program(args.dest_program)
        if args.human_readable == True:
            pp.dump(args.fromfile)
        elif args.hex == True:
            pp.dump_hex()
        else:
            pp.dump_raw()

    if args.program:
        prog = str(args.program)
        try:
            pp.dump_program(prog)
            time.sleep(1)
        except ValueError:
            pp.logger.error("{} is not a valid POD Program name!".format(prog))
            sys.exit(1)
    elif args.dumpedit:
        pp.dump_editbuffer()
        time.sleep(1)
        prog = "Edit Buffer"
    if prog:
        if args.human_readable == True:
            pp.dump(prog)
        else:
            if args.hex == True:
                pp.dump_hex()
            else:
                if args.tofile:
                    pp.dump_raw(filename=args.tofile)
                else:
                    pp.dump_raw()
# }}}
