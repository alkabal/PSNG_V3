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

        if self.inifile.find("TRAJ", "LINEAR_UNITS") not in ["metric", "mm"]:
            # default values for inches
            tup = (20.0, 2.0, 0.5, 1.0, 0.1, 0.125, 1.0, 1.25)
        else:
            tup = (300.0, 10.0, 3.0, 1.0, 0.5, 2.0, 5.0, 5.0)

        # make the spinbox button
        self.spbtn_vel_for_travel = self.builder.get_object("spbtn_vel_for_travel")
        self.spbtn_vel_for_search = self.builder.get_object("spbtn_vel_for_search")
        self.spbtn_vel_for_probe = self.builder.get_object("spbtn_vel_for_probe")
        self.spbtn_probe_max_xy = self.builder.get_object("spbtn_probe_max_xy")
        self.spbtn_latch_probed = self.builder.get_object("spbtn_latch_probed")
        self.spbtn_latch = self.builder.get_object("spbtn_latch")
        self.spbtn_edge_length = self.builder.get_object("spbtn_edge_length")

        # make the Tickbox
        self.chk_use_touch_plate = self.builder.get_object("chk_use_touch_plate")

        # make the LED
        self.hal_led_use_touch_plate = self.builder.get_object("hal_led_use_touch_plate")

        # make the pins hal
        self.halcomp.newpin("chk_use_popup_style_psng", hal.HAL_BIT, hal.HAL_OUT)
        self.halcomp.newpin("psng_vel_for_travel", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("psng_vel_for_search", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("psng_vel_for_probe", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("psng_probe_max_xy", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("psng_latch_probed", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("psng_latch", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("psng_edge_length", hal.HAL_FLOAT, hal.HAL_OUT)

        # make the pins hal for touchplate/touchprobe
        self.halcomp.newpin("chk_use_touch_plate", hal.HAL_BIT, hal.HAL_OUT)
        #self.halcomp.newpin("z_clearence_auto", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("psng_probe_number", hal.HAL_S32, hal.HAL_OUT)
        self.halcomp.newpin("psng_tp_z_full_thickness", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("psng_tp_z_thickness", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("psng_tp_xy_thickness", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("psng_table_clearence", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("psng_table_override", hal.HAL_FLOAT, hal.HAL_OUT)


        ## load value regarding to the pref saved
        #self.spbtn_vel_for_search.set_value(self.prefs.getpref("vel_for_search", tup[0], float))
        #self.spbtn_vel_for_probe.set_value(self.prefs.getpref("vel_for_probe", tup[1], float))
        #self.spbtn_vel_for_travel.set_value(self.prefs.getpref("vel_for_travel", tup[2], float))
        #self.spbtn_latch.set_value(self.prefs.getpref("latch", tup[4], float))
        #self.spbtn_latch_probed.set_value(self.prefs.getpref("latch_probed", tup[5], float))
        #self.spbtn_probe_max_xy.set_value(self.prefs.getpref("probe_max_xy", tup[6], float))
        #self.spbtn_edge_length.set_value(self.prefs.getpref("edge_length", tup[7], float))
        # load value regarding to the pref saved
        self.spbtn_vel_for_search.set_value(self.prefs.getpref("psng_vel_for_search", False, float))
        self.spbtn_vel_for_probe.set_value(self.prefs.getpref("psng_vel_for_probe", False, float))
        self.spbtn_vel_for_travel.set_value(self.prefs.getpref("psng_vel_for_travel", False, float))
        self.spbtn_probe_max_xy.set_value(self.prefs.getpref("psng_probe_max_xy", False, float))
        self.spbtn_latch_probed.set_value(self.prefs.getpref("psng_latch_probed", False, float))
        self.spbtn_latch.set_value(self.prefs.getpref("psng_latch", False, float))
        self.spbtn_edge_length.set_value(self.prefs.getpref("psng_edge_length", False, float))

        self.halcomp["psng_vel_for_search"] = self.spbtn_vel_for_search.get_value()
        self.halcomp["psng_vel_for_probe"] = self.spbtn_vel_for_probe.get_value()
        self.halcomp["psng_vel_for_travel"] = self.spbtn_vel_for_travel.get_value()
        self.halcomp["psng_probe_max_xy"] = self.spbtn_probe_max_xy.get_value()
        self.halcomp["psng_latch_probed"] = self.spbtn_latch_probed.get_value()
        self.halcomp["psng_latch"] = self.spbtn_latch.get_value()
        self.halcomp["psng_edge_length"] = self.spbtn_edge_length.get_value()

        if self.prefs.getpref("chk_use_touch_plate", False, bool):
            self.chk_use_touch_plate.set_active(1)
            self.halcomp["chk_use_touch_plate"] = 1
            self.hal_led_use_touch_plate.hal_pin.set(1)


        # load value regarding to ini file
        self._init_touchplate_and_probe_data()


    # --------------------------
    #
    # Read the ini file config [TOUCH_DEVICE] section
    #
    # --------------------------
    def _init_touchplate_and_probe_data(self):
        chk_use_popup_style_psng = self.inifile.find("TOUCH_DEVICE", "POPUP_STYLE")
        psng_probe_number = self.inifile.find("TOUCH_DEVICE", "PROBE_NUMBER")
        tp_z_full_thickness = self.inifile.find("TOUCH_DEVICE", "PLATE_Z_FULL_THICKNESS")
        tp_z_thickness = self.inifile.find("TOUCH_DEVICE", "PLATE_Z_THICKNESS")
        tp_xy_thickness = self.inifile.find("TOUCH_DEVICE", "PLATE_XY_THICKNESS")
        psng_table_clearence = self.inifile.find("TOUCH_DEVICE", "TABLE_CLEARENCE")
        psng_table_override = self.inifile.find("TOUCH_DEVICE", "TABLE_OVERRIDE")

        if (
            chk_use_popup_style_psng is None
            or psng_probe_number is None
            or tp_z_full_thickness is None
            or tp_z_thickness is None
            or tp_xy_thickness is None
            or psng_table_clearence is None
            or psng_table_override is None
           ):

            self.warning_dialog("Invalidate TOUCH_DEVICE", "Please check the TOUCH_DEVICE INI configurations")
            return 0
        else:
            self.halcomp["chk_use_popup_style_psng"] = float(chk_use_popup_style_psng)
            self.halcomp["psng_probe_number"] = float(psng_probe_number)
            self.halcomp["psng_tp_z_full_thickness"] = float(tp_z_full_thickness)
            self.halcomp["psng_tp_z_thickness"] = float(tp_z_thickness)
            self.halcomp["psng_tp_xy_thickness"] = float(tp_xy_thickness)
            self.halcomp["psng_table_clearence"] = float(psng_table_clearence)
            self.halcomp["psng_table_override"] = float(psng_table_override)


    # --------------------------
    #
    # Checkbox select option
    #
    # --------------------------
    # Manage usage touchplate or 3D-PROBE
    def on_chk_use_touch_plate_toggled(self, gtkcheckbutton):
        self.halcomp["chk_use_touch_plate"] = gtkcheckbutton.get_active()
        self.hal_led_use_touch_plate.hal_pin.set(self.halcomp["chk_use_touch_plate"])
        self.prefs.putpref("chk_use_touch_plate", self.halcomp["chk_use_touch_plate"], bool)
        if self.halcomp["chk_use_touch_plate"]:
            self.add_history_text("Probing using Touchplate is activated")
        else:
            self.add_history_text("Probing using Touchplate is not activated")


    # --------------------------
    #
    # Spinbox Settings Buttons
    #
    # --------------------------

    def on_spbtn_vel_for_travel_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("psng_vel_for_travel", gtkspinbutton, data)

    def on_spbtn_vel_for_travel_value_changed(self, gtkspinbutton):
        self.on_common_spbtn_value_changed("psng_vel_for_travel", gtkspinbutton)

    def on_spbtn_vel_for_search_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("psng_vel_for_search", gtkspinbutton, data)

    def on_spbtn_vel_for_search_value_changed(self, gtkspinbutton):
        self.on_common_spbtn_value_changed("psng_vel_for_search", gtkspinbutton)

    def on_spbtn_vel_for_probe_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("psng_vel_for_probe", gtkspinbutton, data)

    def on_spbtn_vel_for_probe_value_changed(self, gtkspinbutton):
        self.on_common_spbtn_value_changed("psng_vel_for_probe", gtkspinbutton)

    def on_spbtn_probe_max_xy_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("psng_probe_max_xy", gtkspinbutton, data)

    def on_spbtn_probe_max_xy_value_changed(self, gtkspinbutton):
        self.on_common_spbtn_value_changed("psng_probe_max_xy", gtkspinbutton)

    def on_spbtn_latch_probed_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("psng_latch_probed", gtkspinbutton, data)

    def on_spbtn_latch_probed_value_changed(self, gtkspinbutton):
        self.on_common_spbtn_value_changed("psng_latch_probed", gtkspinbutton)

    def on_spbtn_latch_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("psng_latch", gtkspinbutton, data)

    def on_spbtn_latch_value_changed(self, gtkspinbutton):
        self.on_common_spbtn_value_changed("psng_latch", gtkspinbutton)

    def on_spbtn_edge_length_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("psng_edge_length", gtkspinbutton, data)

    def on_spbtn_edge_length_value_changed(self, gtkspinbutton):
        self.on_common_spbtn_value_changed("psng_edge_length", gtkspinbutton)


