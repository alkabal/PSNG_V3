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

        self.halcomp.newpin("offs_x", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("offs_y", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("offs_z", hal.HAL_FLOAT, hal.HAL_OUT)

        self.spbtn_offs_x = self.builder.get_object("spbtn_offs_x")
        self.spbtn_offs_y = self.builder.get_object("spbtn_offs_y")
        self.spbtn_offs_z = self.builder.get_object("spbtn_offs_z")

        self.spbtn_offs_x.set_value(self.prefs.getpref("offs_x", 0.0, float))
        self.spbtn_offs_y.set_value(self.prefs.getpref("offs_y", 0.0, float))
        self.spbtn_offs_z.set_value(self.prefs.getpref("offs_z", 0.0, float))

        self.hal_led_set_zero = self.builder.get_object("hal_led_set_zero")

        self.halcomp.newpin("chk_set_zero", hal.HAL_BIT, hal.HAL_OUT)
        self.chk_set_zero = self.builder.get_object("chk_set_zero")

        self.chk_set_zero.set_active(self.prefs.getpref("chk_set_zero", False, bool))
        self.halcomp["chk_set_zero"] = self.chk_set_zero.get_active()
        self.hal_led_set_zero.hal_pin.set(self.chk_set_zero.get_active())


    # --------------------------
    #
    # Touch Off Buttons
    #
    # --------------------------
    def on_chk_set_zero_toggled(self, gtkcheckbutton, data=None):
        self.halcomp["chk_set_zero"] = gtkcheckbutton.get_active()
        self.hal_led_set_zero.hal_pin.set(gtkcheckbutton.get_active())
        self.prefs.putpref("chk_set_zero", gtkcheckbutton.get_active(), bool)

    def on_spbtn_offs_x_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("offs_x", gtkspinbutton, data)

    def on_spbtn_offs_x_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("offs_x", gtkspinbutton, data)

    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_set_x_released(self, gtkbutton, data=None):
        s = "G10 L20 P0 X%f" % (self.spbtn_offs_x.get_value())
        if self.gcode(s) == -1:
            return
        self.add_history_text("offs_x = %.4f" % (self.spbtn_offs_x.get_value()))
        #self.vcp_reload()

    def on_spbtn_offs_y_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("offs_y", gtkspinbutton, data)

    def on_spbtn_offs_y_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("offs_y", gtkspinbutton, data)

    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_set_y_released(self, gtkbutton, data=None):
        s = "G10 L20 P0 Y%f" % (self.spbtn_offs_y.get_value())
        if self.gcode(s) == -1:
            return
        self.add_history_text("offs_y = %.4f" % (self.spbtn_offs_y.get_value()))
        #self.vcp_reload()

    def on_spbtn_offs_z_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("offs_z", gtkspinbutton, data)

    def on_spbtn_offs_z_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("offs_z", gtkspinbutton, data)

    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_set_z_released(self, gtkbutton, data=None):
        s = "G10 L20 P0 Z%f" % (self.spbtn_offs_z.get_value())
        if self.gcode(s) == -1:
            return
        self.add_history_text("offs_z_applyed = %.4f" % (self.spbtn_offs_z.get_value()))
        #self.vcp_reload()
