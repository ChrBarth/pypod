#!/usr/bin/env python3

import gi
import line6
import pypod
import time

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class pyPODGUI:
    pypod = pypod.pyPOD()
    builder = ""
    midi_inputs = []
    midi_outputs = []

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("pypod_gui.glade")
        # {{{ handlers:
        handlers = {
            "onDestroy": Gtk.main_quit,
            "onMenuSaveAs": self.save_file,
            "onMenuOpen": self.open_file,
            "onMenuQuit": Gtk.main_quit,
            "onMenuDownload": self.download_program,
            "onMenuUpload": self.upload_program,
            "onMenuDownloadEditBuffer": self.download_editbuffer,
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
            "onMidiChannelChange": self.change_midichannel,
            "onMidiInputChange": self.change_midiinput,
            "onMidiOutputChange": self.change_midioutput
            }
        # }}}
        self.builder.connect_signals(handlers)
        window = self.builder.get_object("MainWindow")
        # {{{ fill ComboBoxes:
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
        
        self.midi_outputs = self.pypod.get_midioutputs()
        midi_outputlist = self.go("ListStoreMIDIOutput")
        for output in self.midi_outputs:
            midi_outputlist.append([output])

        self.midi_inputs = self.pypod.get_midiinputs()
        midi_inputlist = self.go("ListStoreMIDIInput")
        for input in self.midi_inputs:
            midi_inputlist.append([input])

        programlist = self.go("ListStoreProgram")
        for program in line6.PROGRAMS:
            programlist.append([program])

        # }}}
        window.show_all()

    # {{{ signal handling functions:
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

    def change_midiinput(self, *args):
        index = self.go("ComboBoxMIDIInput").get_active()
        model = self.go("ComboBoxMIDIInput").get_model()
        midiin = model[index][0]
        self.pypod.connect_input(midiin)

    def change_midioutput(self, *args):
        index = self.go("ComboBoxMIDIOutput").get_active()
        model = self.go("ComboBoxMIDIOutput").get_model()
        midiout = model[index][0]
        self.pypod.connect_output(midiout)
    
    def get_combobox_program(self, *args):
        index = self.go("ComboBoxProgram").get_active()
        model = self.go("ComboBoxProgram").get_model()
        program = model[index][0]
        return program

    def download_editbuffer(self, *args):
        self.pypod.dump_editbuffer()
        time.sleep(1)
        if len(self.pypod.msg_bytes) < 72:
            self.pypod.logger.error("ERROR: No data received!")
        else:
            self.updateGUI()

    def download_program(self, *args):
        # display a dialog to specify what to download:
        program = self.get_combobox_program()
        self.pypod.dump_program(program)
        time.sleep(1)
        if len(self.pypod.msg_bytes) < 72:
            self.pypod.logger.error("ERROR: No data received!")
        else:
            self.updateGUI()

    def upload_program(self, *args):
        # first, download the edit buffer:
        self.pypod.dump_editbuffer()
        time.sleep(1)
        program = self.get_combobox_program()
        self.update_programname()
        self.pypod.upload_program(program)

    def update_programname(self, *args):
        self.pypod.change_name(self.go("EntryPatchName").get_text())

    # }}}

    # {{{ file functions
    def save_file(self, *args):
        """ This function saves the current edit buffer
            to file. It does NOT save anything if the
            pod is not connected via MIDI !!! """
        dialog = Gtk.FileChooserDialog(title="select a file", parent=self.go("MainWindow"), action=Gtk.FileChooserAction.SAVE)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,
            Gtk.ResponseType.OK,
            )
        #self.add_filters
        dialog.set_do_overwrite_confirmation(True)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.pypod.dump_editbuffer()
            time.sleep(1)
            if len(self.pypod.msg_bytes) < 72:
                self.pypod.logger.error("ERROR: no data received!")
            else:
                self.update_programname()
                self.pypod.dump_raw(filename=dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            pass
            #print("Cancel!")

        dialog.destroy()

    def open_file(self, *args):
        dialog = Gtk.FileChooserDialog(title="select a file", parent=self.go("MainWindow"), action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
            )
        #self.add_filters
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.pypod.load_syx(dialog.get_filename())
            self.updateGUI()
        elif response == Gtk.ResponseType.CANCEL:
            pass
            #print("Cancel!")

        dialog.destroy()
    # }}}

    # {{{ updateGUI
    def updateGUI(self):
        """ this function updates all the widgets in the GUI after a
            program was fetched from the pod or loaded from disk
            Some values are not stored in the sysex-dumps:
            volume swell on/off """
        msg = self.pypod.msg_bytes
        self.go("ComboBoxAmpModel").set_active(msg[9])
        self.go("ComboBoxCabModel").set_active(msg[45])
        self.go("ComboBoxEffect").set_active(msg[47])
        self.go("ComboBoxCompressionRatio").set_active(msg[49])
        self.go("ComboBoxReverbType").set_active(msg[39])
        self.go("ComboBoxVolumePos").set_active(msg[25])
        gate = True if msg[7] == 1 else False
        self.go("SwitchNoiseGate").set_state(gate)
        dist = True if msg[1] == 1 else False
        self.go("SwitchDistortion").set_state(dist)
        boost = True if msg[2] == 1 else False
        self.go("SwitchDriveBoost").set_state(boost)
        presence = True if msg[3] == 1 else False
        self.go("SwitchPresence").set_state(presence)
        bright = True if msg[8] == 1 else False
        self.go("SwitchBright").set_state(bright)
        mod = True if msg[5] == 1 else False
        self.go("SwitchModulation").set_state(mod)
        delay = True if msg[4] == 1 else False
        self.go("SwitchDelay").set_state(delay)
        reverb = True if msg[6] == 1 else False
        self.go("SwitchReverb").set_state(reverb)
        self.go("ScaleChannelVol").set_value(msg[16]*2)
        self.go("ScaleBass").set_value(msg[12]*2)
        self.go("ScaleMid").set_value(msg[13]*2)
        self.go("ScaleTreble").set_value(msg[14]*2)
        self.go("ScaleGateThresh").set_value(msg[17]*2)
        self.go("ScaleGateDecay").set_value(msg[18]*2)
        self.go("ScaleAIRAmbience").set_value(msg[46]*2)
        self.go("ScaleEffectTweak").set_value(msg[48]*2)
        self.go("ScaleDrive").set_value(msg[10]*2)
        self.go("ScalePresence").set_value(msg[15]*2)
        # from here on it gets a little bit fishy since different effects
        # share the same bytes (mostly 49-53) and to make things worse,
        # they sometimes only use certain bits!
        # the only difference is they have their own CC commands (some at least...)
        self.go("ScaleModSpeed").set_value(msg[49]) # TODO: msg[50] holds 4 more bits!
        self.go("ScaleModDepth").set_value(msg[51]) # TODO: msg[52] holds 1 more bit!
        self.go("ScaleFeedback").set_value(msg[53]*2)
        self.go("ScaleChorusPreDelay").set_value(msg[54]) # TODO: msg[55] holds 1 more bit!
        rotfast = 127 if msg[49] == 1 else 0 # this should be just a Switch, no slider
        self.go("ScaleRotarySpeed").set_value(rotfast)
        self.go("ScaleRotaryMaxSpeed").set_value(msg[50]) # TODO: msg[51] holds 3 more bits!
        self.go("ScaleRotaryMinSpeed").set_value(msg[52]) # TODO: msg[53] holds 3 more bits!
        self.go("ScaleTremoloSpeed").set_value(msg[49]) # TODO: msg[50] holds 3 more bits!
        self.go("ScaleTremoloDepth").set_value(msg[51])
        # TODO: Right now we ignore that the delay has stereo capabilities!!!
        self.go("ScaleDelayTime").set_value(msg[29] & 127) # this should be 27?
        self.go("ScaleDelayTime2").set_value(msg[30] & 127) # this should be 28?
        self.go("ScaleDelayRepeats").set_value(msg[35]*2)
        self.go("ScaleDelayLevel").set_value(msg[37]*2)
        self.go("ScaleReverbLevel").set_value(msg[44]*2)
        self.go("ScaleReverbDecay").set_value(msg[40]*2)
        self.go("ScaleReverbTone").set_value(msg[41]*2)
        self.go("ScaleReverbDiffusion").set_value(msg[42]*2)
        self.go("ScaleReverbDensity").set_value(msg[43]*2)
        self.go("ScaleWahPosition").set_value(msg[19])
        self.go("ScaleWahBottom").set_value(msg[20])
        self.go("ScaleWahTop").set_value(msg[21])
        self.go("ScaleVolumePedal").set_value(msg[23])
        self.go("ScaleVolumePedalMin").set_value(msg[24])
        self.go("ScaleVolumeSwellRamp").set_value(msg[49]*2)
        self.go("EntryPatchName").set_text(self.pypod.get_program_name())
    # }}}

if __name__ == '__main__':
    pyPODGUI()
    Gtk.main()
