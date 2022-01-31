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

class ProbeScreenSettings(ProbeScreenBase):
    # --------------------------
    #
    #  INIT
    #
    # --------------------------
    def __init__(self, halcomp, builder, useropts):
        super(ProbeScreenSettings, self).__init__(halcomp, builder, useropts)

        self.spbtn1_vel_for_search = self.builder.get_object("spbtn1_vel_for_search")
        self.spbtn1_vel_for_probe = self.builder.get_object("spbtn1_vel_for_probe")
        self.spbtn1_latch_maxprobe = self.builder.get_object("spbtn1_latch_maxprobe")
        self.spbtn1_latch = self.builder.get_object("spbtn1_latch")
        self.spbtn1_probe_max = self.builder.get_object("spbtn1_probe_max")
        self.spbtn1_edge_length = self.builder.get_object("spbtn1_edge_length")
        self.spbtn1_clearance_xy = self.builder.get_object("spbtn1_clearance_xy")
        self.spbtn1_clearance_z = self.builder.get_object("spbtn1_clearance_z")

        if self.inifile.find("TRAJ", "LINEAR_UNITS") not in ["metric", "mm"]:
            # default values for inches
            tup = (20.0, 2.0, 0.5, 1.0, 0.1, 0.125, 1.0, 1.25)
        else:
            tup = (300.0, 10.0, 3.0, 1.0, 0.5, 2.0, 5.0, 5.0)

        self.spbtn1_vel_for_search.set_value(
            self.prefs.getpref("vel_for_search", tup[0], float)
        )
        self.spbtn1_vel_for_probe.set_value(
            self.prefs.getpref("vel_for_probe", tup[1], float)
        )
        self.spbtn1_latch_maxprobe.set_value(
            self.prefs.getpref("latch_maxprobe", tup[5], float)
        )
        self.spbtn1_latch.set_value(
            self.prefs.getpref("latch", tup[4], float)
        )
        self.spbtn1_probe_max.set_value(
            self.prefs.getpref("probe_max", tup[3], float)
        )
        self.spbtn1_edge_length.set_value(
            self.prefs.getpref("edge_length", tup[7], float)
        )
        self.spbtn1_clearance_xy.set_value(
            self.prefs.getpref("clearance_xy", tup[6], float)
        )
        self.spbtn1_clearance_z.set_value(
            self.prefs.getpref("clearance_z", tup[2], float)
        )

        # create the pins for GUI settings
        self.halcomp.newpin("vel_for_travel", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("vel_for_search", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("vel_for_probe", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("latch_maxprobe", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("latch", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("probe_max", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("edge_length", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("clearance_xy", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("clearance_z", hal.HAL_FLOAT, hal.HAL_OUT)

        self.halcomp["vel_for_search"] = self.spbtn1_vel_for_search.get_value()
        self.halcomp["vel_for_probe"] = self.spbtn1_vel_for_probe.get_value()
        self.halcomp["latch_maxprobe"] = self.spbtn1_latch_maxprobe.get_value()
        self.halcomp["latch"] = self.spbtn1_latch.get_value()
        self.halcomp["probe_max"] = self.spbtn1_probe_max.get_value()
        self.halcomp["edge_length"] = self.spbtn1_edge_length.get_value()
        self.halcomp["clearance_xy"] = self.spbtn1_clearance_xy.get_value()
        self.halcomp["clearance_z"] = self.spbtn1_clearance_z.get_value()


        # create the pins for touchplate/touchprobe
        self.halcomp.newpin("chk_popup_style", hal.HAL_BIT, hal.HAL_IN)
        self.halcomp.newpin("probe_number", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("tp_z_full_thickness", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("tp_z_thickness", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("tp_XY_thickness", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("chk_touch_plate_selected", hal.HAL_BIT, hal.HAL_OUT)

        self.hal_led_touch_plate_selected = self.builder.get_object("hal_led_touch_plate_selected")
        self.chk_touch_plate_selected = self.builder.get_object("chk_touch_plate_selected")

        self.chk_touch_plate_selected.set_active(self.prefs.getpref("chk_touch_plate_selected", False, bool))
        if self.chk_touch_plate_selected.get_active():
            self.halcomp["chk_touch_plate_selected"] = True
            self.hal_led_touch_plate_selected.hal_pin.set(1)
        else:
            self.halcomp["chk_touch_plate_selected"] = False
            self.hal_led_touch_plate_selected.hal_pin.set(0)

        self._init_touchplate_and_probe_data()


    # Read the ini file config [TOOL_SETTER] section
    def _init_touchplate_and_probe_data(self):
        vel_for_travel = self.inifile.find("TOUCH_DEVICE", "VEL_FOR_TRAVEL")
        chk_popup_style = self.inifile.find("TOUCH_DEVICE", "POPUP_STYLE")
        probe_number = self.inifile.find("TOUCH_DEVICE", "PROBE_NUMBER")
        tp_z_full_thickness = self.inifile.find("TOUCH_DEVICE", "PLATE_Z_FULL_THICKNESS")
        tp_z_thickness = self.inifile.find("TOUCH_DEVICE", "PLATE_Z_THICKNESS")
        tp_XY_thickness = self.inifile.find("TOUCH_DEVICE", "PLATE_XY_THICKNESS")

        if (
            vel_for_travel is None
            or chk_popup_style is None
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
            self.halcomp["vel_for_travel"] = float(vel_for_travel)
            self.halcomp["chk_popup_style"] = int(chk_popup_style)
            self.halcomp["probe_number"] = int(probe_number)
            self.halcomp["tp_z_full_thickness"] = float(tp_z_full_thickness)
            self.halcomp["tp_z_thickness"] = float(tp_z_thickness)
            self.halcomp["tp_XY_thickness"] = float(tp_XY_thickness)

    # Manage usage touchplate or 3D-PROBE
    def on_chk_touch_plate_selected_toggled(self, gtkcheckbutton, data=None):
        self.halcomp["chk_touch_plate_selected"] = gtkcheckbutton.get_active()
        self.hal_led_touch_plate_selected.hal_pin.set(gtkcheckbutton.get_active())
        self.prefs.putpref("chk_touch_plate_selected", gtkcheckbutton.get_active(), bool)


    # --------------------------
    #
    # Settings Buttons
    #
    # --------------------------
    def on_spbtn1_vel_for_search_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("vel_for_search", gtkspinbutton, data)

    def on_spbtn1_vel_for_search_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("vel_for_search", gtkspinbutton, data)

    def on_spbtn1_vel_for_probe_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("vel_for_probe", gtkspinbutton, data)

    def on_spbtn1_vel_for_probe_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("vel_for_probe", gtkspinbutton, data)

    def on_spbtn1_latch_maxprobe_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("latch_maxprobe", gtkspinbutton, data)

    def on_spbtn1_latch_maxprobe_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("latch_maxprobe", gtkspinbutton, data)

    def on_spbtn1_latch_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("latch", gtkspinbutton, data)

    def on_spbtn1_latch_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("latch", gtkspinbutton, data)

    def on_spbtn1_probe_max_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("probe_max", gtkspinbutton, data)

    def on_spbtn1_probe_max_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("probe_max", gtkspinbutton, data)

    def on_spbtn1_edge_length_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("edge_length", gtkspinbutton, data)

    def on_spbtn1_edge_length_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("edge_length", gtkspinbutton, data)

    def on_spbtn1_clearance_xy_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("clearance_xy", gtkspinbutton, data)

    def on_spbtn1_clearance_xy_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("clearance_xy", gtkspinbutton, data)

    def on_spbtn1_clearance_z_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("clearance_z", gtkspinbutton, data)

    def on_spbtn1_clearance_z_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("clearance_z", gtkspinbutton, data)
