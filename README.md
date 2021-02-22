# PyPOD
a tool to control the POD 2.0 via MIDI

At the moment nothing is working, since I am still figuring out, how to talk to my POD 2.0 via USB-MIDI cable:

- py-midi looked promising but it seems it only works with Serial Connections, not USB
- tried pygame but it seems to be focused on playing midi files instead of controlling stuff
- amidi seems not to work (especially if Alsa-Midi is bridged to jack)

## REQUIREMENTS:

