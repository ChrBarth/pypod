# PyPOD

A tool to control the Line6 POD 2.0 via MIDI

## USAGE command line:

    usage: pypod.py [-h] [-d PROGRAM] [-e] [-x] [-u] [-s TOFILE | -l FROMFILE]
                    [-p DEST_PROGRAM] [-i] [-o] [-c MIDICHAN] [-n PROGNAME]
                    [-m MIDICC] [-v VALUE] [-r PROGCHANGE]

    optional arguments:
      -h, --help            show this help message and exit
      -d PROGRAM, --dump-program PROGRAM
                            Dumps given Program (e.g. 2B)
      -e, --dump-editbuffer
                            Dumps the edit buffer
      -x, --hex             display values in hex instead of decimal
      -u, --human-readable  display data in human readable format
      -s TOFILE, --save TOFILE
                            Saves program data to file
      -l FROMFILE, --load FROMFILE
                            Loads program data from file
      -p DEST_PROGRAM, --put DEST_PROGRAM
                            Uploads program data (from file) to pod
      -i, --info            Shows info about the POD 2.0
      -o, --show-midiports  shows available MIDI-ports
      -c MIDICHAN, --channel MIDICHAN
                            Select MIDI-Channel (default: 1)
      -n PROGNAME, --name PROGNAME
                            Renames the Program to NAME
      -m MIDICC, --midicc MIDICC
                            Send MIDI CC (needs value!)
      -v VALUE, --value VALUE
                            the value to be sent with the CC command
      -r PROGCHANGE, --progam-change PROGCHANGE
                            sends program change

We now have support for a config file. The format is json and it can be either stored in the current working or home directory (name is .pypodrc). Here is a sample:

    {
        "MIDI_IN": "USB Midi Cable:USB Midi Cable MIDI 1 24:0",
        "MIDI_OUT": "USB Midi Cable:USB Midi Cable MIDI 1 24:0",
        "MIDI_CHAN": "1"
    }

## GUI:

There is also a GUI (pypod_gui.py) based on Gtk and built with glade that lets you do all
the stuff using a graphical interface.

## DEMOS:

I made two short videos, one for the commandline and one for the GUI, here are the links (YouTube):

* [commandline version](https://youtu.be/CrxVrib7MgY)
* [GUI version](https://youtu.be/lPLfrbN7K4w)

## BUGS:

* when turning to many knobs on the pod the GUI freezes. This is probably still the same bug as before when it would just quit with a segmentation fault. I still have no idea how to fix this, for now it is not recommended to change too many settings in a short time on the pod.

## TODO:

* needs some testing, finding and fixing bugs
* get rid of time.sleep() and call updateGUI from callback function when new data comes in

## REQUIREMENTS:

* mido (```pip3 install mido```)
* rtmidi (```sudo apt install python3-rtmidi```) -> installing via pip3 did not work on ubuntu 20.04 (ModuleNotFoundError)

GUI version:

* python3-gi (```sudo apt install python3-gi```)

This was written and tested on Ubuntu 20.04, it should probably run on other linux distributions as well, no idea if it also works on windows/mac, tell me if it does ;)

## CHANGELOG:

* 2021-05-17: cleaned up some logging messages, added -l / -log-level argument to pypod_gui.py so the loglevel can be changed on startup (is now CRITICAL, so very quiet by default)
* 2021-05-16: Re-organized Amp&FX Settings-Tab, added "About"-dialog
* 2021-05-14: Send MIDI CC and Program Change commands via GUI to the pod, also started to include some css
* 2021-05-03: The first version I consider somewhat fully functional, especially in the GUI-section. Now I will need to do some extensive testing to find and remove bugs. One bug I already stumbled over is a segmentation fault when changing a lot of settings on the pod directly (this gets now live-updated in the GUI!).
* 2021-05-01: added logging and support for a simple json-configfile. Also added an option to show the available MIDI-ports for easy config-creation.
* 2021-04-29: added pypod_gui.py, a GUI wrapper for pypod.py. There are still some widgets to add but it is mostly working.
* 2021-04-28b : moved the whole thing into a class and reorganized the code. Added function to send arbitrary MIDI CC commands to the pod (-m CC -v VALUE, both are needed)
* 2021-04-28: Renaming programs works, uploading a previously saved program dump also works, next step would be to dump a program from pod to pc, modify it, then put it back on the pod
* 2021-03-07: We are now able to save and load settings to a file. The only thing missing is the ability to upload the patch back to the pod
* 2021-03-05: Added the ability to pass commandline arguments. For now we can dump a program in hex, decimal and human readable format and we can also show device info. I still haven't figured out how all the multi-byte values (delay-time, chorus/flanger/rotary speed/depth... work)
* 2021-02-28: Dumping one Program works, the callback function needs some more functionality, maybe a testing sysex to check if the pod is even connected/responding
* 2021-02-26: After playing around with MIDI in general, sysex-Commands and some "reverse-engineering" in [jsynthlib] (http://www.jsynthlib.org/) I am finally able to send stuff to the POD and receive the response. Thanks to [medias.audiofanzine.com] (https://medias.audiofanzine.com/files/lin020-477344.pdf) I now have a pretty good understanding how to talk to a POD 2.0 via MIDI and from now on most of the work will be regular programming stuff.
