#!/usr/bin/env python3

# Some useful POD-Variables

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

cc_commands = {
    "AmpModel": 12,             # 0-32 (0=Tube Preamp,...)
    "Drive": 13,                # 0-127
    "Bass": 14,                 # 0-127
    "Mid": 15,                  # 0-127
    "Treble": 16,               # 0-127
    "BrightSwitch": 73,         # 0-63: OFF, 64-127: ON
    "Channel Vol": 17,          # 0-127
    "Presence": 21,             # 0-127
    "Noise Gate": 22,           # 0-63: OFF, 64-127: ON
    "GateThreshhold": 23,       # 0-127
    "GateDecay": 24,            # 0-127
    "Effect": 19,               # 0-15 (0=Bypass,...)
    "EffectTweak": 1,           # 0-127
    "Distortion": 25,           # 0-63: OFF, 64-127: ON
    "DriveBoost": 26,           # 0-63: OFF, 64-127: ON
    "Presence": 27,             # 0-63: OFF, 64-127: ON
    "Delay": 28,                # 0-63: OFF, 64-127: ON
    "DelayTime": 30,            # 0-127 = 0-3150ms
    "DelayTime2": 62,           # 0-127 (Extra precision (???))
    "DelayRepeats": 32,         # 0-127
    "DelayLevel": 34,           # 0-127
    "Reverb": 36,               # 0-63: OFF; 64-127: ON
    "ReverbType": 37,           # 0-63: SPRING, 64-127: HALL
    "ReverbDecay": 38,          # 0-127
    "ReverbTone": 39,           # 0-127
    "ReverbDiffusion": 40,      # 0-127
    "ReverbDensity": 41,        # 0-127
    "ReverbLevel": 18,          # 0-127
    "CompressionRatio": 42,     # 0-21=OFF, 22-44=1.4:1, 45-67=2:1, 68-90=3:1, 91-113=6:1, 114-127=INF
    "Wah": 43,                  # 0-63: OFF, 64-127: ON
    "WahPedal": 4,              # 0-127 (Pedal Position)
    "WahBottom": 44,            # 0-127 (Bottom frequency)
    "WahTop": 45,               # 0-127 (Top frequency)
    "Volume": 7,                # 0-127 (Volume Pedal)
    "VolumeMin": 46,            # 0-127 ???
    "VolumePrePost": 47,        # 0-63: PRE TUBE, 64-127: POST TUBE
    "VolSwell": 48,             # 0-63: OFF, 64-127: ON
    "VolSwellRamp": 49,         # 0-127
    "TapTempo": 64,             # 64-127 = A TAP (=sending 2 in a second sets to 120bpm?)
    "ModulationOnOff": 50,      # 0-63: OFF, 64-127: ON (Chorus/Rotary/Tremolo)
    "Speed": 51,                # 0-127 (Chorus/Flanger)
    "Depth": 52,                # 0-127 (Chorus/Flanger)
    "Feedback": 53,             # 0-63: NEGATIVE: 64-127: POSITIVE
    "ChorusPreDelay": 54,       # 0-127
    "RotarySpeed": 55,          # 0-127
    "RotaryMaxSpeed": 56,       # 0-127
    "RotaryMinSpeed": 57,       # 0-127
    "TremoloSpeed": 58,         # 0-127
    "TremoloDepth": 59,         # 0-127
    "CabinetType": 71,          # 0-15 (0=No Cab, ...)
    "AIRAmbienceLevel": 72      # 0-127
    }

compression_values = [ [ 0, "Off" ],
    [ 22, "1.4:1" ],
    [ 45, "2:1"   ],
    [ 68, "3:1"   ],
    [ 91, "6:1"   ],
    [ 114, "INF"  ] ]

