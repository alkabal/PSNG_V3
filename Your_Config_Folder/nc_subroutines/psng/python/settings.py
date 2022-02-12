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

import os
import sys

import hal
import hal_glib

from subprocess import Popen, PIPE

class ProbeScreenSettings(ProbeScreenBase):
    # --------------------------
    #
    #  INIT
    #
    # --------------------------
    def __init__(self, halcomp, builder, useropts):
        super(ProbeScreenSettings, self).__init__(halcomp, builder, useropts)

        self.spbtn_vel_for_travel = self.builder.get_object("spbtn_vel_for_travel")
        self.spbtn_vel_for_search = self.builder.get_object("spbtn_vel_for_search")
        self.spbtn_vel_for_probe = self.builder.get_object("spbtn_vel_for_probe")
        self.spbtn_probe_max_z = self.builder.get_object("spbtn_probe_max_z")
        self.spbtn_probe_max_xy = self.builder.get_object("spbtn_probe_max_xy")
        self.spbtn_probe_max_latch = self.builder.get_object("spbtn_probe_max_latch")
        self.spbtn_latch = self.builder.get_object("spbtn_latch")
        self.spbtn_edge_length = self.builder.get_object("spbtn_edge_length")

        self.chk_use_touch_plate = self.builder.get_object("chk_use_touch_plate")
        self.hal_led_use_touch_plate = self.builder.get_object("hal_led_use_touch_plate")

        if self.inifile.find("TRAJ", "LINEAR_UNITS") not in ["metric", "mm"]:
            # default values for inches
            tup = (20.0, 2.0, 0.5, 1.0, 0.1, 0.125, 1.0, 1.25)
        else:
            tup = (300.0, 10.0, 3.0, 1.0, 0.5, 2.0, 5.0, 5.0)

        self.spbtn_vel_for_travel.set_value(
            self.prefs.getpref("vel_for_travel", tup[2], float)
        )
        self.spbtn_vel_for_search.set_value(
            self.prefs.getpref("vel_for_search", tup[0], float)
        )
        self.spbtn_vel_for_probe.set_value(
            self.prefs.getpref("vel_for_probe", tup[1], float)
        )
        self.spbtn_probe_max_z.set_value(
            self.prefs.getpref("probe_max_z", tup[3], float)
        )
        self.spbtn_probe_max_xy.set_value(
            self.prefs.getpref("probe_max_xy", tup[6], float)
        )
        self.spbtn_probe_max_latch.set_value(
            self.prefs.getpref("probe_max_latch", tup[5], float)
        )
        self.spbtn_latch.set_value(
            self.prefs.getpref("latch", tup[4], float)
        )
        self.spbtn_edge_length.set_value(
            self.prefs.getpref("edge_length", tup[7], float)
        )
        self.chk_use_touch_plate.set_active(
            self.prefs.getpref("chk_use_touch_plate", False, bool)
        )

        # create the pins for GUI settings
        self.halcomp.newpin("vel_for_travel", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("vel_for_search", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("vel_for_probe", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("probe_max_z", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("probe_max_xy", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("probe_max_latch", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("latch", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("edge_length", hal.HAL_FLOAT, hal.HAL_OUT)

        self.halcomp["vel_for_travel"] = self.spbtn_vel_for_travel.get_value()
        self.halcomp["vel_for_search"] = self.spbtn_vel_for_search.get_value()
        self.halcomp["vel_for_probe"] = self.spbtn_vel_for_probe.get_value()
        self.halcomp["probe_max_z"] = self.spbtn_probe_max_z.get_value()
        self.halcomp["probe_max_xy"] = self.spbtn_probe_max_xy.get_value()
        self.halcomp["probe_max_latch"] = self.spbtn_probe_max_latch.get_value()
        self.halcomp["latch"] = self.spbtn_latch.get_value()
        self.halcomp["edge_length"] = self.spbtn_edge_length.get_value()


        # create the pins for touchplate/touchprobe
        self.halcomp.newpin("clearence_auto", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("chk_use_popup_style", hal.HAL_BIT, hal.HAL_OUT)
        self.halcomp.newpin("probe_number", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("tp_z_full_thickness", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("tp_z_thickness", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("tp_XY_thickness", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("chk_use_touch_plate", hal.HAL_BIT, hal.HAL_OUT)


        self.halcomp["chk_use_touch_plate"] = self.chk_use_touch_plate.get_active()
        self.hal_led_use_touch_plate.hal_pin.set(self.chk_use_touch_plate.get_active())

        self._init_touchplate_and_probe_data()


    # --------------------------
    #
    # Read the ini file config [TOUCH_DEVICE] section
    #
    # --------------------------
    def _init_touchplate_and_probe_data(self):
        chk_use_popup_style = self.inifile.find("TOUCH_DEVICE", "POPUP_STYLE")
        probe_number = self.inifile.find("TOUCH_DEVICE", "PROBE_NUMBER")
        tp_z_full_thickness = self.inifile.find("TOUCH_DEVICE", "PLATE_Z_FULL_THICKNESS")
        tp_z_thickness = self.inifile.find("TOUCH_DEVICE", "PLATE_Z_THICKNESS")
        tp_XY_thickness = self.inifile.find("TOUCH_DEVICE", "PLATE_XY_THICKNESS")

        if (
            chk_use_popup_style is None
            or probe_number is None
            or tp_z_full_thickness is None
            or tp_z_thickness is None
            or tp_XY_thickness is None
           ):

            message   = _("Invalidate TOUCH_DEVICE")
            secondary = _("Please check the TOUCH_DEVICE INI configurations")
            self.error_dialog(message, secondary=secondary)
            return 0
        else:
            self.halcomp["chk_use_popup_style"] = int(chk_use_popup_style)
            self.halcomp["probe_number"] = int(probe_number)
            self.halcomp["tp_z_full_thickness"] = float(tp_z_full_thickness)
            self.halcomp["tp_z_thickness"] = float(tp_z_thickness)
            self.halcomp["tp_XY_thickness"] = float(tp_XY_thickness)


    # --------------------------
    #
    # Checkbox select option
    #
    # --------------------------
    # Manage usage touchplate or 3D-PROBE
    def on_chk_use_touch_plate_toggled(self, gtkcheckbutton, data=None):
        self.halcomp["chk_use_touch_plate"] = gtkcheckbutton.get_active()
        self.hal_led_use_touch_plate.hal_pin.set(gtkcheckbutton.get_active())
        self.prefs.putpref("chk_use_touch_plate", gtkcheckbutton.get_active(), bool)


    # --------------------------
    #
    # Spinbox Settings Buttons
    #
    # --------------------------

    def on_spbtn_vel_for_travel_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("vel_for_travel", gtkspinbutton, data)

    def on_spbtn_vel_for_travel_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("vel_for_travel", gtkspinbutton, data)

    def on_spbtn_vel_for_search_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("vel_for_search", gtkspinbutton, data)

    def on_spbtn_vel_for_search_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("vel_for_search", gtkspinbutton, data)

    def on_spbtn_vel_for_probe_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("vel_for_probe", gtkspinbutton, data)

    def on_spbtn_vel_for_probe_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("vel_for_probe", gtkspinbutton, data)

    def on_spbtn_probe_max_z_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("probe_max_z", gtkspinbutton, data)

    def on_spbtn_probe_max_z_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("probe_max_z", gtkspinbutton, data)

    def on_spbtn_probe_max_xy_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("probe_max_xy", gtkspinbutton, data)

    def on_spbtn_probe_max_xy_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("probe_max_xy", gtkspinbutton, data)

    def on_spbtn_probe_max_latch_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("probe_max_latch", gtkspinbutton, data)

    def on_spbtn_probe_max_latch_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("probe_max_latch", gtkspinbutton, data)

    def on_spbtn_latch_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("latch", gtkspinbutton, data)

    def on_spbtn_latch_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("latch", gtkspinbutton, data)

    def on_spbtn_edge_length_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("edge_length", gtkspinbutton, data)

    def on_spbtn_edge_length_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("edge_length", gtkspinbutton, data)
