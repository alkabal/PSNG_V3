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

        # connect the frame for allow to inhibit
        self.frm_measure_angle = self.builder.get_object("frm_measure_angle")

        # make the spinbox button
        self.spbtn_offs_angle = self.builder.get_object("spbtn_offs_angle")

        # make the Tickbox
        self.chk_use_auto_rott = self.builder.get_object("chk_use_auto_rott")

        # make the LED
        self.hal_led_use_auto_rott = self.builder.get_object("hal_led_use_auto_rott")

        # make the pins hal
        self.halcomp.newpin("offs_angle", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("offs_angle_active", hal.HAL_BIT, hal.HAL_OUT)
        self.halcomp.newpin("chk_use_auto_rott", hal.HAL_BIT, hal.HAL_OUT)


        # load value regarding to the pref saved
        if self.prefs.getpref("chk_use_auto_rott", False, bool) == 1 :
            self.spbtn_offs_angle.set_value(self.prefs.getpref("offs_angle", 0.0, float))
            self.halcomp["offs_angle"] = self.spbtn_offs_angle.get_value()
            self.chk_use_auto_rott.set_active(1)
            self.halcomp["chk_use_auto_rott"] = 1
            self.hal_led_use_auto_rott.set_property("on_color","blue")
            self.hal_led_use_auto_rott.hal_pin.set(self.halcomp["chk_use_auto_rott"])
            self.frm_measure_angle.set_sensitive(False)
        else:
            self.frm_measure_angle.set_sensitive(True)

    # --------------------------
    #
    # Checkbox select option
    #
    # --------------------------
    def on_chk_use_auto_rott_toggled(self, gtkcheckbutton, data=None):
        self.halcomp["chk_use_auto_rott"] = gtkcheckbutton.get_active()
        self.prefs.putpref("chk_use_auto_rott", self.halcomp["chk_use_auto_rott"], bool)

        if gtkcheckbutton.get_active():
            self.frm_measure_angle.set_sensitive(False)
            self.add_history_text("Auto rotation is activated")
            self.halcomp["offs_angle"] = self.spbtn_offs_angle.get_value()
            self.prefs.putpref("offs_angle", self.halcomp["offs_angle"], float)
            if self.halcomp["offs_angle"] == self.spbtn_offs_angle.get_value():
               self.hal_led_use_auto_rott.set_property("on_color","blue")
               self.hal_led_use_auto_rott.hal_pin.set(1)
            else:
                self.hal_led_use_auto_rott.set_property("on_color","orange")
                self.hal_led_use_auto_rott.hal_pin.set(1)
        else:
            self.frm_measure_angle.set_sensitive(True)
            self.add_history_text("Auto rotation is not activated")
            if self.halcomp["offs_angle_active"] == 1 and self.halcomp["offs_angle"] == self.spbtn_offs_angle.get_value():
                self.hal_led_use_auto_rott.set_property("on_color","green")
                self.hal_led_use_auto_rott.hal_pin.set(1)
            elif self.halcomp["offs_angle_active"] == 1 and self.halcomp["offs_angle"] != self.spbtn_offs_angle.get_value():
                self.hal_led_use_auto_rott.set_property("on_color","red")
                self.hal_led_use_auto_rott.hal_pin.set(1)
            else:
                self.halcomp["offs_angle"] = 0
                self.prefs.putpref("offs_angle", 0, float)
                #self.halcomp["offs_angle_active"] = 0
                self.hal_led_use_auto_rott.hal_pin.set(0)


    # --------------------------
    #
    # Spinbox entry editable
    #
    # --------------------------
    def on_spbtn_offs_angle_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("offs_angle", gtkspinbutton, data)
        if self.halcomp["chk_use_auto_rott"] == 1 and self.halcomp["offs_angle"] == self.spbtn_offs_angle.get_value():
            self.hal_led_use_auto_rott.set_property("on_color","blue")
            self.hal_led_use_auto_rott.hal_pin.set(1)
        elif self.halcomp["chk_use_auto_rott"] == 1 and self.halcomp["offs_angle"] != self.spbtn_offs_angle.get_value():
            self.halcomp["offs_angle"] = self.spbtn_offs_angle.get_value()
            self.hal_led_use_auto_rott.set_property("on_color","pink")
            self.hal_led_use_auto_rott.hal_pin.set(1)
        elif self.halcomp["offs_angle_active"] == 1 and self.halcomp["offs_angle"] == self.spbtn_offs_angle.get_value():
            self.hal_led_use_auto_rott.set_property("on_color","green")
            self.hal_led_use_auto_rott.hal_pin.set(1)
        #elif self.halcomp["offs_angle_active"] == 1 and self.halcomp["offs_angle"] != self.spbtn_offs_angle.get_value():
        elif self.halcomp["offs_angle"] != self.spbtn_offs_angle.get_value():
            self.hal_led_use_auto_rott.set_property("on_color","red")
            self.hal_led_use_auto_rott.hal_pin.set(1)
        elif self.halcomp["offs_angle_active"] == 0 and self.halcomp["chk_use_auto_rott"] == 0 and self.halcomp["offs_angle"] == 0:
            self.hal_led_use_auto_rott.hal_pin.set(0)
        else:
            self.hal_led_use_auto_rott.set_property("on_color","yellow")
            self.hal_led_use_auto_rott.hal_pin.set(1)

    def on_spbtn_offs_angle_value_changed(self, gtkspinbutton, data=None):
        if self.halcomp["chk_use_auto_rott"] == 1 and self.halcomp["offs_angle"] == self.spbtn_offs_angle.get_value():
            self.hal_led_use_auto_rott.set_property("on_color","blue")
            self.hal_led_use_auto_rott.hal_pin.set(1)
        elif self.halcomp["chk_use_auto_rott"] == 1 and self.halcomp["offs_angle"] != self.spbtn_offs_angle.get_value():
            self.halcomp["offs_angle"] = self.spbtn_offs_angle.get_value()
            self.hal_led_use_auto_rott.set_property("on_color","pink")
            self.hal_led_use_auto_rott.hal_pin.set(1)
        elif self.halcomp["offs_angle_active"] == 1 and self.halcomp["offs_angle"] == self.spbtn_offs_angle.get_value():
            self.hal_led_use_auto_rott.set_property("on_color","green")
            self.hal_led_use_auto_rott.hal_pin.set(1)
        #elif self.halcomp["offs_angle_active"] == 1 and self.halcomp["offs_angle"] != self.spbtn_offs_angle.get_value():
        elif self.halcomp["offs_angle"] != self.spbtn_offs_angle.get_value():
            self.hal_led_use_auto_rott.set_property("on_color","red")
            self.hal_led_use_auto_rott.hal_pin.set(1)
        elif self.halcomp["offs_angle_active"] == 0 and self.halcomp["chk_use_auto_rott"] == 0 and self.halcomp["offs_angle"] == 0:
            self.hal_led_use_auto_rott.hal_pin.set(0)
        else:
            self.hal_led_use_auto_rott.set_property("on_color","yellow")
            self.hal_led_use_auto_rott.hal_pin.set(1)


    # --------------------------
    #
    # button pressed set angle manually
    #
    # --------------------------
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_set_angle_released(self, gtkbutton, data=None):
        self.halcomp["offs_angle"] = self.spbtn_offs_angle.get_value()
        self.prefs.putpref("offs_angle", self.halcomp["offs_angle"],  float)

        if self.halcomp["offs_angle"] == 0:
            if self.halcomp["chk_use_auto_rott"] == 1:
                if self.halcomp["offs_angle"] == self.spbtn_offs_angle.get_value():
                   self.hal_led_use_auto_rott.set_property("on_color","blue")
                   self.hal_led_use_auto_rott.hal_pin.set(1)
                else:
                    self.hal_led_use_auto_rott.set_property("on_color","orange")
                    self.hal_led_use_auto_rott.hal_pin.set(1)
            else:
                self.hal_led_use_auto_rott.hal_pin.set(0)
                self.halcomp["offs_angle_active"] = 0
                self.add_history_text("ANGLE_OFFSET G10 L2 P0 Rx VALUE RESETED TO 0")

        else:
            if self.halcomp["chk_use_auto_rott"] == 1:
                if self.halcomp["offs_angle"] == self.spbtn_offs_angle.get_value():
                   self.hal_led_use_auto_rott.set_property("on_color","blue")
                else:
                    self.hal_led_use_auto_rott.set_property("on_color","orange")
            else:
                if self.halcomp["offs_angle"] == self.spbtn_offs_angle.get_value():
                   self.hal_led_use_auto_rott.set_property("on_color","green")
                else:
                    self.hal_led_use_auto_rott.set_property("on_color","orange")
            self.hal_led_use_auto_rott.hal_pin.set(1)
            self.halcomp["offs_angle_active"] = 1
            self.add_history_text("ANGLE_OFFSET SET G10 L2 P0 R%.4f" % (self.halcomp["offs_angle"]))

        # now we can apply the offset correctly
        s = "G10 L2 P0 R%s" % (self.halcomp["offs_angle"])
        if self.gcode(s) == -1:
            return


    # --------------------------
    #
    # Button probe rotation
    #
    # --------------------------
    # button pressed angle_xp
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_angle_xp_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
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
            self.on_btn_set_angle_released()

        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self._work_in_progress = 0


    # button pressed angle_ym
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_angle_ym_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
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
            self.on_btn_set_angle_released()

        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self._work_in_progress = 0


    # button pressed angle_yp
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_angle_yp_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
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
            self.on_btn_set_angle_released()

        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self._work_in_progress = 0


    # button pressed angle_xm
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_angle_xm_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
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
            self.on_btn_set_angle_released()

        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self._work_in_progress = 0
