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

        # make the spinbox button
        self.spbtn_probe_block_height = self.builder.get_object("spbtn_probe_block_height")
        self.spbtn_probe_table_offset = self.builder.get_object("spbtn_probe_table_offset")
        self.spbtn_latch_bed_compensation = self.builder.get_object("spbtn_latch_bed_compensation")

        # make the Tickbox
        self.chk_use_bed_compensation = self.builder.get_object("chk_use_bed_compensation")

        # make the LED
        self.hal_led_use_block_height = self.builder.get_object("hal_led_use_block_height")
        self.hal_led_use_table_offset = self.builder.get_object("hal_led_use_table_offset")
        self.hal_led_use_bed_compensation = self.builder.get_object("hal_led_use_bed_compensation")

        # make the pins hal
        self.halcomp.newpin("offs_block_height", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("offs_table_offset", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("offs_block_height_active", hal.HAL_BIT, hal.HAL_OUT)
        self.halcomp.newpin("offs_table_offset_active", hal.HAL_BIT, hal.HAL_OUT)

        self.halcomp.newpin("compensation_xcount", hal.HAL_S32, hal.HAL_OUT)
        self.halcomp.newpin("compensation_ycount", hal.HAL_S32, hal.HAL_OUT)
        self.halcomp.newpin("compensation_xlength", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("compensation_ylength", hal.HAL_FLOAT, hal.HAL_OUT)

        self.halcomp.newpin("latch_bed_compensation", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("chk_use_bed_compensation", hal.HAL_BIT, hal.HAL_OUT)
        self.halcomp.newpin("compensation_active", hal.HAL_BIT, hal.HAL_IN)
        self.halcomp.newpin("compensation_is_ready", hal.HAL_BIT, hal.HAL_IN)


        # load value regarding to the pref saved
        self.spbtn_probe_block_height.set_value(self.prefs.getpref("offs_block_height", 0.0, float))
        self.spbtn_probe_table_offset.set_value(self.prefs.getpref("offs_table_offset", 0.0, float))
        self.chk_use_bed_compensation.set_active(self.prefs.getpref("chk_use_bed_compensation", False, bool))
        self.halcomp["chk_use_bed_compensation"] = self.chk_use_bed_compensation.get_active()
        self.hal_led_use_bed_compensation.hal_pin.set(self.halcomp["chk_use_bed_compensation"])

        #self.halcomp["offs_table_offset"] = self.spbtn_probe_table_offset.get_value()                  # they are not initialized until is necessary
        #self.halcomp["offs_block_height"] = self.spbtn_probe_block_height.get_value()                  # they are not initialized until is necessary

        self.spbtn_latch_bed_compensation.set_value(self.prefs.getpref("latch_bed_compensation", 0.0, float))
        self.halcomp["latch_bed_compensation"] = self.spbtn_latch_bed_compensation.get_value()

        if self.halcomp["chk_use_bed_compensation"] == 1:
            self.spbtn_latch_bed_compensation.set_sensitive(False)
        else:
            self.spbtn_latch_bed_compensation.set_sensitive(True)



    # --------------------------
    #
    # Checkbox select option
    #
    # --------------------------

    def on_chk_use_bed_compensation_toggled(self, gtkcheckbutton, data=None):
        if gtkcheckbutton.get_active() == 1 and self.halcomp["compensation_is_ready"] == 1:
            self.spbtn_latch_bed_compensation.set_sensitive(False)
            self.halcomp["chk_use_bed_compensation"] = 1
            self.hal_led_use_bed_compensation.hal_pin.set(1)
            self.prefs.putpref("chk_use_bed_compensation", 1, bool)
            self.halcomp["latch_bed_compensation"] = self.spbtn_latch_bed_compensation.get_value()
            self.prefs.putpref("latch_bed_compensation", self.halcomp["latch_bed_compensation"], float)
            self.add_history_text("Bed Compensation z-grid-max   = %.4f" % (float(Popen('halcmd getp probe.compensation.z-grid-max', shell=True, stdout=PIPE).stdout.read())))
            self.add_history_text("Bed Compensation z-grid-min   = %.4f" % (float(Popen('halcmd getp probe.compensation.z-grid-min', shell=True, stdout=PIPE).stdout.read())))
            self.add_history_text("Bed Compensation y-grid-end   = %.4f" % (float(Popen('halcmd getp probe.compensation.y-grid-end', shell=True, stdout=PIPE).stdout.read())))
            self.add_history_text("Bed Compensation y-grid-start = %.4f" % (float(Popen('halcmd getp probe.compensation.y-grid-start', shell=True, stdout=PIPE).stdout.read())))
            self.add_history_text("Bed Compensation x-grid-end   = %.4f" % (float(Popen('halcmd getp probe.compensation.x-grid-end', shell=True, stdout=PIPE).stdout.read())))
            self.add_history_text("Bed Compensation x-grid-start = %.4f" % (float(Popen('halcmd getp probe.compensation.x-grid-start', shell=True, stdout=PIPE).stdout.read())))
        elif gtkcheckbutton.get_active() == 1 and self.halcomp["compensation_is_ready"] == 0:
            self.spbtn_latch_bed_compensation.set_sensitive(True)
            self.halcomp["chk_use_bed_compensation"] = 0
            self.hal_led_use_bed_compensation.set_property("on_color","red")
            self.hal_led_use_bed_compensation.hal_pin.set(1)
            self.prefs.putpref("chk_use_bed_compensation", 0, bool)
            self.add_history_text("ERROR : BED COMPENSATION IS NOT READY")
        else:
            self.spbtn_latch_bed_compensation.set_sensitive(True)
            self.halcomp["chk_use_bed_compensation"] = 0
            self.hal_led_use_bed_compensation.hal_pin.set(0)
            self.prefs.putpref("chk_use_bed_compensation", 0, bool)
            self.add_history_text("Bed Compensation STOPPED by user")
            if self.halcomp["compensation_is_ready"] == 0:
                self.add_history_text("ERROR : BED COMPENSATION IS NOT READY")


    # --------------------------
    #
    # Spinbox for block height with autosave value inside machine pref file
    #
    # --------------------------

    def on_spbtn_latch_bed_compensation_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("latch_bed_compensation", gtkspinbutton, data)

    def on_spbtn_latch_bed_compensation_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("latch_bed_compensation", gtkspinbutton, data)
        self.halcomp["latch_bed_compensation"] = gtkspinbutton.get_value()
        self.prefs.putpref("latch_bed_compensation", self.halcomp["latch_bed_compensation"], float)


    def on_spbtn_probe_block_height_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("offs_block_height", gtkspinbutton, data)
        if self.halcomp["offs_block_height_active"] == 0:
            if self.halcomp["offs_block_height"] == 0 and self.spbtn_probe_block_height.get_value() == 0:
                self.hal_led_use_block_height.hal_pin.set(0)
            else:
                self.hal_led_use_block_height.set_property("on_color","pink")
                self.hal_led_use_block_height.hal_pin.set(1)
        elif self.halcomp["offs_block_height"] == self.spbtn_probe_block_height.get_value():
            self.hal_led_use_block_height.set_property("on_color","green")
            self.hal_led_use_block_height.hal_pin.set(1)
        else:
            self.hal_led_use_block_height.set_property("on_color","red")
            self.hal_led_use_block_height.hal_pin.set(1)

    def on_spbtn_probe_block_height_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("offs_block_height", gtkspinbutton, data)
        if self.halcomp["offs_block_height_active"] == 0:
            if self.halcomp["offs_block_height"] == 0 and self.spbtn_probe_block_height.get_value() == 0:
                self.hal_led_use_block_height.hal_pin.set(0)
            else:
                self.hal_led_use_block_height.set_property("on_color","pink")
                self.hal_led_use_block_height.hal_pin.set(1)
        elif self.halcomp["offs_block_height"] == self.spbtn_probe_block_height.get_value():
            self.hal_led_use_block_height.set_property("on_color","green")
            self.hal_led_use_block_height.hal_pin.set(1)
        else:
            self.hal_led_use_block_height.set_property("on_color","red")
            self.hal_led_use_block_height.hal_pin.set(1)

    def on_spbtn_probe_table_offset_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("offs_table_offset", gtkspinbutton, data)
        if self.halcomp["offs_table_offset_active"] == 0:
            if self.halcomp["offs_table_offset"] == 0 and self.spbtn_probe_table_offset.get_value() == 0:
                self.hal_led_use_table_offset.hal_pin.set(0)
            else:
                self.hal_led_use_table_offset.set_property("on_color","pink")
                self.hal_led_use_table_offset.hal_pin.set(1)
        elif self.halcomp["offs_table_offset"] == self.spbtn_probe_table_offset.get_value():
            self.hal_led_use_table_offset.set_property("on_color","green")
            self.hal_led_use_table_offset.hal_pin.set(1)
        else:
            self.hal_led_use_table_offset.set_property("on_color","red")
            self.hal_led_use_table_offset.hal_pin.set(1)

    def on_spbtn_probe_table_offset_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("offs_table_offset", gtkspinbutton, data)
        if self.halcomp["offs_table_offset_active"] == 0:
            if self.halcomp["offs_table_offset"] == 0 and self.spbtn_probe_table_offset.get_value() == 0:
                self.hal_led_use_table_offset.hal_pin.set(0)
            else:
                self.hal_led_use_table_offset.set_property("on_color","pink")
                self.hal_led_use_table_offset.hal_pin.set(1)
        elif self.halcomp["offs_table_offset"] == self.spbtn_probe_table_offset.get_value():
            self.hal_led_use_table_offset.set_property("on_color","green")
            self.hal_led_use_table_offset.hal_pin.set(1)
        else:
            self.hal_led_use_table_offset.set_property("on_color","red")
            self.hal_led_use_table_offset.hal_pin.set(1)


    # --------------------------
    #
    # probe to block_height and table_offset
    #
    # --------------------------

    # Button pressed compensation probe to table for measuring it and use for calculate tool setter height and can set G10 L20 P0 Z0 if you tick auto zero
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_probe_bed_compensation_released(self, gtkbutton, data=None):

        # lock the use if compensation is activated
        if self.halcomp["chk_use_bed_compensation"] == 1:
            self.add_history_text("You need to disable bed compensation before create a new grid")
            return

        # ask grid config from popup
        if self._dialog_spbtn_bed_compensation() == -1:
            self.add_history_text("Grid generation canceled by user")
            return
        else:
            self.add_history_text("Bed Compensation ylength value = %.4f" % (self.halcomp["compensation_ylength"]))
            self.add_history_text("Bed Compensation xlength value = %.4f" % (self.halcomp["compensation_xlength"]))
            self.add_history_text("Bed Compensation ycount value  = %.4f" % (self.halcomp["compensation_ycount"]))
            self.add_history_text("Bed Compensation xcount value  = %.4f" % (self.halcomp["compensation_xcount"]))

        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [1]") == -1:
            return
        if self.ocode("o<psng_hook> call [3]") == -1:
            return

        # Start psng_probe_table_offset
        self.add_history_text("probing compensation started")
        if self.ocode("o<psng_probe_compensation> call") == -1:
            self.add_history_text("!!! probing compensation failed !!!")
            return

        # save and show the probed point
        self.add_history_text("Probing compensation finshed correctly")

        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self._work_in_progress = 0


    # button pressed set table_offset manually
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_set_table_offset_released(self, gtkbutton, data=None):

        if self.spbtn_probe_table_offset.get_value() != 0:
            s = "G10 L2 P0 Z%s" % (self.spbtn_probe_table_offset.get_value())
            if self.gcode(s) == -1:
                return
            self.hal_led_use_table_offset.set_property("on_color","green")
            self.hal_led_use_table_offset.hal_pin.set(1)
            self.halcomp["offs_table_offset"] = self.spbtn_probe_table_offset.get_value()
            self.prefs.putpref("offs_table_offset", self.halcomp["offs_table_offset"], float)
            self.halcomp["offs_table_offset_active"] = 1
            self.add_history_text("TABLE_OFFSET SET G10 L2 P0 Z%.4f" % (self.halcomp["offs_table_offset"]))
        else:
            s = "G10 L2 P0 Z0"
            if self.gcode(s) == -1:
                return
            self.hal_led_use_table_offset.hal_pin.set(0)
            self.halcomp["offs_table_offset"] = 0
            self.prefs.putpref("offs_table_offset", 0, float)
            self.halcomp["offs_table_offset_active"] = 0
            self.add_history_text("TABLE_OFFSET G10 L2 VALUE RESETED TO 0")


    # button pressed set block_height manually
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_set_block_height_released(self, gtkbutton, data=None):
        s = "G92.1"
        if self.gcode(s) == -1:
            return
        if self.spbtn_probe_block_height.get_value() == 0:
            self.hal_led_use_block_height.hal_pin.set(0)
            self.halcomp["offs_block_height"] = 0
            self.prefs.putpref("offs_block_height", 0, float)
            self.halcomp["offs_block_height_active"] = 0
            self.add_history_text("BLOCK_HEIGHT G92 VALUE RESETED TO 0")
        else:
            self.add_history_text("G92 CLEARED BEFORE APPLY NEW OFFSET")

            # before using some self value from linuxcnc we need to poll
            self.stat.poll()        # WE NEED TO POLL FOR READ CORRECTLY THE initial_z_position
            initial_z_position = float(Popen('halcmd getp halui.axis.z.pos-relative', shell=True, stdout=PIPE).stdout.read())

            ## now we can apply the offset correctly
            #if self.halcomp["offs_table_offset_active"] == 0:
            #    s = "G92 Z%f" % (initial_z_position - self.spbtn_probe_block_height.get_value())
            #else:
            #    s = "G92 Z%f" % (initial_z_position - self.spbtn_probe_block_height.get_value() - self.halcomp["offs_table_offset"])   #use hal value for table offset is important because they are not initialized until is necessary
            s = "G92 Z%f" % (initial_z_position - self.spbtn_probe_block_height.get_value())
            if self.gcode(s) == -1:
                return

            # update test_param for prevent cumulating offset and display info to user
            self.hal_led_use_block_height.set_property("on_color","green")
            self.hal_led_use_block_height.hal_pin.set(1)
            self.halcomp["offs_block_height"] = self.spbtn_probe_block_height.get_value()
            self.prefs.putpref("offs_block_height", self.halcomp["offs_block_height"],  float)
            self.halcomp["offs_block_height_active"] = 1
            self.add_history_text("BLOCK_HEIGHT SET G92 Z%.4f" % (initial_z_position - self.halcomp["offs_block_height"]))


    # Button pressed Down probe to table for measuring it for calculate tool setter height and can set G10 L20 P0 Z0 if you tick auto zero
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_probe_table_offset_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [1]") == -1:
            return
        if self.ocode("o<psng_hook> call [3]") == -1:
            return

        # Start psng_probe_table_offset
        if self.ocode("o<psng_probe_table_offset> call") == -1:
            return

        # Calculate result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"] == True:
            ptres = float(a[2]) - self.halcomp["tp_z_full_thickness"]
        else:
            ptres = float(a[2])

        # save and show the probed point
        self.spbtn_probe_table_offset.set_value(ptres)
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "Z",
            z=ptres,
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offset_box"]:
            self.on_btn_set_table_offset_released()
        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self._work_in_progress = 0


    # Button pressed Down probe to block_height for measuring it vs Know tool setter height
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_probe_block_height_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [5]") == -1:
            return

        # Start psng_probe_block_height
        if self.ocode("o<psng_probe_block_height> call") == -1:
            return

        # Calculate result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"] == True:
            pwres = float(a[2]) - self.halcomp["tp_z_thickness"]
        else:
            pwres = float(a[2])

        # save and show the probed point
        self.spbtn_probe_block_height.set_value(pwres)
        self.add_history_text("block_height probe result point = %.4f" % (pwres))
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "Z",
            z=pwres,
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offset_box"]:
            self.on_btn_set_block_height_released()
        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self._work_in_progress = 0

    # --------------------------
    #
    # Length Buttons Distance measurement
    #
    # --------------------------

    # Button pressed Lx OUT
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_lx_out_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # before using some self value from linuxcnc we need to poll
        self.stat.poll()
        initial_x_position = self.stat.position[0]

        # Start psng_start_z_probing_for_diam.ngc
        if self.ocode("o<psng_start_z_probing_for_diam> call [1]") == -1:
            return

#        # Start psng_start_inverse_probing.ngc
#        if self.ocode("o<psng_start_inverse_probing> call [1]") == -1:
#            return

        # move to calculated point X clearance + up Z with latch value
        s = """G91
        G1 X-%f Z%f
        G90""" % (self.halcomp["latch"] + tooldiameter, self.halcomp["latch"])
        if self.gcode(s) == -1:
            return

        # move Z to probing position
        if self.move_probe_z_down() == -1:
            return

        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate result
        a = self.probed_position_with_offsets()
        xpres = float(a[0]) + (0.5 * tooldiameter)

        # move Z temporary away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 X%f" % (initial_x_position)
        if self.gcode(s) == -1:
            return

        # Start psng_start_z_probing_for_diam.ngc
        if self.ocode("o<psng_start_z_probing_for_diam> call") == -1:
            return

#        # Start psng_start_inverse_probing.ngc
#        if self.ocode("o<psng_start_inverse_probing> call [2]") == -1:
#            return

        # move to calculated point X clearance + up Z with latch value
        s = """G91
        G1 X%f Z%f
        G90""" % (self.halcomp["latch"] + tooldiameter, self.halcomp["latch"])
        if self.gcode(s) == -1:
            return

        # move Z to probing position
        if self.move_probe_z_down() == -1:
            return

        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate result
        a = self.probed_position_with_offsets()
        xmres = float(a[0]) - (0.5 * tooldiameter)
        xcres = 0.5 * (xpres + xmres)

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # go to the new center of X
        s = "G1 X%f" % (xcres)
        if self.gcode(s) == -1:
            return

        # show calculated point center
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmXcXpLx",
            xm=xmres,
            xc=xcres,
            xp=xpres,
            lx=self.length_x(xm=xmres, xp=xpres),
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offset_box"]:
            self.set_zero_offset_box("X")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self._work_in_progress = 0


    # Button pressed Ly OUT
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_ly_out_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # before using some self value from linuxcnc we need to poll
        self.stat.poll()
        initial_y_position = self.stat.position[1]

        # Start psng_start_z_probing_for_diam.ngc
        if self.ocode("o<psng_start_z_probing_for_diam> call") == -1:
            return

#        # Start psng_start_inverse_probing.ngc
#        if self.ocode("o<psng_start_inverse_probing> call [3]") == -1:
#            return

        # move to calculated point Y clearance + up Z with latch value
        s = """G91
        G1 Y-%f Z%f
        G90""" % (self.halcomp["latch"] + tooldiameter, self.halcomp["latch"])
        if self.gcode(s) == -1:
            return

        # move Z to probing position
        if self.move_probe_z_down() == -1:
            return

        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate result
        a = self.probed_position_with_offsets()
        ypres = float(a[1]) + (0.5 * tooldiameter)

        # move Z temporary away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 Y%f" % (initial_y_position)
        if self.gcode(s) == -1:
            return

        # Start psng_start_z_probing_for_diam.ngc
        if self.ocode("o<psng_start_z_probing_for_diam> call [4]") == -1:
            return

#        # Start psng_start_inverse_probing.ngc
#        if self.ocode("o<psng_start_inverse_probing> call [4]") == -1:
#            return

        # move to calculated point Y clearance + up Z with latch value
        s = """G91
        G1 Y%f Z%f
        G90""" % (self.halcomp["latch"] + tooldiameter, self.halcomp["latch"])
        if self.gcode(s) == -1:
            return

        # move Z to probing position
        if self.move_probe_z_down() == -1:
            return

        # Start psng_yminus.ngc load var fromm hal
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate result
        a = self.probed_position_with_offsets()
        ymres = float(a[1]) - (0.5 * tooldiameter)
        ycres = 0.5 * (ypres + ymres)

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # go to the new center of Y
        s = "G1 Y%f" % (ycres)
        if self.gcode(s) == -1:
            return

        # show calculated point center
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "YmYcYpLy",
            ym=ymres,
            yc=ycres,
            yp=ypres,
            ly=self.length_y(ym=ymres, yp=ypres),
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offset_box"]:
            self.set_zero_offset_box("Y")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self._work_in_progress = 0


    # Button pressed Lx IN
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_lx_in_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # Start psng_xminus.ngc
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xmres = float(a[0]) - (0.5 * tooldiameter)

        # Start psng_xplus.ngc
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xpres = float(a[0]) + (0.5 * tooldiameter)
        xcres = 0.5 * (xmres + xpres)

        # move X to new center
        s = "G1 X%f" % (xcres)
        if self.gcode(s) == -1:
            return

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # show calculated point center
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmXcXpLx",
            xm=xmres,
            xc=xcres,
            xp=xpres,
            lx=self.length_x(xm=xmres, xp=xpres),
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offset_box"]:
            self.set_zero_offset_box("X")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self._work_in_progress = 0


    # Button pressed Ly IN
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_ly_in_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return

        # Start psng_yminus.ngc
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        ymres = float(a[1]) - (0.5 * tooldiameter)

        # Start psng_yplus.ngc
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        ypres = float(a[1]) + (0.5 * tooldiameter)
        ycres = 0.5 * (ymres + ypres)

        # move to calculated point
        s = "G1 Y%f" % (ycres)
        if self.gcode(s) == -1:
            return

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # show calculated point center
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "YmYcYpLy",
            ym=ymres,
            yc=ycres,
            yp=ypres,
            ly=self.length_y(ym=ymres, yp=ypres),
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offset_box"]:
            self.set_zero_offset_box("Y")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self._work_in_progress = 0


