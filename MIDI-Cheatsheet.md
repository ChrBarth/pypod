# MIDI Cheatsheet

## The Structure Of A Midi Event:

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

### Controller Change on Channel 1:

0x01 | 0xB0 => 0xB1

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
