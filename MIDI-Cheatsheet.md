# MIDI Cheatsheet

## The Structure Of A Midi Event:

stolen from:
[Midi Programming - A Complete Study Part 1] (http://www.petesqbsite.com/sections/express/issue18/midifilespart1.html)

Name        | Length and Range| Description
------------|-----------------|------------------------------
StatusByte  | [0-F]           | Type of Midi message
ChannelByte | [0-F]           | MIDI Channel Number
DataByte1   | [0-FF]          | First midi message data byte
DataByte2   | [0-FF]          | Second midi message data byte

The status and channel Bytes are merged into one byte (00-FF) Because these messages have an MSB (Most Significant Byte) of 1 the command statuses actually begin at 80 hexadecimal (128 and up to 255) The LSB (Least Significant Byte takes a value of 0-F Hexadecimal (0 to 15) to specify which MIDI channel the command will be sent to. A command message tells the MIDI gear to perform certain types of things like play a note, change the volume, add effects, and other types of things. This table shows the different command status and what they do.

Status | Expected Data     | Comments
-------|-------------------|------------------------------------------
8x     | note, velocity    | Note off
9x     | note, velocity    | Note on (velocity 0 = note off)
Ax     | note, value       | Polyphonic pressure
Bx     | controller, value | Controller change
Cx     | program           | Program change
Dx     | value             | Channel pressure
Ex     | value (two bytes: LSB then MSB. many devices will accept only one byte which will be interpreted as the MSB.) | Pitch bend

Midi Notes:

Octave | C  | C# | D  | D# | E  | F  | F# | G  | G# | A  | A# | B
-------|----|----|----|----|----|----|----|----|----|----|----|----
0      |  0 |  1 |  2 |  3 |  4 |  5 |  6 |  7 |  8 |  9 | 10 | 11
1      | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23
...

### SysEx Commands:

    F0 XX nn nn ... F7

F0 -> Start SysEx
XX -> Manufacturer ID ( 00 01 0C for Line 6) see [here] (https://www.midi.org/specifications-old/item/manufacturer-id-numbers)
nn -> one or more commands
F7 -> End of SysEx

#### Device identification:

stolen from:
[medias.audiofanzine.com] (https://medias.audiofanzine.com/files/lin020-477344.pdf)

    $ amidi -p hw:2,0,0 -S 'F0 7E 7F 06 01 F7' -d -t 1
    F0 7E 7F 06 02 00 01 0C 00 00 00 03 30 32 35 34 F7
    17 bytes read

Request:
- F0 -> Start SysEX
- 7E 7F 06 01 -> Universal Device Inquiry (7F -> all channels)
- F7 -> End of SysEx

Response:

- F0 7E 7F 06 02 -> Universal Device Reply
- 00 01 0C -> Line 6 (Manufaturer)
- 00 00 -> POD Product Family ID
- 00 03 -> POD Product Family Member (LSB first)
- 30 32 35 34 -> Software Revision (ASCII) = 0 2 5 4 = 2.54
- F7 -> EOX

### Example Controller Change on Channel 1:

0x01 | 0xB0 => 0xB1
(first byte of MIDI CC is status and channel byte combined)

Change Amp1 Channel on Line 6 POD 2.0:

0xB1 0xC 0xF

-> 0xB1 (Control Change, Channel 1)
-> 0xC (12 -> Change Amp)
-> 0xF (15 -> Fuzz Box)

    $ amidi -l
    Dir Device    Name
    IO  hw:0,0    M Audio Audiophile 24/96 MIDI
    IO  hw:2,0,0  USB Midi Cable MIDI 1
    $ amidi -p hw:2,0,0 -S 'B1 0C 0D'

-> POD 2.0 changes to Fuzz Box!

### MIDI-Dump jsynthlib POD 2.0 get Patch 1A:

XMIT: SysEX:length=9
  f0 00 01 0c 01 00 00 00 f7
RECV: SysEX:length=152
  f0 00 01 0c 01 01 00 00 00 00 01 00 01 00 01 00
00 00 00 00 01 00 00 00 01 00 07 03 00 00 0c 02
0c 02 01 02 07 00 00 01 07 00 0e 00 0d 00 00 02
01 07 09 07 0f 07 0f 00 00 00 00 00 00 00 00 00
00 03 00 0c 00 00 00 00 00 03 00 0c 00 02 0d 00
00 02 00 00 0f 00 00 01 0b 02 00 02 00 02 00 00
0b 00 0d 02 00 00 0a 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 04 02 06 09 06 07 02 00 04
0c 06 05 06 01 06 04 02 00 05 04 06 0f 06 0e 06
05 02 00 02 00 02 00 f7

get 1B:
f0 00 01 0c 01 00 00 01 f7

Works as well with amidi:

    $ amidi -p hw:2,0,0 -S 'f0 00 01 0c 01 00 00 00 f7' -d -t 2

### MIDI-Dump jsynthlib POD 2.0 upload Patch 1A:

XMIT: SysEX:length=152
  f0 00 01 0c 01 01 00 00 00 00 00 00 00 00 00 00
00 00 00 00 01 00 00 00 01 00 00 01 00 00 0e 02
00 02 00 02 00 02 00 02 00 02 04 00 0e 07 0f 00
00 07 0f 07 0e 07 0f 00 00 00 00 00 00 00 00 00
00 03 00 0c 00 00 00 00 00 03 00 0c 00 02 00 02
0d 02 00 02 00 00 00 02 00 02 00 02 00 02 00 02
00 00 00 03 0f 00 0a 01 0f 00 02 0d 0a 00 01 03
09 04 00 00 00 00 01 05 04 06 05 07 03 07 04 02
00 02 00 02 00 02 00 02 00 02 00 02 00 02 00 02
00 02 00 02 00 02 00 f7

### MIDI-Dump jsynthlib POD 2.0 upload Patch 1B:

XMIT: SysEX:length=152
  f0 00 01 0c 01 01 00 01 00 00 00 00 00 00 00 00
00 00 00 00 01 00 00 00 01 00 00 01 00 00 0e 02
00 02 00 02 00 02 00 02 00 02 04 00 0e 07 0f 00
00 07 0f 07 0e 07 0f 00 00 00 00 00 00 00 00 00
00 03 00 0c 00 00 00 00 00 03 00 0c 00 02 00 02
0d 02 00 02 00 00 00 02 00 02 00 02 00 02 00 02
00 00 00 03 0f 00 0a 01 0f 00 02 0d 0a 00 01 03
09 04 00 00 00 00 01 05 04 06 05 07 03 07 04 02
00 02 00 02 00 02 00 02 00 02 00 02 00 02 00 02
00 02 00 02 00 02 00 f7

### Switch To Patch 1C:

    $ amidi -p hw:2,0,0 -S 'f0 00 01 0c 00 00 c0 03 f7'

### Switch To Patch 1B:

    $ amidi -p hw:2,0,0 -S 'f0 00 01 0c 00 00 c0 02 f7'

## python-pygame:

[documentation] (https://www.pygame.org/docs/ref/midi.html)

    import pygame.midi
    pygame.midi.get_device_info(5)

Output: (b'ALSA', b'USB Midi Cable MIDI 1', 1, 0, 0)

    pygame.midi.get_device_info(4)

Output: (b'ALSA', b'USB Midi Cable MIDI 1', 0, 1, 0)

    pygame.midi.Output.write_sys_ex(pygame.midi.Output(4), pygame.midi.time(), [0xF0, 0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7])

sends the sysex command (led blinks) but I haven't found out how to capture the data the pod sends back...
Maybe I need to set up a "game-loop" and poll/read from the device constantly until something gets sent back.
Will probably try [mido] (https://www.pygame.org/docs/ref/midi.html) tomorrow... ;)
