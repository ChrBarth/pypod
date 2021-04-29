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
            "onEffectTweakChange": self.change_effect_tweak
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

if __name__ == '__main__':
    pyPODGUI()
    Gtk.main()
