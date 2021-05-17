#!/usr/bin/env python3

import gi
import line6
import pypod
import time
import mido
import argparse

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject

class pyPODGUI:
    # by default we are now quiet, loglevel can now be set with -l / --log-level
    pypod = pypod.pyPOD(loglevel="CRITICAL")
    builder = ""
    midi_inputs = []
    midi_outputs = []

    def callbackMIDI(self, message):
        # this is the new callback function so we can update the GUI in
        # realtime when we receive CC-messages because settings were
        # changed on the pod (by turning a knob or by switching program)
        # copied from pypod.py:
        # a single program dump is 152 bytes long (9 bytes header, 142 bytes data, &xF7 is the last byte)
        if message.type == 'sysex' and len(message.bytes()) == 152:
            self.pypod.logger.debug(f"Received sysex (program dump)")
            self.pypod.parse_progdump(message)
            # if we call updateGUI from here, we no longer need time.sleep()!
            self.updateGUI()
        elif message.type == 'sysex' and len(message.bytes()) == 17:
            pod_version = "".join([chr(x) for x in message.bytes()[12:16]])
            manufacturer_id = "{:02X} {:02X} {:02X}".format(message.bytes()[5], message.bytes()[6], message.bytes()[7])
            product_family = "{:02X}{:02X}".format(message.bytes()[9], message.bytes()[8])
            product_family_member = "{:02X}{:02X}".format(message.bytes()[11], message.bytes()[10])
            self.pypod.logger.debug("Received sysex (device info)")
            self.go("EntryPODVersion").set_text(pod_version)
            self.go("EntryManufacturerID").set_text(manufacturer_id)
            self.go("EntryProductFamilyID").set_text(product_family)
            self.go("EntryProductFamilyMember").set_text(product_family_member)
        elif message.type == 'sysex' and len(message.bytes()) == 151:
            # the editbuffer-dump is one byte shorter than a regular program dump
            dummymsg = mido.Message('sysex', data = [ 0 ])
            message.data = dummymsg.data + message.data
            self.pypod.parse_progdump(message)
            self.pypod.logger.debug("Received sysex (edit buffer)")
            self.updateGUI()
        elif message.type == 'program_change' and len(message.bytes()) == 2:
            prog = "Edit Buffer" if message.bytes()[1] == 0 else line6.PROGRAMS[message.bytes()[1]-1]
            self.pypod.logger.debug(f"Received program_change message: {prog}")
            if prog == "Edit Buffer":
                self.download_editbuffer()
            else:
                self.go("ComboBoxProgram").set_active(int(message.bytes()[1]-1))
                self.download_program()
        elif message.type == 'control_change':
            self.pypod.logger.debug(f"Received CC: {message.bytes()}")
            self.updatewidgets(message.bytes())
        else:
            # this usually only happens when there is some issue with
            # the MIDI connection and MIDI data sent to the pod gets
            # returned to the application.
            self.pypod.logger.warning(f"Unknown message type {message.type}: {message.bytes()} ({len(message.bytes())}) bytes:")

    def __init__(self, **kwargs):
        if kwargs['loglevel']:
            self.pypod.set_loglevel(kwargs['loglevel'])
            self.pypod.logger.info(f"Set loglevel to {kwargs['loglevel']}")
        self.builder = Gtk.Builder()
        self.builder.add_from_file("pypod_gui.glade")
        # {{{ handlers:
        handlers = {
            "onDestroy": Gtk.main_quit,
            "onAbout": self.about_dialog,
            "onMenuSaveAs": self.save_file,
            "onMenuOpen": self.open_file,
            "onMenuQuit": Gtk.main_quit,
            "onMenuDownload": self.download_program,
            "onMenuUpload": self.upload_program,
            "onMenuDownloadEditBuffer": self.download_editbuffer,
            "onGetDeviceInfo": self.get_deviceinfo,
            "onRescanMIDI": self.rescanMIDI,
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
        self.pypod.inport.callback = self.callbackMIDI
        window = self.builder.get_object("MainWindow")
        # {{{ fill ComboBoxes:
        self.rescanMIDI()

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
        
        programlist = self.go("ListStoreProgram")
        for program in line6.PROGRAMS:
            programlist.append([program])

        # }}}
        window.show_all()

    # {{{ signal handling functions:
    def go(self, objname):
        return self.builder.get_object(objname)

    def rescanMIDI(self, *args):
        self.pypod.logger.debug("Scanning for MIDI devices...")
        self.midi_outputs = self.pypod.get_midioutputs()
        midi_outputlist = self.go("ListStoreMIDIOutput")
        midi_outputlist.clear()
        for output in self.midi_outputs:
            midi_outputlist.append([output])
            if output == self.pypod.outport.name:
                self.go("ComboBoxMIDIOutput").set_active(self.midi_outputs.index(output))


        self.midi_inputs = self.pypod.get_midiinputs()
        midi_inputlist = self.go("ListStoreMIDIInput")
        midi_inputlist.clear()
        for m_input in self.midi_inputs:
            midi_inputlist.append([m_input])
            if m_input == self.pypod.inport.name:
                self.pypod.logger.debug(f"active MIDI input: {m_input}")
                self.go("ComboBoxMIDIInput").set_active(self.midi_inputs.index(m_input))

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
        gate = 0
        gatesw = self.go("CheckButtonNoiseGate").get_active()
        if gatesw:
            gate = 127
        self.pypod.send_cc(22, gate)

    def change_noisegate_thresh(self, *args):
        threshhold = int(self.go("ScaleGateThresh").get_value())
        self.pypod.send_cc(23, threshhold)

    def change_noisegate_decay(self, *args):
        decay = int(self.go("ScaleGateDecay").get_value())
        self.pypod.send_cc(24, decay)

    def toggle_distortion(self, *args):
        dist = 0
        distsw = self.go("CheckButtonDistortion").get_active()
        if distsw:
            dist = 127
        self.pypod.send_cc(25, dist)

    def change_drive(self, *args):
        drive = int(self.go("ScaleDrive").get_value())
        self.pypod.send_cc(13, drive)

    def toggle_driveboost(self, *args):
        driveb = 0
        drivebsw = self.go("CheckButtonDriveBoost").get_active()
        if drivebsw:
            driveb = 0
        self.pypod.send_cc(26, driveb)

    def toggle_presence(self, *args):
        presence = 0
        presencesw = self.go("CheckButtonPresence").get_active()
        if presencesw:
            presence = 127
        self.pypod.send_cc(27, presence)

    def change_presence(self, *args):
        presence = int(self.go("ScalePresence").get_value())
        self.pypod.send_cc(21, presence)

    def toggle_bright(self, *args):
        bright = 0
        brightsw = self.go("CheckButtonBright").get_active()
        if brightsw:
            bright = 127
        self.pypod.send_cc(73, bright)

    def toggle_delay(self, *args):
        delay = 0
        delaysw = self.go("CheckButtonDelay").get_active()
        if delaysw:
            delay = 127
        self.pypod.send_cc(28, delay)
        #self.pypod.logger.debug(f"delay: {delay} (sw: {delaysw})")

    def change_delaytime(self, *args):
        delaytime = int(self.go("ScaleDelayTime").get_value())
        self.pypod.send_cc(30, delaytime)
        self.update_delaytime()

    def change_delaytime2(self, *args):
        delaytime2 = int(self.go("ScaleDelayTime2").get_value())
        self.pypod.send_cc(62, delaytime2)
        self.update_delaytime()

    def change_delayrepeats(self, *args):
        delayrepeats = int(self.go("ScaleDelayRepeats").get_value())
        self.pypod.send_cc(32, delayrepeats)

    def change_delaylevel(self, *args):
        delaylevel = int(self.go("ScaleDelayLevel").get_value())
        self.pypod.send_cc(34, delaylevel)

    def toggle_reverb(self, *args):
        rev = 0
        revsw = self.go("CheckButtonReverb").get_active()
        if revsw:
            rev = 127
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
        self.pypod.inport.callback = self.callbackMIDI

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

    def download_program(self, *args):
        # downloads program selected in ComboBoxProgram
        program = self.get_combobox_program()
        # program is just the index of the selected element but it is the
        # same index as in line6.PROGRAMS[]
        self.pypod.dump_program(program)
        if len(args) == 1:
            # we are getting called from the GUI, so
            # we send a program change to the pod:
            prog = line6.PROGRAMS.index(program)
            self.pypod.send_pc(prog + 1)
        self.pypod.logger.debug(f"program: {program}")

    def upload_program(self, *args):
        # first, download the edit buffer, but save the Name Entry before that:
        new_name = self.go("EntryPatchName").get_text()
        self.pypod.dump_editbuffer()
        time.sleep(1)
        program = self.get_combobox_program()
        self.go("EntryPatchName").set_text(new_name)
        self.update_programname()
        self.pypod.logger.debug(f"Uploading {program}")
        self.pypod.upload_program(program)

    def update_programname(self, *args):
        self.pypod.change_name(self.go("EntryPatchName").get_text())

    def get_deviceinfo(self, *args):
        self.pypod.udq()

    def calculate_delaytime(self, *args):
        msg = self.pypod.msg_bytes
        delay = int(self.go("ScaleDelayTime").get_value())
        delay2 = int(self.go("ScaleDelayTime2").get_value())
        delaytime = int(((delay << 7) | delay2) * 0.192272) #3150/16383 steps
        return delaytime

    def update_delaytime(self, *args):
        self.go("EntryDelayMS").set_text(str(self.calculate_delaytime()))

    def about_dialog(self, *args):
        dialog = Gtk.MessageDialog(
            #transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="pyPOD GUI",
            )
        dialog.format_secondary_text(
            """a simple gui for pypod.py
by C. Barth 2021
https://github.com/ChrBarth/pypod
See README.md for more info"""
        )
        dialog.run()
        dialog.destroy()

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
            # We need to update the edit buffer after we load a file
            # otherwise the GUI will show the settings of the file
            # but the settings on the pod will remain unchanged. For that
            # we have to use pypod.upload_editbuffer()
            self.updateGUI()
            self.pypod.upload_editbuffer()
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
        self.block_handlers()
        msg = self.pypod.msg_bytes
        self.go("ComboBoxAmpModel").set_active(msg[9])
        self.go("ComboBoxCabModel").set_active(msg[45])
        self.go("ComboBoxEffect").set_active(msg[47])
        self.go("ComboBoxCompressionRatio").set_active(msg[49])
        self.go("ComboBoxReverbType").set_active(msg[39])
        self.go("ComboBoxVolumePos").set_active(msg[25])
        gate = True if msg[7] == 1 else False
        self.go("CheckButtonNoiseGate").set_active(gate)
        dist = True if msg[1] == 1 else False
        self.go("CheckButtonDistortion").set_active(dist)
        boost = True if msg[2] == 1 else False
        self.go("CheckButtonDriveBoost").set_active(boost)
        presence = True if msg[3] == 1 else False
        self.go("CheckButtonPresence").set_active(presence)
        bright = True if msg[8] == 1 else False
        self.go("CheckButtonBright").set_active(bright)
        mod = True if msg[5] == 1 else False
        self.go("SwitchModulation").set_state(mod)
        delay = True if msg[4] == 1 else False
        self.go("CheckButtonDelay").set_active(delay)
        reverb = True if msg[6] == 1 else False
        self.go("CheckButtonReverb").set_active(reverb)
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
        delay = msg[28] << 8
        delay = delay | msg[29]
        delay = delay << 8
        delay = delay | msg[30]
        delay = int(delay/6)
        delay2 = delay & 127
        delay1 = delay >> 7
        #self.pypod.logger.debug(f"delay: {delay:0x} -> {delay2} + {delay1}")
        self.go("ScaleDelayTime").set_value(delay1)
        self.go("ScaleDelayTime2").set_value(delay2)
        self.update_delaytime()
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
        progname = "".join(map(chr,msg[56:]))
        self.go("EntryPatchName").set_text(progname)
        self.unblock_handlers()
    # }}}

    # {{{ updatewidets
    def updatewidgets(self, m_bytes):
        self.pypod.logger.debug(f"m_bytes: {m_bytes}")
        self.block_handlers()
        if m_bytes[0] == 176 and len(m_bytes) == 3:
            # CC received:
            cc = m_bytes[1]
            val = m_bytes[2]
            if cc == 12:
                self.go("ComboBoxAmpModel").set_active(val)
            if cc == 71:
                self.go("ComboBoxCabModel").set_active(val)
            if cc == 19:
                self.go("ComboBoxEffect").set_active(val)
            if cc == 17:
                self.go("ScaleChannelVol").set_value(val)
            if cc == 14:
                self.go("ScaleBass").set_value(val)
            if cc == 15:
                self.go("ScaleMid").set_value(val)
            if cc == 16:
                self.go("ScaleTreble").set_value(val)
            if cc == 23:
                self.go("ScaleGateThresh").set_value(val)
            if cc == 24:
                self.go("ScaleGateDecay").set_value(val)
            if cc == 72:
                self.go("ScaleAIRAmbience").set_value(val)
            if cc == 1:
                self.go("ScaleEffectTweak").set_value(val)
            if cc == 13:
                self.go("ScaleDrive").set_value(val)
            if cc == 21:
                self.go("ScalePresence").set_value(val)
            if cc == 51:
                self.go("ScaleModSpeed").set_value(val)
            if cc == 52:
                self.go("ScaleModDepth").set_value(val)
            if cc == 53:
                self.go("ScaleFeedback").set_value(val)
            if cc == 54:
                self.go("ScaleChorusPreDelay").set_value(val)
            if cc == 55:
                self.go("ScaleRotarySpeed").set_value(val)
            if cc == 56:
                self.go("ScaleRotaryMaxSpeed").set_value(val)
            if cc == 57:
                self.go("ScaleRotaryMinSpeed").set_value(val)
            if cc == 58:
                self.go("ScaleTremoloSpeed").set_value(val)
            if cc == 59:
                self.go("ScaleTremoloDepth").set_value(val)
            if cc == 22:
                gate = True if val > 0 else False
                self.go("CheckButtonNoiseGate").set_active(gate)
            if cc == 25:
                dist = True if val > 0 else False
                self.go("CheckButtonDistortion").set_active(dist)
            if cc == 26:
                boost = True if val > 0 else False
                self.go("CheckButtonDriveBoost").set_active(boost)
            if cc == 27:
                presence = True if val > 0 else False
                self.go("CheckButtonPresence").set_active(presence)
            if cc == 73:
                bright = True if val > 0 else False
                self.go("CheckButtonBright").set_active(bright)
            if cc == 34:
                self.go("ScaleDelayLevel").set_value(val)
            if cc == 32:
                self.go("ScaleDelayRepeats").set_value(val)
            self.unblock_handlers()
    # }}}

    # {{{ blocking/unblocking signal handlers:
    def block_handlers(self):
        """
           blocks signal handlers, so we do not immediately re-send settings
           we just received from the pod
           https://python-gtk-3-tutorial.readthedocs.io/en/latest/objects.html#signals
           https://www.parlatype.org/reference/python_example.html
        """
        GObject.GObject.handler_block_by_func(self.go("ComboBoxAmpModel"), self.change_amp)
        GObject.GObject.handler_block_by_func(self.go("ComboBoxCabModel"), self.change_cab)
        GObject.GObject.handler_block_by_func(self.go("ScaleChannelVol"), self.change_channel_vol)
        GObject.GObject.handler_block_by_func(self.go("ScaleBass"), self.change_bass)
        GObject.GObject.handler_block_by_func(self.go("ScaleMid"), self.change_mid)
        GObject.GObject.handler_block_by_func(self.go("ScaleTreble"), self.change_treble)
        GObject.GObject.handler_block_by_func(self.go("ScaleDrive"), self.change_drive)
        GObject.GObject.handler_block_by_func(self.go("CheckButtonDistortion"), self.toggle_distortion)
        GObject.GObject.handler_block_by_func(self.go("CheckButtonDriveBoost"), self.toggle_driveboost)
        GObject.GObject.handler_block_by_func(self.go("CheckButtonPresence"), self.toggle_presence)
        GObject.GObject.handler_block_by_func(self.go("ScalePresence"), self.change_presence)
        GObject.GObject.handler_block_by_func(self.go("ScaleAIRAmbience"), self.change_airambience)
        GObject.GObject.handler_block_by_func(self.go("CheckButtonBright"), self.toggle_bright)
        GObject.GObject.handler_block_by_func(self.go("ComboBoxEffect"), self.change_effect)
        GObject.GObject.handler_block_by_func(self.go("ScaleEffectTweak"), self.change_effect_tweak)
        GObject.GObject.handler_block_by_func(self.go("ScaleModSpeed"), self.change_modspeed)
        GObject.GObject.handler_block_by_func(self.go("ScaleModDepth"), self.change_moddepth)
        GObject.GObject.handler_block_by_func(self.go("ScaleFeedback"), self.change_feedback)
        GObject.GObject.handler_block_by_func(self.go("ScaleChorusPreDelay"), self.change_choruspredelay)
        GObject.GObject.handler_block_by_func(self.go("ScaleRotarySpeed"), self.change_rotaryspeed)
        GObject.GObject.handler_block_by_func(self.go("ScaleRotaryMaxSpeed"), self.change_rotarymaxspeed)
        GObject.GObject.handler_block_by_func(self.go("ScaleRotaryMinSpeed"), self.change_rotaryminspeed)
        GObject.GObject.handler_block_by_func(self.go("ScaleTremoloSpeed"), self.change_tremolospeed)
        GObject.GObject.handler_block_by_func(self.go("ScaleTremoloDepth"), self.change_tremolodepth)
        GObject.GObject.handler_block_by_func(self.go("ComboBoxCompressionRatio"), self.change_compressionvalue)
        GObject.GObject.handler_block_by_func(self.go("CheckButtonNoiseGate"), self.toggle_noisegate)
        GObject.GObject.handler_block_by_func(self.go("ScaleGateThresh"), self.change_noisegate_thresh)
        GObject.GObject.handler_block_by_func(self.go("ScaleGateDecay"), self.change_noisegate_decay)
        GObject.GObject.handler_block_by_func(self.go("CheckButtonDelay"), self.toggle_delay)
        GObject.GObject.handler_block_by_func(self.go("ScaleDelayTime"), self.change_delaytime)
        GObject.GObject.handler_block_by_func(self.go("ScaleDelayTime2"), self.change_delaytime2)
        GObject.GObject.handler_block_by_func(self.go("ScaleDelayRepeats"), self.change_delayrepeats)
        GObject.GObject.handler_block_by_func(self.go("ScaleDelayLevel"), self.change_delaylevel)
        GObject.GObject.handler_block_by_func(self.go("CheckButtonReverb"), self.toggle_reverb)
        GObject.GObject.handler_block_by_func(self.go("ScaleReverbLevel"), self.change_reverblevel)
        GObject.GObject.handler_block_by_func(self.go("ComboBoxReverbType"), self.change_reverbtype)
        GObject.GObject.handler_block_by_func(self.go("ScaleReverbDecay"), self.change_reverbdecay)
        GObject.GObject.handler_block_by_func(self.go("ScaleReverbTone"), self.change_reverbtone)
        GObject.GObject.handler_block_by_func(self.go("ScaleReverbDiffusion"), self.change_reverbdiffusion)
        GObject.GObject.handler_block_by_func(self.go("ScaleReverbDensity"), self.change_reverbdensity)
        GObject.GObject.handler_block_by_func(self.go("SwitchWah"), self.toggle_wah)
        GObject.GObject.handler_block_by_func(self.go("ScaleWahPosition"), self.change_wahposition)
        GObject.GObject.handler_block_by_func(self.go("ScaleWahBottom"), self.change_wahbottom)
        GObject.GObject.handler_block_by_func(self.go("ScaleWahTop"), self.change_wahtop)
        GObject.GObject.handler_block_by_func(self.go("ScaleVolumePedal"), self.change_volumepedal)
        GObject.GObject.handler_block_by_func(self.go("ScaleVolumePedalMin"), self.change_volumepedalmin)
        GObject.GObject.handler_block_by_func(self.go("ComboBoxVolumePos"), self.change_volumepos)
        GObject.GObject.handler_block_by_func(self.go("SwitchVolumeSwell"), self.toggle_volumeswell)
        GObject.GObject.handler_block_by_func(self.go("ScaleVolumeSwellRamp"), self.change_volumeswellramp)

    def unblock_handlers(self):
        """
           blocks signal handlers, so we do not immediately re-send settings
           we just received from the pod
           https://python-gtk-3-tutorial.readthedocs.io/en/latest/objects.html#signals
           https://www.parlatype.org/reference/python_example.html
        """
        GObject.GObject.handler_unblock_by_func(self.go("ComboBoxAmpModel"), self.change_amp)
        GObject.GObject.handler_unblock_by_func(self.go("ComboBoxCabModel"), self.change_cab)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleChannelVol"), self.change_channel_vol)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleBass"), self.change_bass)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleMid"), self.change_mid)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleTreble"), self.change_treble)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleDrive"), self.change_drive)
        GObject.GObject.handler_unblock_by_func(self.go("CheckButtonDistortion"), self.toggle_distortion)
        GObject.GObject.handler_unblock_by_func(self.go("CheckButtonDriveBoost"), self.toggle_driveboost)
        GObject.GObject.handler_unblock_by_func(self.go("CheckButtonPresence"), self.toggle_presence)
        GObject.GObject.handler_unblock_by_func(self.go("ScalePresence"), self.change_presence)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleAIRAmbience"), self.change_airambience)
        GObject.GObject.handler_unblock_by_func(self.go("CheckButtonBright"), self.toggle_bright)
        GObject.GObject.handler_unblock_by_func(self.go("ComboBoxEffect"), self.change_effect)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleEffectTweak"), self.change_effect_tweak)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleModSpeed"), self.change_modspeed)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleModDepth"), self.change_moddepth)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleFeedback"), self.change_feedback)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleChorusPreDelay"), self.change_choruspredelay)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleRotarySpeed"), self.change_rotaryspeed)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleRotaryMaxSpeed"), self.change_rotarymaxspeed)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleRotaryMinSpeed"), self.change_rotaryminspeed)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleTremoloSpeed"), self.change_tremolospeed)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleTremoloDepth"), self.change_tremolodepth)
        GObject.GObject.handler_unblock_by_func(self.go("ComboBoxCompressionRatio"), self.change_compressionvalue)
        GObject.GObject.handler_unblock_by_func(self.go("CheckButtonNoiseGate"), self.toggle_noisegate)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleGateThresh"), self.change_noisegate_thresh)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleGateDecay"), self.change_noisegate_decay)
        GObject.GObject.handler_unblock_by_func(self.go("CheckButtonDelay"), self.toggle_delay)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleDelayTime"), self.change_delaytime)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleDelayTime2"), self.change_delaytime2)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleDelayRepeats"), self.change_delayrepeats)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleDelayLevel"), self.change_delaylevel)
        GObject.GObject.handler_unblock_by_func(self.go("CheckButtonReverb"), self.toggle_reverb)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleReverbLevel"), self.change_reverblevel)
        GObject.GObject.handler_unblock_by_func(self.go("ComboBoxReverbType"), self.change_reverbtype)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleReverbDecay"), self.change_reverbdecay)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleReverbTone"), self.change_reverbtone)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleReverbDiffusion"), self.change_reverbdiffusion)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleReverbDensity"), self.change_reverbdensity)
        GObject.GObject.handler_unblock_by_func(self.go("SwitchWah"), self.toggle_wah)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleWahPosition"), self.change_wahposition)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleWahBottom"), self.change_wahbottom)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleWahTop"), self.change_wahtop)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleVolumePedal"), self.change_volumepedal)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleVolumePedalMin"), self.change_volumepedalmin)
        GObject.GObject.handler_unblock_by_func(self.go("ComboBoxVolumePos"), self.change_volumepos)
        GObject.GObject.handler_unblock_by_func(self.go("SwitchVolumeSwell"), self.toggle_volumeswell)
        GObject.GObject.handler_unblock_by_func(self.go("ScaleVolumeSwellRamp"), self.change_volumeswellramp)
    # }}}

if __name__ == '__main__':
    # style stuff from
    # https://gist.github.com/fcwu/5794494
    css = b"""
    .borderframe {
        border-bottom: solid 1px #ccc;
        padding: 4px;
        }
    .PODInfo {
        font-weight: bold;
        color: #555;
        }
    """
    style_provider =  Gtk.CssProvider()
    style_provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        style_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    # end style stuff
    
    # parsing arguments:
    parser = argparse.ArgumentParser('pypod_gui.py')
    parser.add_argument('-l', '--log-level', type=str, help='Uploads program data (from file) to pod', dest='log_level')

    args=parser.parse_args()

    loglevel = "ERROR"
    if args.log_level:
        if args.log_level in [ "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL" ]:
            loglevel = args.log_level

    pyPODGUI(loglevel=loglevel)
    Gtk.main()
