# PyPOD

a tool to control the Line6 POD 2.0 via MIDI

Goal is to be able to dump Programs from the POD to PC, tweak some settings and put the modified sounds back on the POD. Also saving presets to disk would be nice.

## USAGE:


    usage: pypod.py [-h] [-d PROGRAM] [-x] [-u] [-s TOFILE | -l FROMFILE] [-i] [-c MIDICHAN]
    
    optional arguments:
      -h, --help            show this help message and exit
      -d PROGRAM, --dump-program PROGRAM
                            Dumps given Program (e.g. 2B)
      -x, --hex             display values in hex instead of decimal
      -u, --human-readable  display data in human readable format
      -s TOFILE, --save TOFILE
                            Saves Settings to file
      -l FROMFILE, --load FROMFILE
                            Loads Settings from file
      -i, --info            Shows info about the POD 2.0
      -c MIDICHAN, --channel MIDICHAN
                            Select MIDI-Channel (default: 1)
## TODO:

* Put Settings back on the POD
* GUI (not decided yet, maybe only curses but with that much settings GTK/QT/??? is probably a better option)

## REQUIREMENTS:

* mido (```pip3 install mido```)
* rtmidi (```sudo apt install python3-rtmidi```) -> installing via pip3 did not work on ubuntu 20.04 (ModuleNotFoundError)

## CHANGELOG:

* 2021-03-07: We are now able to save and load settings to a file. The only thing missing is the ability to upload the patch back to the pod
* 2021-03-05: Added the ability to pass commandline arguments. For now we can dump a program in hex, decimal and human readable format and we can also show device info. I still haven't figured out how all the multi-byte values (delay-time, chorus/flanger/rotary speed/depth... work)
* 2021-02-28: Dumping one Program works, the callback function needs some more functionality, maybe a testing sysex to check if the pod is even connected/responding
* 2021-02-26: After playing around with MIDI in general, sysex-Commands and some "reverse-engineering" in [jsynthlib] (http://www.jsynthlib.org/) I am finally able to send stuff to the POD and receive the response. Thanks to [medias.audiofanzine.com] (https://medias.audiofanzine.com/files/lin020-477344.pdf) I now have a pretty good understanding how to talk to a POD 2.0 via MIDI and from now on most of the work will be regular programming stuff.
