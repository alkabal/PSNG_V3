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

class ProbeScreenLengthMeasurement(ProbeScreenBase):
    # --------------------------
    #
    #  INIT
    #
    # --------------------------
    def __init__(self, halcomp, builder, useropts):
        super(ProbeScreenLengthMeasurement, self).__init__(halcomp, builder, useropts)

        # create the pins for block height spinbox
        self.spbtn_block_height = self.builder.get_object("spbtn_block_height")
        self.halcomp.newpin("blockheight", hal.HAL_FLOAT, hal.HAL_OUT)

        self.spbtn_block_height.set_value(self.prefs.getpref("blockheight", 0.0, float))
        self.halcomp["blockheight"] = self.spbtn_block_height.get_value()

    # --------------------------
    #
    # Spinbox entry editable block height
    #
    # --------------------------

    # Spinbox for block height with autosave value inside machine pref file
    def on_spbtn_block_height_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("blockheight", gtkspinbutton, data)

    def on_spbtn_block_height_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("blockheight", gtkspinbutton, data)
        # set coordinate system to new origin                                      # think about using or not using if self.halcomp["set_zero"]: for make it optional
        if self.halcomp["chk_set_zero"]:
            s = "G10 L2 P0 Z%s" % (gtkspinbutton.get_value())
            if self.gcode(s) == -1:        # we can't use self.set_zerro("Z") : G10 L2 vs G10 L20
                return
        #self.vcp_reload()


    # --------------------------
    #
    # probe to workpiece buttons Measurement block height
    #
    # --------------------------

    # Down probe to workpiece for measuring it vs Know tool setter height
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_probe_workpiece_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [5]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # Start psng_probe_workpiece
        if self.ocode("o<psng_probe_workpiece> call") == -1:
            return

        # Calculate Z result
        a = self.probed_position_with_offsets()
        pwres = float(a[2])
        if self.halcomp["chk_touch_plate_selected"] == True:
            pwres = pwres - self.halcomp["tp_z_thickness"]
        print("workpieces_height_probed  = ", pwres)
        print("ts_height", self.halcomp["ts_height"])

        # save and show the probed point
        self.spbtn_block_height.set_value(pwres)                                           # this call update automatically the offset for workpiece
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "Z",
            z=pwres,
        )
        if self.ocode("o<backup_restore> call [999]") == -1:
            return


    # --------------------------
    #
    # Length Buttons Distance measurement
    #
    # --------------------------

    # Lx OUT
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_lx_out_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xpres = float(a[0]) + (0.5 * tooldiameter)

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move to calculated point X
        s = "G1 X%f" % (xpres)
        if self.gcode(s) == -1:
            return

        # move Z to probing position
        if self.clearance_z_down() == -1:
            return

        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xmres = float(a[0]) - (0.5 * tooldiameter)

        # find, show calculated point center
        xcres = 0.5 * (xpres + xmres)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmXcXpLx",
            xm=xmres,
            xc=xcres,
            xp=xpres,
            lx=self.length_x(xm=xmres, xp=xpres),
        )

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # go to the new center of X
        s = "G1 X%f" % (xcres)
        if self.gcode(s) == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("X")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # Ly OUT
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_ly_out_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        ypres = float(a[1]) + (0.5 * tooldiameter)

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move to calculated point Y
        s = "G1 Y%f" % (ypres)
        if self.gcode(s) == -1:
            return

        # move Z to probing position
        if self.clearance_z_down() == -1:
            return

        # Start psng_yminus.ngc load var fromm hal
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        ymres = float(a[1]) - (0.5 * tooldiameter)

        # find, show calculated point center
        ycres = 0.5 * (ypres + ymres)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "YmYcYpLy",
            ym=ymres,
            yc=ycres,
            yp=ypres,
            ly=self.length_y(ym=ymres, yp=ypres),
        )

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # go to the new center of Y
        s = "G1 Y%f" % (ycres)
        if self.gcode(s) == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("Y")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return


    # Lx IN
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_lx_in_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xmres = float(a[0]) - (0.5 * tooldiameter)
        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xpres = float(a[0]) + (0.5 * tooldiameter)

        # find, show calculated point center
        xcres = 0.5 * (xmres + xpres)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmXcXpLx",
            xm=xmres,
            xc=xcres,
            xp=xpres,
            lx=self.length_x(xm=xmres, xp=xpres),
        )

        # go to the new center of X
        s = """G1 X%f""" % (xcres)
        if self.gcode(s) == -1:
            return

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("X")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return


    # Ly IN
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_ly_in_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # Start psng_yminus.ngc load var fromm hal
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        ymres = float(a[1]) - (0.5 * tooldiameter)

        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        ypres = float(a[1]) + (0.5 * tooldiameter)

        # find, show calculated point center
        ycres = 0.5 * (ymres + ypres)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "YmYcYpLy",
            ym=ymres,
            yc=ycres,
            yp=ypres,
            ly=self.length_y(ym=ymres, yp=ypres),
        )

        # go to the new center of Y
        s = "G1 Y%f" % (ycres)
        if self.gcode(s) == -1:
            return

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("Y")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return
