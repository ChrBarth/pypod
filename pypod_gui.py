#!/usr/bin/env python3

import gi
import line6
import pypod

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class pyPODGUI:
    pypod = pypod.pyPOD()
    builder = ""

    def __init__(self):
        self.pypod.connect_output('USB Midi Cable:USB Midi Cable MIDI 1 20:0')
        self.pypod.connect_input('USB Midi Cable:USB Midi Cable MIDI 1 20:0')
        self.builder = Gtk.Builder()
        self.builder.add_from_file("pypod_gui.glade")
        handlers = {
            "onDestroy": Gtk.main_quit,
            "onAmpChange": self.change_amp,
            "onCabChange": self.change_cab,
            "onEffectChange": self.change_effect,
            "onEffectTweakChange": self.change_effect_tweak,
            "onChannelVolChange": self.change_channel_vol,
            "onBassChange": self.change_bass,
            "onMidChange": self.change_mid,
            "onTrebleChange": self.change_treble,
            "onNoiseGateToggle": self.toggle_noisegate,
            "onGateThreshChange": self.change_noisegate_thresh,
            "onGateDecayChange": self.change_noisegate_decay,
            "onDistortionToggle": self.toggle_distortion,
            "onDriveChange": self.change_drive,
            "onDriveBoostToggle": self.toggle_driveboost,
            "onPresenceToggle": self.toggle_presence,
            "onPresenceChange": self.change_presence,
            "onBrightToggle": self.toggle_bright,
            "onDelayToggle": self.toggle_delay,
            "onDelayTimeChange": self.change_delaytime,
            "onDelayTime2Change": self.change_delaytime2,
            "onDelayRepeatsChange": self.change_delayrepeats,
            "onDelayLevelChange": self.change_delaylevel,
            "onReverbToggle": self.toggle_reverb,
            "onReverbLevelChange": self.change_reverblevel,
            "onReverbDecayChange": self.change_reverbdecay,
            "onReverbToneChange": self.change_reverbtone,
            "onReverbDiffusionChange": self.change_reverbdiffusion,
            "onReverbDensityChange": self.change_reverbdensity
            }
        self.builder.connect_signals(handlers)
        window = self.builder.get_object("MainWindow")
        # fill ComboBoxes:
        amplist = self.go("ListStoreAmps")
        for item in line6.amp_names:
            amplist.append([line6.amp_names.index(item), item])
        cablist = self.go("ListStoreCabs")
        for item in line6.cab_names:
            cablist.append([line6.cab_names.index(item), item])
        fxlist = self.go("ListStoreEffects")
        for item in line6.fx_names:
            fxlist.append([line6.fx_names.index(item), item])

        window.show_all()

    def go(self, objname):
        return self.builder.get_object(objname)

    def change_amp(self, *args):
        amp_model = self.go("ComboBoxAmpModel").get_active()
        self.pypod.send_cc(12,amp_model)

    def change_cab(self, *args):
        cab_model = self.go("ComboBoxCabModel").get_active()
        self.pypod.send_cc(71, cab_model)

    def change_effect(self, *args):
        effect_type = self.go("ComboBoxEffect").get_active()
        self.pypod.send_cc(19, effect_type)

    def change_effect_tweak(self, *args):
        effect_tweak = int(self.go("ScaleEffectTweak").get_value())
        self.pypod.send_cc(1, effect_tweak)

    def change_channel_vol(self, *args):
        channel_vol = int(self.go("ScaleChannelVol").get_value())
        self.pypod.send_cc(17, channel_vol)

    def change_bass(self, *args):
        bass = int(self.go("ScaleBass").get_value())
        self.pypod.send_cc(14, bass)

    def change_mid(self, *args):
        mid = int(self.go("ScaleMid").get_value())
        self.pypod.send_cc(15, mid)

    def change_treble(self, *args):
        treble = int(self.go("ScaleTreble").get_value())
        self.pypod.send_cc(16, treble)

    def toggle_noisegate(self, *args):
        gate = 127
        gatesw = self.go("SwitchNoiseGate").get_state()
        if gatesw:
            gate = 0
        self.pypod.send_cc(22, gate)

    def change_noisegate_thresh(self, *args):
        threshhold = int(self.go("ScaleGateThresh").get_value())
        self.pypod.send_cc(23, threshhold)

    def change_noisegate_decay(self, *args):
        decay = int(self.go("ScaleGateDecay").get_value())
        self.pypod.send_cc(24, decay)

    def toggle_distortion(self, *args):
        dist = 127
        distsw = self.go("SwitchDistortion").get_state()
        if distsw:
            dist = 0
        self.pypod.send_cc(25, dist)

    def change_drive(self, *args):
        drive = int(self.go("ScaleDrive").get_value())
        self.pypod.send_cc(13, drive)

    def toggle_driveboost(self, *args):
        driveb = 127
        drivebsw = self.go("SwitchDriveBoost").get_state()
        if drivebsw:
            driveb = 0
        self.pypod.send_cc(26, driveb)

    def toggle_presence(self, *args):
        presence = 0
        presencesw = self.go("SwitchPresence").get_state()
        if presencesw:
            presence = 127
        self.pypod.send_cc(27, presence)

    def change_presence(self, *args):
        presence = int(self.go("ScalePresence").get_value())
        self.pypod.send_cc(21, presence)

    def toggle_bright(self, *args):
        bright = 127
        brightsw = self.go("SwitchBright").get_state()
        if brightsw:
            bright = 0
        self.pypod.send_cc(73, bright)

    def toggle_delay(self, *args):
        delay = 127
        delaysw = self.go("SwitchDelay").get_state()
        if delaysw:
            delay =0
        self.pypod.send_cc(28, delay)

    def change_delaytime(self, *args):
        delaytime = int(self.go("ScaleDelayTime").get_value())
        self.pypod.send_cc(30, delaytime)

    def change_delaytime2(self, *args):
        delaytime2 = int(self.go("ScaleDelayTime2").get_value())
        self.pypod.send_cc(62, delaytime2)

    def change_delayrepeats(self, *args):
        delayrepeats = int(self.go("ScaleDelayRepeats").get_value())
        self.pypod.send_cc(32, delayrepeats)

    def change_delaylevel(self, *args):
        delaylevel = int(self.go("ScaleDelayLevel").get_value())
        self.pypod.send_cc(34, delaylevel)

    def toggle_reverb(self, *args):
        rev = 127
        revsw = self.go("SwitchReverb").get_state()
        if revsw:
            rev = 0
        self.pypod.send_cc(36, rev)

    def change_reverblevel(self, *args):
        revlevel = int(self.go("ScaleReverbLevel").get_value())
        self.pypod.send_cc(18, revlevel)

    def change_reverbdecay(self, *args):
        revdecay = int(self.go("ScaleReverbDecay").get_value())
        self.pypod.send_cc(38, revdecay)

    def change_reverbtone(self, *args):
        revtone = int(self.go("ScaleReverbTone").get_value())
        self.pypod.send_cc(39, revtone)

    def change_reverbdiffusion(self, *args):
        revdiff = int(self.go("ScaleReverbDiffusion").get_value())
        self.pypod.send_cc(40, revdiff)

    def change_reverbdensity(self, *args):
        revdens = int(self.go("ScaleReverbDensity").get_value())
        self.pypod.send_cc(41, revdens)

if __name__ == '__main__':
    pyPODGUI()
    Gtk.main()
