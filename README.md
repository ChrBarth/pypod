# PyPOD

a tool to control the Line6 POD 2.0 via MIDI

Goal is to be able to dump Programs from the POD to PC, tweak some settings and put the modified sounds back on the POD. Also saving presets to disk would be nice.

## TODO:

* Dump Single Program/Bank/Everything (somewhat working, but only via amidi)
* Put Settings back on the POD
* Save Programs to disk (maybe just as .syx-file since mido already supports that)
* GUI (not decided yet, maybe only curses but with that much settings GTK/QT/??? is probably a better option)

## REQUIREMENTS:

* mido (```pip3 install mido```)
* rtmidi (```sudo apt install python3-rtmidi```) -> installing via pip3 did not work on ubuntu 20.04 (ModuleNotFoundError)

## CHANGELOG:

* 2021-02-26: After playing around with MIDI in general, sysex-Commands and some "reverse-engineering" in [jsynthlib] (http://www.jsynthlib.org/) I am finally able to send stuff to the POD and receive the response. Thanks to [medias.audiofanzine.com] (https://medias.audiofanzine.com/files/lin020-477344.pdf) I now have a pretty good understanding how to talk to a POD 2.0 via MIDI and from now on most of the work will be regular programming stuff.
