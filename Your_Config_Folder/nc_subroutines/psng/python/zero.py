#!/usr/bin/env python
#
# Copyright (c) 2015 Serguei Glavatski ( verser  from cnc-club.ru )
# Copyright (c) 2020 Probe Screen NG Developers
# Copyright (c) 2022 Alkabal free fr with different approach
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; If not, see <http://www.gnu.org/licenses/>.

from .base import ProbeScreenBase

import hal

class ProbeScreenZero(ProbeScreenBase):
    # --------------------------
    #
    #  INIT
    #
    # --------------------------
    def __init__(self, halcomp, builder, useropts):
        super(ProbeScreenZero, self).__init__(halcomp, builder, useropts)

        # connect the frame for allow to inhibit
        self.frm_zero = self.builder.get_object("frm_zero")

        # make the spinbox button
        self.spbtn_offs_x = self.builder.get_object("spbtn_offs_x")
        self.spbtn_offs_y = self.builder.get_object("spbtn_offs_y")
        self.spbtn_offs_z = self.builder.get_object("spbtn_offs_z")

        # make the Tickbox
        self.chk_use_auto_zero_offs_xyz = self.builder.get_object("chk_use_auto_zero_offs_xyz")
        self.chk_use_auto_zero_offs_xyz.set_active(self.prefs.getpref("chk_use_auto_zero_offs_xyz", False, bool))

        # make the LED
        self.hal_led_use_offs_x = self.builder.get_object("hal_led_use_offs_x")
        self.hal_led_use_offs_y = self.builder.get_object("hal_led_use_offs_y")
        self.hal_led_use_offs_z = self.builder.get_object("hal_led_use_offs_z")

        # make the pins hal
        self.halcomp.newpin("offs_x", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("offs_y", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("offs_z", hal.HAL_FLOAT, hal.HAL_OUT)

        self.halcomp.newpin("offs_x_active", hal.HAL_BIT, hal.HAL_OUT)
        self.halcomp.newpin("offs_y_active", hal.HAL_BIT, hal.HAL_OUT)
        self.halcomp.newpin("offs_z_active", hal.HAL_BIT, hal.HAL_OUT)

        self.halcomp.newpin("chk_use_auto_zero_offs_xyz", hal.HAL_BIT, hal.HAL_OUT)

        # After getting value we need to init some of them
        self._init_zero_offs_data()


    # --------------------------
    #
    # Init value etc
    #
    # --------------------------
    def _init_zero_offs_data(self):
        # load value regarding to the pref saved
        if self.prefs.getpref("chk_use_auto_zero_offs_xyz", False, bool):
            self.spbtn_offs_x.set_value(self.prefs.getpref("offs_x", 0.0, float))
            self.spbtn_offs_y.set_value(self.prefs.getpref("offs_y", 0.0, float))
            self.spbtn_offs_z.set_value(self.prefs.getpref("offs_z", 0.0, float))
            self.halcomp["offs_x"] = self.spbtn_offs_x.get_value()
            self.halcomp["offs_y"] = self.spbtn_offs_x.get_value()
            self.halcomp["offs_z"] = self.spbtn_offs_x.get_value()
            self.chk_use_auto_zero_offs_xyz.set_active(1)
            self.halcomp["chk_use_auto_zero_offs_xyz"] = 1
            self.hal_led_use_offs_x.set_property("on_color","blue")
            self.hal_led_use_offs_y.set_property("on_color","blue")
            self.hal_led_use_offs_z.set_property("on_color","blue")
            self.hal_led_use_offs_x.hal_pin.set(1)
            self.hal_led_use_offs_y.hal_pin.set(1)
            self.hal_led_use_offs_z.hal_pin.set(1)
            self.frm_zero.set_sensitive(False)
        else:
            self.spbtn_offs_x.set_value(self.prefs.getpref("offs_x", 0.0, float))
            self.spbtn_offs_y.set_value(self.prefs.getpref("offs_y", 0.0, float))
            self.spbtn_offs_z.set_value(self.prefs.getpref("offs_z", 0.0, float))
            self.frm_zero.set_sensitive(True)


    # --------------------------
    #
    # Checkbox select option
    #
    # --------------------------
    def on_chk_use_auto_zero_offs_xyz_toggled(self, gtkcheckbutton):
        self.halcomp["chk_use_auto_zero_offs_xyz"] = gtkcheckbutton.get_active()
        self.prefs.putpref("chk_use_auto_zero_offs_xyz", gtkcheckbutton.get_active(), bool)

        if self.halcomp["chk_use_auto_zero_offs_xyz"]:
            self.frm_zero.set_sensitive(False)
            self.halcomp["offs_x"] = self.spbtn_offs_x.get_value()
            self.halcomp["offs_y"] = self.spbtn_offs_y.get_value()
            self.halcomp["offs_z"] = self.spbtn_offs_z.get_value()
            self.prefs.putpref("offs_x", self.halcomp["offs_x"], float)
            self.prefs.putpref("offs_y", self.halcomp["offs_y"], float)
            self.prefs.putpref("offs_z", self.halcomp["offs_z"], float)
            self.add_history_text("Auto zero with offset is activated")
                                                                                 # todo check for actual offset applied vs hal for color pink
            if self.halcomp["offs_x"] == self.spbtn_offs_x.get_value():
               self.halcomp["offs_x_active"] = 1
               self.hal_led_use_offs_x.set_property("on_color","blue")
               self.hal_led_use_offs_x.hal_pin.set(1)
            else:
                self.halcomp["offs_x_active"] = 0
                self.hal_led_use_offs_x.set_property("on_color","orange")
                self.hal_led_use_offs_x.hal_pin.set(1)
                self.warning_dialog("OFFS_X GTK CHECKBUTTON UNKNOW STATUS")

                                                                                 # todo check for actual offset applied vs hal for color pink
            if self.halcomp["offs_y"] == self.spbtn_offs_y.get_value():
               self.halcomp["offs_y_active"] = 1
               self.hal_led_use_offs_y.set_property("on_color","blue")
               self.hal_led_use_offs_y.hal_pin.set(1)
            else:
                self.halcomp["offs_y_active"] = 0
                self.hal_led_use_offs_y.set_property("on_color","orange")
                self.hal_led_use_offs_y.hal_pin.set(1)
                self.warning_dialog("OFFS_Y GTK CHECKBUTTON UNKNOW STATUS")

                                                                                 # todo check for actual offset applied vs hal for color pink
            if self.halcomp["offs_z"] == self.spbtn_offs_z.get_value():
               self.halcomp["offs_z_active"] = 1
               self.hal_led_use_offs_z.set_property("on_color","blue")
               self.hal_led_use_offs_z.hal_pin.set(1)
            else:
                self.halcomp["offs_z_active"] = 0
                self.hal_led_use_offs_z.set_property("on_color","orange")
                self.hal_led_use_offs_z.hal_pin.set(1)
                self.warning_dialog("OFFS_Z GTK CHECKBUTTON UNKNOW STATUS")
        else:
            # now we can reset the offset correctly
# todo test new : not remember what append using this sub here in place of self.gcode
            s = "G10 L2 P0 X0 Y0 Z0"
            if self.gcode(s) == -1:
                return
# todo test new : not remember what append using this sub here in place of self.gcode
            #self._set_auto_zero_offset("XYZ")

            self.frm_zero.set_sensitive(True)
            self.halcomp["offs_x"] = 0
            self.prefs.putpref("offs_x", 0, int)
            self.halcomp["offs_x_active"] = 0
            self.hal_led_use_offs_x.hal_pin.set(0)
            self.halcomp["offs_y"] = 0
            self.prefs.putpref("offs_y", 0, int)
            self.halcomp["offs_y_active"] = 0
            self.hal_led_use_offs_y.hal_pin.set(0)
            self.halcomp["offs_z"] = 0
            self.prefs.putpref("offs_z", 0, int)
            self.halcomp["offs_z_active"] = 0
            self.hal_led_use_offs_z.hal_pin.set(0)
            self.add_history_text("Auto zero with offset is not activated")

    # --------------------------
    #
    # Spinbox entry editable
    #
    # --------------------------
    def on_spbtn_offs_x_key_press_event(self, gtkspinbutton, data=None):
        self.common_spbtn_key_press_event("offs_x", gtkspinbutton, data)
        if self.halcomp["offs_x_active"] == 0:
            if self.halcomp["offs_x"] == 0 and self.spbtn_offs_x.get_value() == 0:
                self.hal_led_use_offs_x.hal_pin.set(0)
            else:
                self.hal_led_use_offs_x.set_property("on_color","pink")
                self.hal_led_use_offs_x.hal_pin.set(1)
        elif self.halcomp["offs_x"] == self.spbtn_offs_x.get_value():
            self.hal_led_use_offs_x.set_property("on_color","green")
            self.hal_led_use_offs_x.hal_pin.set(1)
        else:
            self.hal_led_use_offs_x.set_property("on_color","red")
            self.hal_led_use_offs_x.hal_pin.set(1)

    def on_spbtn_offs_x_value_changed(self, gtkspinbutton):
        self.common_spbtn_value_changed("offs_x", gtkspinbutton)
        if self.halcomp["offs_x_active"] == 0:
            if self.halcomp["offs_x"] == 0 and self.spbtn_offs_x.get_value() == 0:
                self.hal_led_use_offs_x.hal_pin.set(0)
            else:
                self.hal_led_use_offs_x.set_property("on_color","pink")
                self.hal_led_use_offs_x.hal_pin.set(1)
        elif self.halcomp["offs_x"] == self.spbtn_offs_x.get_value():
            self.hal_led_use_offs_x.set_property("on_color","green")
            self.hal_led_use_offs_x.hal_pin.set(1)
        else:
            self.hal_led_use_offs_x.set_property("on_color","red")
            self.hal_led_use_offs_x.hal_pin.set(1)

    def on_spbtn_offs_y_key_press_event(self, gtkspinbutton, data=None):
        self.common_spbtn_key_press_event("offs_y", gtkspinbutton, data)
        if self.halcomp["offs_y_active"] == 0:
            if self.halcomp["offs_y"] == 0 and self.spbtn_offs_y.get_value() == 0:
                self.hal_led_use_offs_y.hal_pin.set(0)
            else:
                self.hal_led_use_offs_y.set_property("on_color","pink")
                self.hal_led_use_offs_y.hal_pin.set(1)
        elif self.halcomp["offs_y"] == self.spbtn_offs_y.get_value():
            self.hal_led_use_offs_y.set_property("on_color","green")
            self.hal_led_use_offs_y.hal_pin.set(1)
        else:
            self.hal_led_use_offs_y.set_property("on_color","red")
            self.hal_led_use_offs_y.hal_pin.set(1)

    def on_spbtn_offs_y_value_changed(self, gtkspinbutton):
        self.common_spbtn_value_changed("offs_y", gtkspinbutton)
        if self.halcomp["offs_y_active"] == 0:
            if self.halcomp["offs_y"] == 0 and self.spbtn_offs_y.get_value() == 0:
                self.hal_led_use_offs_y.hal_pin.set(0)
            else:
                self.hal_led_use_offs_y.set_property("on_color","pink")
                self.hal_led_use_offs_y.hal_pin.set(1)
        elif self.halcomp["offs_y"] == self.spbtn_offs_y.get_value():
            self.hal_led_use_offs_y.set_property("on_color","green")
            self.hal_led_use_offs_y.hal_pin.set(1)
        else:
            self.hal_led_use_offs_y.set_property("on_color","red")
            self.hal_led_use_offs_y.hal_pin.set(1)

    def on_spbtn_offs_z_key_press_event(self, gtkspinbutton, data=None):
        self.common_spbtn_key_press_event("offs_z", gtkspinbutton, data)
        if self.halcomp["offs_z_active"] == 0:
            if self.halcomp["offs_z"] == 0 and self.spbtn_offs_z.get_value() == 0:
                self.hal_led_use_offs_z.hal_pin.set(0)
            else:
                self.hal_led_use_offs_z.set_property("on_color","pink")
                self.hal_led_use_offs_z.hal_pin.set(1)
        elif self.halcomp["offs_z"] == self.spbtn_offs_z.get_value():
            self.hal_led_use_offs_z.set_property("on_color","green")
            self.hal_led_use_offs_z.hal_pin.set(1)
        else:
            self.hal_led_use_offs_z.set_property("on_color","red")
            self.hal_led_use_offs_z.hal_pin.set(1)

    def on_spbtn_offs_z_value_changed(self, gtkspinbutton):
        self.common_spbtn_value_changed("offs_z", gtkspinbutton)
        if self.halcomp["offs_z_active"] == 0:
            if self.halcomp["offs_z"] == 0 and self.spbtn_offs_z.get_value() == 0:
                self.hal_led_use_offs_z.hal_pin.set(0)
            else:
                self.hal_led_use_offs_z.set_property("on_color","pink")
                self.hal_led_use_offs_z.hal_pin.set(1)
        elif self.halcomp["offs_z"] == self.spbtn_offs_z.get_value():
            self.hal_led_use_offs_z.set_property("on_color","green")
            self.hal_led_use_offs_z.hal_pin.set(1)
        else:
            self.hal_led_use_offs_z.set_property("on_color","red")
            self.hal_led_use_offs_z.hal_pin.set(1)

    # --------------------------
    #
    # Touch Off Buttons
    #
    # --------------------------
    # button pressed set offset x manually
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_set_x_released(self, gtkbutton):
        if self.spbtn_offs_x.get_value() == 0:
            self.hal_led_use_offs_x.hal_pin.set(0)
            self.halcomp["offs_x"] = 0
            self._set_auto_zero_offset("X")
            self.halcomp["offs_x_active"] = 0
            self.prefs.putpref("offs_x", 0, int)
            self.add_history_text("OFFSET_BOX_X REMOVED FROM G10_L2")
        else:
            self.hal_led_use_offs_x.set_property("on_color","green")
            self.hal_led_use_offs_x.hal_pin.set(1)
            self.halcomp["offs_x"] = self.spbtn_offs_x.get_value()
            self._set_auto_zero_offset("X")
            self.halcomp["offs_x_active"] = 1
            self.prefs.putpref("offs_x", self.halcomp["offs_x"], float)
            self.add_history_text("OFFSET_BOX_X %.4f ADDED TO G10_L2" % (self.halcomp["offs_x"]))

    # button pressed set offset y manually
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_set_y_released(self, gtkbutton):
        if self.spbtn_offs_y.get_value() == 0:
            self.hal_led_use_offs_y.hal_pin.set(0)
            self.halcomp["offs_y"] = 0
            self._set_auto_zero_offset("Y")
            self.halcomp["offs_y_active"] = 0
            self.prefs.putpref("offs_y", 0, int)
            self.add_history_text("OFFSET_BOX_Y REMOVED FROM G10_L2")
        else:
            self.hal_led_use_offs_y.set_property("on_color","green")
            self.hal_led_use_offs_y.hal_pin.set(1)
            self.halcomp["offs_y"] = self.spbtn_offs_y.get_value()
            self._set_auto_zero_offset("Y")
            self.halcomp["offs_y_active"] = 1
            self.prefs.putpref("offs_y", self.halcomp["offs_y"], float)
            self.add_history_text("OFFSET_BOX_Y %.4f ADDED TO G10_L2" % (self.halcomp["offs_y"]))

    # button pressed set offset z manually
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_set_z_released(self, gtkbutton):
        if self.spbtn_offs_z.get_value() == 0:
            self.hal_led_use_offs_z.hal_pin.set(0)
            self.halcomp["offs_z"] = 0
            self._set_auto_zero_offset("Z")
            self.halcomp["offs_z_active"] = 0
            self.prefs.putpref("offs_z", 0, int)
            self.add_history_text("OFFSET_BOX_Z REMOVED FROM G10_L2")
        else:
            self.hal_led_use_offs_z.set_property("on_color","green")
            self.hal_led_use_offs_z.hal_pin.set(1)
            self.halcomp["offs_z"] = self.spbtn_offs_z.get_value()
            self._set_auto_zero_offset("Z")
            self.halcomp["offs_z_active"] = 1
            self.prefs.putpref("offs_z", self.halcomp["offs_z"], float)
            self.add_history_text("OFFSET_BOX_Z %.4f ADDED TO G10_L2" % (self.halcomp["offs_z"]))


