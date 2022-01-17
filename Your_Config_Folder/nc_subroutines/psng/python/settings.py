#!/usr/bin/env python
#
# Copyright (c) 2015 Serguei Glavatski ( verser  from cnc-club.ru )
# Copyright (c) 2020 Probe Screen NG Developers
# Copyright (c) 2021 Alkabal free fr with different approach
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

import hal

from .base import ProbeScreenBase


class ProbeScreenSettings(ProbeScreenBase):
    # --------------------------
    #
    #  INIT
    #
    # --------------------------
    def __init__(self, halcomp, builder, useropts):
        super(ProbeScreenSettings, self).__init__(halcomp, builder, useropts)

        self.spbtn1_search_vel = self.builder.get_object("spbtn1_search_vel")
        self.spbtn1_probe_vel = self.builder.get_object("spbtn1_probe_vel")
        self.spbtn1_z_clearance = self.builder.get_object("spbtn1_z_clearance")
        self.spbtn1_probe_max = self.builder.get_object("spbtn1_probe_max")
        self.spbtn1_probe_latch = self.builder.get_object("spbtn1_probe_latch")
        self.spbtn1_probe_diam = self.builder.get_object("spbtn1_probe_diam")
        self.spbtn1_xy_clearance = self.builder.get_object("spbtn1_xy_clearance")
        self.spbtn1_edge_length = self.builder.get_object("spbtn1_edge_length")

        if self.inifile.find("TRAJ", "LINEAR_UNITS") not in ["metric", "mm"]:
            # default values for inches
            tup = (20.0, 2.0, 0.5, 1.0, 0.1, 0.125, 1.0, 1.25)
        else:
            tup = (300.0, 10.0, 3.0, 1.0, 0.5, 2.0, 5.0, 5.0)

        self.spbtn1_search_vel.set_value(
            self.prefs.getpref("search_vel", tup[0], float)
        )
        self.spbtn1_probe_vel.set_value(
            self.prefs.getpref("probe_vel", tup[1], float)
        )
        self.spbtn1_z_clearance.set_value(
            self.prefs.getpref("z_clearance", tup[2], float)
        )
        self.spbtn1_probe_max.set_value(
            self.prefs.getpref("probe_max", tup[3], float)
        )
        self.spbtn1_probe_latch.set_value(
            self.prefs.getpref("probe_latch", tup[4], float)
        )
        self.spbtn1_probe_diam.set_value(
            self.prefs.getpref("probe_diam", tup[5], float)
        )
        self.spbtn1_xy_clearance.set_value(
            self.prefs.getpref("xy_clearance", tup[6], float)
        )
        self.spbtn1_edge_length.set_value(
            self.prefs.getpref("edge_length", tup[7], float)
        )

        self.halcomp.newpin("search_vel", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("probe_vel", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("z_clearance", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("probe_max", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("probe_latch", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("probe_diam", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("xy_clearance", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("edge_length", hal.HAL_FLOAT, hal.HAL_OUT)

        self.halcomp["search_vel"] = self.spbtn1_search_vel.get_value()
        self.halcomp["probe_vel"] = self.spbtn1_probe_vel.get_value()
        self.halcomp["z_clearance"] = self.spbtn1_z_clearance.get_value()
        self.halcomp["probe_max"] = self.spbtn1_probe_max.get_value()
        self.halcomp["probe_latch"] = self.spbtn1_probe_latch.get_value()
        self.halcomp["probe_diam"] = self.spbtn1_probe_diam.get_value()
        self.halcomp["xy_clearance"] = self.spbtn1_xy_clearance.get_value()
        self.halcomp["edge_length"] = self.spbtn1_edge_length.get_value()

    # ----------------
    # Settings Buttons
    # ----------------
    def on_spbtn1_search_vel_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("search_vel", gtkspinbutton, data)

    def on_spbtn1_search_vel_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("search_vel", gtkspinbutton, data)

    def on_spbtn1_probe_vel_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("probe_vel", gtkspinbutton, data)

    def on_spbtn1_probe_vel_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("probe_vel", gtkspinbutton, data)

    def on_spbtn1_probe_max_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("probe_max", gtkspinbutton, data)

    def on_spbtn1_probe_max_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("probe_max", gtkspinbutton, data)

    def on_spbtn1_probe_latch_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("probe_latch", gtkspinbutton, data)

    def on_spbtn1_probe_latch_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("probe_latch", gtkspinbutton, data)

    def on_spbtn1_probe_diam_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("probe_diam", gtkspinbutton, data)

    def on_spbtn1_probe_diam_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("probe_diam", gtkspinbutton, data)

    def on_spbtn1_xy_clearance_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("xy_clearance", gtkspinbutton, data)

    def on_spbtn1_xy_clearance_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("xy_clearance", gtkspinbutton, data)

    def on_spbtn1_edge_length_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("edge_length", gtkspinbutton, data)

    def on_spbtn1_edge_length_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("edge_length", gtkspinbutton, data)

    def on_spbtn1_z_clearance_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("z_clearance", gtkspinbutton, data)

    def on_spbtn1_z_clearance_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("z_clearance", gtkspinbutton, data)
