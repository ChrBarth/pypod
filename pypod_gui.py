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
            "onReverbDensityChange": self.change_reverbdensity,
            "onWahToggle": self.toggle_wah,
            "onWahPositionChange": self.change_wahposition,
            "onWahBottomChange": self.change_wahbottom,
            "onWahTopChange": self.change_wahtop,
            "onVolumePedalChange": self.change_volumepedal,
            "onVolumePedalMinChange": self.change_volumepedalmin,
            "onVolumeSwellToggle": self.toggle_volumeswell,
            "onVolumeSwellRampChange": self.change_volumeswellramp,
            "onCompressionRatioChange": self.change_compressionvalue,
            "onReverbTypeChange": self.change_reverbtype,
            "onVolumePosChange": self.change_volumepos,
            "onAIRAmbienceChange": self.change_airambience,
            "onModSpeedChange": self.change_modspeed,
            "onModDepthChange": self.change_moddepth,
            "onFeedbackChange": self.change_feedback,
            "onChorusPreDelayChange": self.change_choruspredelay,
            "onRotarySpeedChange": self.change_rotaryspeed,
            "onRotaryMaxSpeedChange": self.change_rotarymaxspeed,
            "onRotaryMinSpeedChange": self.change_rotaryminspeed,
            "onTremoloSpeedChange": self.change_tremolospeed,
            "onTremoloDepthChange": self.change_tremolodepth,
            "onButtonTapClicked": self.send_tap,
            "onModulationToggle": self.toggle_modulation,
            "onMidiChannelChange": self.change_midichannel
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
        complist = self.go("ListStoreCompressionRatio")
        for item in line6.compression_values:
            complist.append(item)
        revlist = self.go("ListStoreReverbType")
        for item in line6.reverb_types:
            revlist.append(item)
        volumelist = self.go("ListStoreVolumePos")
        for item in line6.volume_pos:
            volumelist.append(item)
        midichanlist = self.go("ListStoreMIDIChannel")
        midichanlist.append(["ALL"])
        for chan in range(1, 17):
            midichanlist.append(["CH" + str(chan)])

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

    def toggle_wah(self, *args):
        wah = 127
        wahsw = self.go("SwitchWah").get_state()
        if wahsw:
            wah = 0
        self.pypod.send_cc(43, wah)

    def change_wahposition(self, *args):
        wahpos = int(self.go("ScaleWahPosition").get_value())
        self.pypod.send_cc(4, wahpos)

    def change_wahbottom(self, *args):
        wahbottom = int(self.go("ScaleWahBottom").get_value())
        self.pypod.send_cc(44, wahbottom)

    def change_wahtop(self, *args):
        wahtop = int(self.go("ScaleWahTop").get_value())
        self.pypod.send_cc(45, wahtop)

    def change_volumepedal(self, *args):
        volped = int(self.go("ScaleVolumePedal").get_value())
        self.pypod.send_cc(7, volped)

    def change_volumepedalmin(self, *args):
        volpedalmin = int(self.go("ScaleVolumePedalMin").get_value())
        self.pypod.send_cc(46, volpedalmin)

    def toggle_volumeswell(self, *args):
        swell = 127
        swellsw = self.go("SwitchVolumeSwell").get_state()
        if swellsw:
            swell = 0
        self.pypod.send_cc(48, swell)

    def change_volumeswellramp(self, *args):
        swellramp = int(self.go("ScaleVolumeSwellRamp").get_value())
        self.pypod.send_cc(49, swellramp)

    def change_compressionvalue(self, *args):
        index = int(self.go("ComboBoxCompressionRatio").get_active())
        # the ListStore CompressionRatio has two colums:
        # the first (index 0) is the midi-value to be sent,
        # the second (index 1) is the text displayed in the combobox
        # with get_active() we only get the index, not the actual value
        # from the first column. To get this value we have to use the model
        # https://gnipsel.com/glade/glade06b.html
        model = self.go("ComboBoxCompressionRatio").get_model()
        compval = model[index][0]
        liststore = self.go("ListStoreCompressionRatio")
        self.pypod.send_cc(42, compval)

    def change_reverbtype(self, *args):
        index = int(self.go("ComboBoxReverbType").get_active())
        model = self.go("ComboBoxReverbType").get_model()
        reverbval = model[index][0]
        self.pypod.send_cc(37, reverbval)

    def change_volumepos(self, *args):
        index = int(self.go("ComboBoxVolumePos").get_active())
        model = self.go("ComboBoxVolumePos").get_model()
        volposval = model[index][0]
        self.pypod.send_cc(47, volposval)

    def change_airambience(self, *args):
        amb = int(self.go("ScaleAIRAmbience").get_value())
        self.pypod.send_cc(72, amb)

    def change_modspeed(self, *args):
        modspeed = int(self.go("ScaleModSpeed").get_value())
        self.pypod.send_cc(51, modspeed)

    def change_moddepth(self, *args):
        moddepth = int(self.go("ScaleModDepth").get_value())
        self.pypod.send_cc(52, moddepth)

    def change_feedback(self, *args):
        feedback = int(self.go("ScaleFeedback").get_value())
        self.pypod.send_cc(53, feedback)

    def change_choruspredelay(self, *args):
        predelay = int(self.go("ScaleChorusPreDelay").get_value())
        self.pypod.send_cc(54, predelay)

    def change_rotaryspeed(self, *args):
        rotaryspeed = int(self.go("ScaleRotarySpeed").get_value())
        self.pypod.send_cc(55, rotaryspeed)

    def change_rotarymaxspeed(self, *args):
        rotarymaxspeed = int(self.go("ScaleRotaryMaxSpeed").get_value())
        self.pypod.send_cc(56, rotarymaxspeed)

    def change_rotaryminspeed(self, *args):
        rotaryminspeed = int(self.go("ScaleRotaryMinSpeed").get_value())
        self.pypod.send_cc(57, rotaryminspeed)
    
    def change_tremolospeed(self, *args):
        tremolospeed = int(self.go("ScaleTremoloSpeed").get_value())
        self.pypod.send_cc(58, tremolospeed)

    def change_tremolodepth(self, *args):
        tremolodepth = int(self.go("ScaleTremoloDepth").get_value())
        self.pypod.send_cc(59, tremolodepth)

    def send_tap(self, *args):
        self.pypod.send_cc(64,127)

    def toggle_modulation(self, *args):
        mod = 127
        modsw = self.go("SwitchModulation").get_state()
        if modsw:
            mod = 0
        self.pypod.send_cc(50, mod)

    def change_midichannel(self, *args):
        midichan = int(self.go("ComboBoxMIDIChannel").get_active())
        self.pypod.midi_channel = midichan

if __name__ == '__main__':
    pyPODGUI()
    Gtk.main()
