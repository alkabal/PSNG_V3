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

        # make the spinbox button
        self.spbtn_offs_angle = self.builder.get_object("spbtn_offs_angle")

        # make the Tickbox
        self.chk_use_auto_zero_offs_angle = self.builder.get_object("chk_use_auto_zero_offs_angle")

        # make the LED
        self.hal_led_use_offs_angle = self.builder.get_object("hal_led_use_offs_angle")

        # make the pins hal
        self.halcomp.newpin("offs_angle", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("offs_angle_active", hal.HAL_BIT, hal.HAL_OUT)
        self.halcomp.newpin("chk_use_auto_zero_offs_angle", hal.HAL_BIT, hal.HAL_OUT)

        # After getting value we need to init some of them
        self._init_rotation_data()


    # --------------------------
    #
    # Init value etc
    #
    # --------------------------
    def _init_rotation_data(self):
        # load value regarding to the pref saved
        if self.prefs.getpref("chk_use_auto_zero_offs_angle", False, bool):
            self.spbtn_offs_angle.set_value(self.prefs.getpref("offs_angle", 0.0, float))
            self.halcomp["offs_angle"] = self.spbtn_offs_angle.get_value()
            self.chk_use_auto_zero_offs_angle.set_active(1)
            self.halcomp["chk_use_auto_zero_offs_angle"] = 1
            self.hal_led_use_offs_angle.set_property("on_color","blue")
            self.hal_led_use_offs_angle.hal_pin.set(self.halcomp["chk_use_auto_zero_offs_angle"])
            self.spbtn_offs_angle.set_sensitive(False)
        else:
            self.spbtn_offs_angle.set_value(self.prefs.getpref("offs_angle", 0.0, float))
            self.spbtn_offs_angle.set_sensitive(True)



    # --------------------------
    #
    # Checkbox select option
    #
    # --------------------------
    def on_chk_use_auto_zero_offs_angle_toggled(self, gtkcheckbutton):
        self.halcomp["chk_use_auto_zero_offs_angle"] = gtkcheckbutton.get_active()
        self.prefs.putpref("chk_use_auto_zero_offs_angle", self.halcomp["chk_use_auto_zero_offs_angle"], bool)

        if self.halcomp["chk_use_auto_zero_offs_angle"]:
            self.spbtn_offs_angle.set_sensitive(False)
            self.halcomp["offs_angle"] = self.spbtn_offs_angle.get_value()
            self.prefs.putpref("offs_angle", self.halcomp["offs_angle"], float)
            self.add_history_text("Auto rotation is activated")
                                                                                 # todo check for actual angle applied vs hal for color pink
            if self.halcomp["offs_angle"] == self.spbtn_offs_angle.get_value():
               self.halcomp["offs_angle_active"] = 1
               self.hal_led_use_offs_angle.set_property("on_color","blue")
               self.hal_led_use_offs_angle.hal_pin.set(1)
            else:
                self.halcomp["offs_angle_active"] = 0
                self.hal_led_use_offs_angle.set_property("on_color","orange")
                self.hal_led_use_offs_angle.hal_pin.set(1)
                self.warning_dialog("ANGLE_OFFSET GTK CHECKBUTTON UNKNOW STATUS")
        else:
            self.spbtn_offs_angle.set_sensitive(True)
            self.halcomp["offs_angle"] = 0
            self._set_auto_zero_offset("R")
            self.prefs.putpref("offs_angle", 0, float)
            self.halcomp["offs_angle_active"] = 0
            self.hal_led_use_offs_angle.hal_pin.set(0)
            self.add_history_text("ANGLE_OFFSET G10_L2 P0 Rx VALUE RESETED TO 0")
            self.add_history_text("Auto rotation is not activated")


    # --------------------------
    #
    # Spinbox entry editable
    #
    # --------------------------
    def on_spbtn_offs_angle_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("offs_angle", gtkspinbutton, data)
        if self.halcomp["offs_angle_active"] == 0:
            if self.halcomp["offs_angle"] == 0 and self.spbtn_offs_angle.get_value() == 0:
                self.hal_led_use_offs_angle.hal_pin.set(0)
            else:
                self.hal_led_use_offs_angle.set_property("on_color","pink")
                self.hal_led_use_offs_angle.hal_pin.set(1)
        elif self.halcomp["offs_angle"] == self.spbtn_offs_angle.get_value():
            self.hal_led_use_offs_angle.set_property("on_color","green")
            self.hal_led_use_offs_angle.hal_pin.set(1)
        else:
            self.hal_led_use_offs_angle.set_property("on_color","red")
            self.hal_led_use_offs_angle.hal_pin.set(1)

    def on_spbtn_offs_angle_value_changed(self, gtkspinbutton):
        self.on_common_spbtn_value_changed("offs_angle", gtkspinbutton)
        if self.halcomp["offs_angle_active"] == 0:
            if self.halcomp["offs_angle"] == 0 and self.spbtn_offs_angle.get_value() == 0:
                self.hal_led_use_offs_angle.hal_pin.set(0)
            else:
                self.hal_led_use_offs_angle.set_property("on_color","pink")
                self.hal_led_use_offs_angle.hal_pin.set(1)
        elif self.halcomp["offs_angle"] == self.spbtn_offs_angle.get_value():
            self.hal_led_use_offs_angle.set_property("on_color","green")
            self.hal_led_use_offs_angle.hal_pin.set(1)
        else:
            self.hal_led_use_offs_angle.set_property("on_color","red")
            self.hal_led_use_offs_angle.hal_pin.set(1)


    # --------------------------
    #
    # button pressed set angle manually
    #
    # --------------------------
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_set_angle_released(self, gtkbutton):
        if self.spbtn_offs_angle.get_value() == 0:
            self.hal_led_use_offs_angle.hal_pin.set(0)
            self.halcomp["offs_angle"] = 0
            self._set_auto_zero_offset("R")
            self.halcomp["offs_angle_active"] = 0
            self.prefs.putpref("offs_angle", 0, float)
            self.add_history_text("OFFSET_BOX_ANGLE REMOVED FROM G10_L2")
        else:
            self.hal_led_use_offs_angle.set_property("on_color","green")
            self.hal_led_use_offs_angle.hal_pin.set(1)
            self.halcomp["offs_angle"] = self.spbtn_offs_angle.get_value()
            self._set_auto_zero_offset("R")
            self.halcomp["offs_angle_active"] = 1
            self.prefs.putpref("offs_angle", self.halcomp["offs_angle"], float)
            self.add_history_text("OFFSET_BOX_ANGLE %.4f ADDED TO G10_L2" % (self.halcomp["offs_angle"]))


    # --------------------------
    #
    # Button probe rotation
    #
    # --------------------------
    # button pressed angle_xp
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_angle_xp_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("angle_xp") == -1:
            self.warning_dialog("angle_xp canceled by user !")
            return

        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            xcres = float(a[0]) + self.halcomp["psng_tp_xy_thickness"] + (0.5 * tooldiameter)
        else:
            xcres = float(a[0]) + (0.5 * tooldiameter)

        # move to calculated point
        s = """G91
        G1 Y%f
        G90""" % (self.halcomp["psng_edge_length"])
        if self.gcode(s) == -1:
            return

        # TODO OR NOT MANAGE TO ADD ADDITIONAL <_psng_probe_max_xy>

        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            xpres = float(a[0]) + self.halcomp["psng_tp_xy_thickness"] + (0.5 * tooldiameter)
        else:
            xpres = float(a[0]) + (0.5 * tooldiameter)
        alfa = math.degrees(math.atan2(xcres - xpres, self.halcomp["psng_edge_length"]))

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G90 G1 X%f" % (xpres)
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
        if self.chk_use_auto_zero_offs_angle.get_active():
            self.on_btn_set_angle_released(gtkbutton)

        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0


    # button pressed angle_ym
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_angle_ym_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("angle_ym") == -1:
            self.warning_dialog("angle_ym canceled by user !")
            return

        # Start psng_yminus.ngc load var fromm hal
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            ycres = float(a[1]) - self.halcomp["psng_tp_xy_thickness"] - (0.5 * tooldiameter)
        else:
            ycres = float(a[1]) - (0.5 * tooldiameter)

        # move to calculated point
        s = """G91
        G1 X%f
        G90""" % (self.halcomp["psng_edge_length"])
        if self.gcode(s) == -1:
            return

        # TODO OR NOT MANAGE TO ADD ADDITIONAL <_psng_probe_max_xy>

        # Start psng_yminus.ngc load var fromm hal
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            ymres = float(a[1]) - self.halcomp["psng_tp_xy_thickness"] - (0.5 * tooldiameter)
        else:
            ymres = float(a[1]) - (0.5 * tooldiameter)
        alfa = math.degrees(math.atan2(ycres - ymres, self.halcomp["psng_edge_length"]))

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G90 G1 Y%f" % (ymres)
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
        if self.chk_use_auto_zero_offs_angle.get_active():
            self.on_btn_set_angle_released(gtkbutton)

        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0


    # button pressed angle_yp
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_angle_yp_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("angle_yp") == -1:
            self.warning_dialog("angle_yp canceled by user !")
            return

        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            ycres = float(a[1]) + self.halcomp["psng_tp_xy_thickness"] + (0.5 * tooldiameter)
        else:
            ycres = float(a[1]) + (0.5 * tooldiameter)

        # move to calculated point
        s = """G91
        G1 X-%f
        G90""" % (self.halcomp["psng_edge_length"])
        if self.gcode(s) == -1:
            return

        # TODO OR NOT MANAGE TO ADD ADDITIONAL <_psng_probe_max_xy>

        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            ypres = float(a[1]) + self.halcomp["psng_tp_xy_thickness"] + (0.5 * tooldiameter)
        else:
            ypres = float(a[1]) + (0.5 * tooldiameter)
        alfa = math.degrees(math.atan2(ypres - ycres, self.halcomp["psng_edge_length"]))

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G90 G1 Y%f" % (ypres)
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
        if self.chk_use_auto_zero_offs_angle.get_active():
            self.on_btn_set_angle_released(gtkbutton)

        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0


    # button pressed angle_xm
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_angle_xm_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("angle_xm") == -1:
            self.warning_dialog("angle_xm canceled by user !")
            return

        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            xcres = float(a[0]) - self.halcomp["psng_tp_xy_thickness"] - (0.5 * tooldiameter)
        else:
            xcres = float(a[0]) - (0.5 * tooldiameter)

        # move to calculated point
        s = """G91
        G1 Y-%f
        G90""" % (self.halcomp["psng_edge_length"])
        if self.gcode(s) == -1:
            return

        # TODO OR NOT MANAGE TO ADD ADDITIONAL <_psng_probe_max_xy>

        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            xmres = float(a[0]) - self.halcomp["psng_tp_xy_thickness"] - (0.5 * tooldiameter)
        else:
            xmres = float(a[0]) - (0.5 * tooldiameter)
        alfa = math.degrees(math.atan2(xcres - xmres, self.halcomp["psng_edge_length"]))

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G90 G1 X%f" % (xmres)
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
        if self.chk_use_auto_zero_offs_angle.get_active():
            self.on_btn_set_angle_released(gtkbutton)

        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0
