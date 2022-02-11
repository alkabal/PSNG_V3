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

import math
import time

class ProbeScreenRotation(ProbeScreenBase):
    # --------------------------
    #
    #  INIT
    #
    # --------------------------
    def __init__(self, halcomp, builder, useropts):
        super(ProbeScreenRotation, self).__init__(halcomp, builder, useropts)

        self.spbtn_offs_angle = self.builder.get_object("spbtn_offs_angle")
        self.chk_use_auto_rott = self.builder.get_object("chk_use_auto_rott")

        self.spbtn_offs_angle.set_value(self.prefs.getpref("offs_angle", 0.0, float))
        self.chk_use_auto_rott.set_active(self.prefs.getpref("chk_use_auto_rott", False, bool))

        self.halcomp.newpin("offs_angle", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("chk_use_auto_rott", hal.HAL_BIT, hal.HAL_OUT)

        self.halcomp["offs_angle"] = self.spbtn_offs_angle.get_value()
        self.halcomp["chk_use_auto_rott"] = self.chk_use_auto_rott.get_active()

        self.hal_led_use_auto_rott = self.builder.get_object("hal_led_use_auto_rott")
        self.hal_led_use_auto_rott.hal_pin.set(self.chk_use_auto_rott.get_active())

    # --------------------------
    #
    # Checkbox select option
    #
    # --------------------------
    def on_chk_use_auto_rott_toggled(self, gtkcheckbutton, data=None):
        self.halcomp["chk_use_auto_rott"] = gtkcheckbutton.get_active()
        self.hal_led_use_auto_rott.hal_pin.set(gtkcheckbutton.get_active())
        self.prefs.putpref("chk_use_auto_rott", gtkcheckbutton.get_active(), bool)


    # --------------------------
    #
    # Spinbox entry editable
    #
    # --------------------------
    def on_spbtn_offs_angle_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("offs_angle", gtkspinbutton, data)

    def on_spbtn_offs_angle_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("offs_angle", gtkspinbutton, data)


    # --------------------------
    #
    # Rotate Buttons
    #
    # --------------------------

    # button pressed set angle manually
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_set_angle_released(self, gtkbutton, data=None):
        self.rotate_coord_system(self.spbtn_offs_angle.get_value())
        self.work_in_progress = 0


    # button pressed angle_xp
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_angle_xp_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"] == True:
            xcres = float(a[0]) + self.halcomp["tp_XY_thickness"] + (0.5 * tooldiameter)
        else:
            xcres = float(a[0]) + (0.5 * tooldiameter)

        # move to calculated point
        s = """G91
        G1 Y%f
        G90""" % (self.halcomp["edge_length"])
        if self.gcode(s) == -1:
            return

        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"] == True:
            xpres = float(a[0]) + self.halcomp["tp_XY_thickness"] + (0.5 * tooldiameter)
        else:
            xpres = float(a[0]) + (0.5 * tooldiameter)
        alfa = math.degrees(math.atan2(xcres - xpres, self.halcomp["edge_length"]))

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 X%f" % (xpres)
        if self.gcode(s) == -1:
            return

        # save and show the probed point
        self.spbtn_offs_angle.set_value(alfa)
        self.add_history_text("Probed_angle_offset = %.4f" % (alfa))
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XcXpA",
            xc=xcres,
            xp=xpres,
            a=alfa,
        )

        # Optional auto zero selectable from gui
        if self.chk_use_auto_rott.get_active():
            self.rotate_coord_system(alfa)

        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self.work_in_progress = 0


    # button pressed angle_ym
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_angle_ym_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # Start psng_yminus.ngc load var fromm hal
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"] == True:
            ycres = float(a[1]) - self.halcomp["tp_XY_thickness"] - (0.5 * tooldiameter)
        else:
            ycres = float(a[1]) - (0.5 * tooldiameter)

        # move to calculated point
        s = """G91
        G1 X%f
        G90""" % (self.halcomp["edge_length"])
        if self.gcode(s) == -1:
            return

        # Start psng_yminus.ngc load var fromm hal
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"] == True:
            ymres = float(a[1]) - self.halcomp["tp_XY_thickness"] - (0.5 * tooldiameter)
        else:
            ymres = float(a[1]) - (0.5 * tooldiameter)
        alfa = math.degrees(math.atan2(ycres - ymres, self.halcomp["edge_length"]))

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 Y%f" % (ymres)
        if self.gcode(s) == -1:
            return

        # save and show the probed point
        self.spbtn_offs_angle.set_value(alfa)
        self.add_history_text("Probed_angle_offset = %.4f" % (alfa))
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "YmYcA",
            ym=ymres,
            yc=ycres,
            a=alfa,
        )

        # Optional auto zero selectable from gui
        if self.chk_use_auto_rott.get_active():
            self.rotate_coord_system(alfa)

        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self.work_in_progress = 0


    # button pressed angle_yp
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_angle_yp_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"] == True:
            ycres = float(a[1]) + self.halcomp["tp_XY_thickness"] + (0.5 * tooldiameter)
        else:
            ycres = float(a[1]) + (0.5 * tooldiameter)

        # move to calculated point
        s = """G91
        G1 X-%f
        G90""" % (self.halcomp["edge_length"])
        if self.gcode(s) == -1:
            return

        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"] == True:
            ypres = float(a[1]) + self.halcomp["tp_XY_thickness"] + (0.5 * tooldiameter)
        else:
            ypres = float(a[1]) + (0.5 * tooldiameter)
        alfa = math.degrees(math.atan2(ypres - ycres, self.halcomp["edge_length"]))

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 Y%f" % (ypres)
        if self.gcode(s) == -1:
            return

        # save and show the probed point
        self.spbtn_offs_angle.set_value(alfa)
        self.add_history_text("Probed_angle_offset = %.4f" % (alfa))
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "YcYpA",
            yc=ycres,
            yp=ypres,
            a=alfa,
        )

        # Optional auto zero selectable from gui
        if self.chk_use_auto_rott.get_active():
            self.rotate_coord_system(alfa)

        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self.work_in_progress = 0


    # button pressed angle_xm
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_angle_xm_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"] == True:
            xcres = float(a[0]) - self.halcomp["tp_XY_thickness"] - (0.5 * tooldiameter)
        else:
            xcres = float(a[0]) - (0.5 * tooldiameter)

        # move to calculated point
        s = """G91
        G1 Y-%f
        G90""" % (self.halcomp["edge_length"])
        if self.gcode(s) == -1:
            return

        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"] == True:
            xmres = float(a[0]) - self.halcomp["tp_XY_thickness"] - (0.5 * tooldiameter)
        else:
            xmres = float(a[0]) - (0.5 * tooldiameter)
        alfa = math.degrees(math.atan2(xcres - xmres, self.halcomp["edge_length"]))

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 X%f" % (xmres)
        if self.gcode(s) == -1:
            return

        # save and show the probed point
        self.spbtn_offs_angle.set_value(alfa)
        self.add_history_text("Probed_angle_offset = %.4f" % (alfa))
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmXcA",
            xm=xmres,
            xc=xcres,
            a=alfa,
        )

        # Optional auto zero selectable from gui
        if self.chk_use_auto_rott.get_active():
            self.rotate_coord_system(alfa)

        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self.work_in_progress = 0

    # --------------------------
    #
    # Apply the rotation offset
    #
    # --------------------------
    def rotate_coord_system(self, alfa=0.0):
            s = "G10 L2 P0"
            if self.halcomp["chk_use_auto_zero_offset_box"]:
                s += " X%s" % (self.halcomp["offs_x"])
                s += " Y%s" % (self.halcomp["offs_y"])
            else:
                self.stat.poll()   # before using some self value from linuxcnc we need to poll
                x = self.stat.position[0]
                y = self.stat.position[1]
                s += " X%s" % (x)
                s += " Y%s" % (y)
            s += " R%s" % (alfa)
            if self.gcode(s) == -1:
                return
            self.add_history_text("offset_angle_applyed = %.4f" % (a))
            #self.vcp_reload()
            #time.sleep(1)
