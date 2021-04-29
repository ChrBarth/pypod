# PyPOD

A tool to control the Line6 POD 2.0 via MIDI

## USAGE command line:


    usage: pypod.py [-h] [-d PROGRAM] [-x] [-u] [-s TOFILE | -l FROMFILE] [-i] [-c MIDICHAN]
    
    optional arguments:
      -h, --help            show this help message and exit
      -d PROGRAM, --dump-program PROGRAM
                            Dumps given Program (e.g. 2B)
      -x, --hex             display values in hex instead of decimal
      -u, --human-readable  display data in human readable format
      -s TOFILE, --save TOFILE
                            Saves program data to file
      -l FROMFILE, --load FROMFILE
                            Loads program data from file
      -p DEST_PROGRAM, --put DEST_PROGRAM
                            Uploads program data (from file) to pod
      -i, --info            Shows info about the POD 2.0
      -c MIDICHAN, --channel MIDICHAN
                            Select MIDI-Channel (default: 1)
      -n PROGNAME, --name PROGNAME
                            Renames the Program to NAME
      -m MIDICC, --midicc MIDICC
                            Send MIDI CC (needs value!)
      -v VALUE, --value VALUE
                            the value to be sent with the CC command
## GUI:

There is also a GUI (pypod_gui.py) based on Gtk and built with glade that is almost completely functional. At least modifying sounds works (and some stuff that is not possible using only the
buttons on the pod itself like wah, volume pedal, disable/enable reverb, delay, modulation fx...)

## TODO:

* add some more widgets to the gui (save, load, up- and download to/from pod, midi settings, device info)

## REQUIREMENTS:

* mido (```pip3 install mido```)
* rtmidi (```sudo apt install python3-rtmidi```) -> installing via pip3 did not work on ubuntu 20.04 (ModuleNotFoundError)
* python3-gi (```sudo apt install python3-gi```)

## CHANGELOG:

* 2021-04-29: added pypod_gui.py, a GUI wrapper for pypod.py. There are still some widgets to add but it is mostly working.
* 2021-04-28b : moved the whole thing into a class and reorganized the code. Added function to send arbitrary MIDI CC commands to the pod (-m CC -v VALUE, both are needed)
* 2021-04-28: Renaming programs works, uploading a previously saved program dump also works, next step would be to dump a program from pod to pc, modify it, then put it back on the pod
* 2021-03-07: We are now able to save and load settings to a file. The only thing missing is the ability to upload the patch back to the pod
* 2021-03-05: Added the ability to pass commandline arguments. For now we can dump a program in hex, decimal and human readable format and we can also show device info. I still haven't figured out how all the multi-byte values (delay-time, chorus/flanger/rotary speed/depth... work)
* 2021-02-28: Dumping one Program works, the callback function needs some more functionality, maybe a testing sysex to check if the pod is even connected/responding
* 2021-02-26: After playing around with MIDI in general, sysex-Commands and some "reverse-engineering" in [jsynthlib] (http://www.jsynthlib.org/) I am finally able to send stuff to the POD and receive the response. Thanks to [medias.audiofanzine.com] (https://medias.audiofanzine.com/files/lin020-477344.pdf) I now have a pretty good understanding how to talk to a POD 2.0 via MIDI and from now on most of the work will be regular programming stuff.
