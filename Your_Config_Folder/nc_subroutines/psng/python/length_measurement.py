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
        self.spbtn_probe_block_height = self.builder.get_object("spbtn_probe_block_height")
        self.spbtn_probe_table_offset = self.builder.get_object("spbtn_probe_table_offset")

        self.halcomp.newpin("block_height", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("table_offset", hal.HAL_FLOAT, hal.HAL_OUT)

        self.spbtn_probe_block_height.set_value(self.prefs.getpref("block_height", 0.0, float))
        self.halcomp["block_height"] = self.spbtn_probe_block_height.get_value()                  # test ne pas restaurer la valeur dans hal a voir ce qui est mieux

        self.spbtn_probe_table_offset.set_value(self.prefs.getpref("table_offset", 0.0, float))
        self.halcomp["table_offset"] = self.spbtn_probe_table_offset.get_value()



        self.hal_led_use_bed_compensation = self.builder.get_object("hal_led_use_bed_compensation")
        self.chk_use_bed_compensation = self.builder.get_object("chk_use_bed_compensation")
        self.chk_use_bed_compensation.set_active(self.prefs.getpref("chk_use_bed_compensation", False, bool))

        self.halcomp.newpin("chk_use_bed_compensation", hal.HAL_BIT, hal.HAL_OUT)

        self.halcomp["chk_use_bed_compensation"] = self.chk_use_bed_compensation.get_active()
        self.hal_led_use_bed_compensation.hal_pin.set(self.chk_use_bed_compensation.get_active())

        self.test_param = 0

    # --------------------------
    #
    # Checkbox select option
    #
    # --------------------------

    def on_chk_use_bed_compensation_toggled(self, gtkcheckbutton, data=None):
        self.halcomp["chk_use_bed_compensation"] = gtkcheckbutton.get_active()
        self.hal_led_use_bed_compensation.hal_pin.set(gtkcheckbutton.get_active())
        self.prefs.putpref("chk_use_bed_compensation", gtkcheckbutton.get_active(), bool)


    # --------------------------
    #
    # Spinbox for block height with autosave value inside machine pref file
    #
    # --------------------------
    def on_spbtn_probe_block_height_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("block_height", gtkspinbutton, data)
        self.add_history_text("YOU NEED TO APPLY BLOCK_HEIGTH MANUALLY")

    def on_spbtn_probe_block_height_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("block_height", gtkspinbutton, data)

    def on_spbtn_probe_table_offset_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("table_offset", gtkspinbutton, data)
        self.add_history_text("YOU NEED TO APPLY TABLE_OFFSET MANUALLY")

    def on_spbtn_probe_table_offset_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("table_offset", gtkspinbutton, data)


    # --------------------------
    #
    # probe to block_height and table_offset
    #
    # --------------------------

    # button pressed set table_offset manually
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_set_table_offset_released(self, gtkbutton, data=None):
        self.add_history_text("G10 L2 added tableoffset = %.4f" % (self.spbtn_probe_table_offset.get_value()))
        s = "G10 L2 P0 Z%s" % (self.spbtn_probe_table_offset.get_value())
        if self.gcode(s) == -1:
            return
        self.work_in_progress = 0


    # button pressed set block_height manually
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_set_block_height_released(self, gtkbutton, data=None):
        if self.spbtn_probe_block_height.get_value() == 0:
            self.add_history_text("VALUE RESETED TO 0")
            self.test_param = 0
            s = "G92.1"
            if self.gcode(s) == -1:
                return
        else:
            if self.test_param == self.spbtn_probe_block_height.get_value():
                self.add_history_text("VALUE ALREADY CHANGED SO WE RESET BEFORE APPLY AGAIN")
                s = "G92.1"
                if self.gcode(s) == -1:
                    return

            # before using some self value from linuxcnc we need to poll
            self.stat.poll()        # WE NEED TO POLL FOR READ CORRECTLY THE initial_z_position
            initial_z_position = float(Popen('halcmd getp halui.axis.z.pos-relative', shell=True, stdout=PIPE).stdout.read())

            # update test_param for prevent cumulating offset and display info to user
            self.test_param = self.spbtn_probe_block_height.get_value()
            self.add_history_text("g92_sent = %.4f" % (initial_z_position - self.spbtn_probe_block_height.get_value()))

            # now we can apply the offset correctly
            s = "G92 Z%f" % (initial_z_position - self.spbtn_probe_block_height.get_value())
            if self.gcode(s) == -1:
                return
        self.work_in_progress = 0


    # Button pressed compensation probe to table for measuring it and use for calculate tool setter height and can set G10 L20 Z0 if you tick auto zero
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_probe_bed_compensation_released(self, gtkbutton, data=None):

        # ask toolnumber from popup
        if self.spbtn_dialog_with_question() == None:
            self.add_history_text("Bed Compensation Canceled by user")
            return

        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [3]") == -1:
            return

        # Before start bed leveling we need to deactivate the compensation grid
        #self.chk_use_bed_compensation(0)

        # Start psng_probe_table_offset
        self.add_history_text("probing compensation started")
        if self.ocode("o<psng_probe_compensation> call") == -1:
            self.add_history_text("!!! probing compensation failed !!!")
            return

        # save and show the probed point
        self.add_history_text("Probing compensation finshed correctly")

        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self.work_in_progress = 0


    # Button pressed Down probe to table for measuring it for calculate tool setter height and can set G10 L20 Z0 if you tick auto zero
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_probe_table_offset_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0]") == -1:
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
            self.on_btn_set_table_offset_released(ptres)
        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self.work_in_progress = 0


    # Button pressed Down probe to block_height for measuring it vs Know tool setter height
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_probe_block_height_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0]") == -1:
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
            self.on_btn_set_block_height_released(pwres)
        if self.ocode("o<backup_restore> call [999]") == -1:
            return
        self.work_in_progress = 0

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
        if self.ocode("o<psng_load_var> call [0]") == -1:
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
        self.work_in_progress = 0


    # Button pressed Ly OUT
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_ly_out_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0]") == -1:
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
        self.work_in_progress = 0


    # Button pressed Lx IN
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_lx_in_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0]") == -1:
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
        self.work_in_progress = 0


    # Button pressed Ly IN
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_ly_in_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var> call [0]") == -1:
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
        self.work_in_progress = 0
