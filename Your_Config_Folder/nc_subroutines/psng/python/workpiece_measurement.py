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

class ProbeScreenWorkpieceMeasurement(ProbeScreenBase):

    # --------------------------
    #
    #  INIT
    #
    # --------------------------
    def __init__(self, halcomp, builder, useropts):
        super(ProbeScreenWorkpieceMeasurement, self).__init__(halcomp, builder, useropts)

    # --------------------------
    #
    #  Command buttons Measurement common
    #
    # --------------------------

    # Button pressed X+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_xp_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("xp") == -1:
            self.warning_dialog("xp canceled by user !")
            return

        # Start psng_xplus.ngc
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            xres = float(a[0]) + self.halcomp["psng_tp_xy_thickness"] + (0.5 * tooldiameter)
        else:
            xres = float(a[0]) + (0.5 * tooldiameter)

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 X%f" % (xres)
        if self.gcode(s) == -1:
            return

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XpLx",
            xp=xres,
            lx=self.length_x(xp=xres),
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offs_xyz"]:
            self._set_auto_zero_offset("X")
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0


    # Button pressed Y+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_yp_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("yp") == -1:
            self.warning_dialog("yp canceled by user !")
            return

        # Start psng_yplus.ngc
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            yres = float(a[1]) + self.halcomp["psng_tp_xy_thickness"] + (0.5 * tooldiameter)
        else:
            yres = float(a[1]) + (0.5 * tooldiameter)

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 Y%f" % (yres)
        if self.gcode(s) == -1:
            return

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "YpLy",
            yp=yres,
            ly=self.length_y(yp=yres),
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offs_xyz"]:
            self._set_auto_zero_offset("Y")
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0


    # Button pressed X-
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_xm_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("xm") == -1:
            self.warning_dialog("xm canceled by user !")
            return

        # Start psng_xminus.ngc
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            xres = float(a[0]) - self.halcomp["psng_tp_xy_thickness"] - (0.5 * tooldiameter)
        else:
            xres = float(a[0]) - (0.5 * tooldiameter)

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 X%f" % (xres)
        if self.gcode(s) == -1:
            return

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmLx",
            xm=xres,
            lx=self.length_x(xm=xres),
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offs_xyz"]:
            self._set_auto_zero_offset("X")
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0


    # Button pressed Y-
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_ym_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("ym") == -1:
            self.warning_dialog("ym canceled by user !")
            return

        # Start psng_yminus.ngc
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            yres = float(a[1]) - self.halcomp["psng_tp_xy_thickness"] - (0.5 * tooldiameter)
        else:
            yres = float(a[1]) - (0.5 * tooldiameter)

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 Y%f" % (yres)
        if self.gcode(s) == -1:
            return

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "YmLy",
            ym=yres,
            ly=self.length_y(ym=yres),
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offs_xyz"]:
            self._set_auto_zero_offset("Y")
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0

    # --------------------------
    #
    #  Command buttons Measurement outside
    #
    # --------------------------

    # Corners
    # Move Probe manual under corner 2-3 mm
    # Button pressed X+Y+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_xpyp_out_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("xpyp") == -1:
            self.warning_dialog("xpyp canceled by user !")
            return

        # before using some self value from linuxcnc we need to poll
        self.stat.poll()
        initial_x_position = self.stat.position[0]
        initial_y_position = self.stat.position[1]

        # move to calculated point
        s = """G91
        G1 Y%f
        G90""" % (self.halcomp["psng_edge_length"])
        if self.gcode(s) == -1:
            return

        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            xres = float(a[0]) + self.halcomp["psng_tp_xy_thickness"] + (0.5 * tooldiameter)
        else:
            xres = float(a[0]) + (0.5 * tooldiameter)

        # move to calculated point
        s = "G1 Y%f" % (initial_y_position)
        if self.gcode(s) == -1:
            return

        # move to calculated point
        s = """G91
        G1 X%f
        G90""" % (self.halcomp["psng_edge_length"])
        if self.gcode(s) == -1:
            return

        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            yres = float(a[1]) + self.halcomp["psng_tp_xy_thickness"] + (0.5 * tooldiameter)
        else:
            yres = float(a[1]) + (0.5 * tooldiameter)

        # move to calculated point
        s = "G1 X%f" % (initial_x_position)
        if self.gcode(s) == -1:
            return

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XpLxYpLy",
            xp=xres,
            lx=self.length_x(xp=xres),
            yp=yres,
            ly=self.length_y(yp=yres),
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offs_xyz"]:
            self._set_auto_zero_offset("XY")
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0


    # Button pressed X+Y-
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_xpym_out_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("xpym") == -1:
            self.warning_dialog("xpym canceled by user !")
            return

        # before using some self value from linuxcnc we need to poll
        self.stat.poll()
        initial_x_position = self.stat.position[0]
        initial_y_position = self.stat.position[1]

        # move to calculated point
        s = """G91
        G1 Y-%f
        G90""" % (self.halcomp["psng_edge_length"])
        if self.gcode(s) == -1:
            return

        # Start psng_xplus.ngc
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            xres = float(a[0]) + self.halcomp["psng_tp_xy_thickness"] + (0.5 * tooldiameter)
        else:
            xres = float(a[0]) + (0.5 * tooldiameter)

        # move to calculated point
        s = "G1 Y%f" % (initial_y_position)
        if self.gcode(s) == -1:
            return

        # move to calculated point
        s = """G91
        G1 X%f
        G90""" % (self.halcomp["psng_edge_length"])
        if self.gcode(s) == -1:
            return

        # Start psng_yminus.ngc
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            yres = float(a[1]) - self.halcomp["psng_tp_xy_thickness"] - (0.5 * tooldiameter)
        else:
            yres = float(a[1]) - (0.5 * tooldiameter)

        # move to calculated point
        s = "G1 X%f" % (initial_x_position)
        if self.gcode(s) == -1:
            return

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XpLxYmLy",
            xp=xres,
            lx=self.length_x(xp=xres),
            ym=yres,
            ly=self.length_y(ym=yres),
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offs_xyz"]:
            self._set_auto_zero_offset("XY")
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0


    # Button pressed X-Y+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_xmyp_out_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("xmyp") == -1:
            self.warning_dialog("xmyp canceled by user !")
            return

        # before using some self value from linuxcnc we need to poll
        self.stat.poll()
        initial_x_position = self.stat.position[0]
        initial_y_position = self.stat.position[1]

        # move to calculated point
        s = """G91
        G1 Y%f
        G90""" % (self.halcomp["psng_edge_length"])
        if self.gcode(s) == -1:
            return

        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            xres = float(a[0]) - self.halcomp["psng_tp_xy_thickness"] - (0.5 * tooldiameter)
        else:
            xres = float(a[0]) - (0.5 * tooldiameter)

        # move to calculated point
        s = "G1 Y%f" % (initial_y_position)
        if self.gcode(s) == -1:
            return

        # move to calculated point
        s = """G91
        G1 X-%f
        G90""" % (self.halcomp["psng_edge_length"])
        if self.gcode(s) == -1:
            return

        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            yres = float(a[1]) + self.halcomp["psng_tp_xy_thickness"] + (0.5 * tooldiameter)
        else:
            yres = float(a[1]) + (0.5 * tooldiameter)

        # move to calculated point
        s = "G1 X%f" % (initial_x_position)
        if self.gcode(s) == -1:
            return

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmLxYpLy",
            xm=xres,
            lx=self.length_x(xm=xres),
            yp=yres,
            ly=self.length_y(yp=yres),
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offs_xyz"]:
            self._set_auto_zero_offset("XY")
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0


    # Button pressed X-Y-
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_xmym_out_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("xmym") == -1:
            self.warning_dialog("xmym canceled by user !")
            return

        # before using some self value from linuxcnc we need to poll
        self.stat.poll()
        initial_x_position = self.stat.position[0]
        initial_y_position = self.stat.position[1]

        # move to calculated point
        s = """G91
        G1 Y-%f
        G90""" % (self.halcomp["psng_edge_length"])
        if self.gcode(s) == -1:
            return

        # Start psng_xminus.ngc
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            xres = float(a[0]) - self.halcomp["psng_tp_xy_thickness"] - (0.5 * tooldiameter)
        else:
            xres = float(a[0]) - (0.5 * tooldiameter)

        # move to calculated point
        s = "G1 Y%f" % (initial_y_position)
        if self.gcode(s) == -1:
            return

        # move to calculated point
        s = """G91
        G1 X-%f
        G90""" % (self.halcomp["psng_edge_length"])
        if self.gcode(s) == -1:
            return

        # Start psng_yminus.ngc
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        if self.halcomp["chk_use_touch_plate"]:
            yres = float(a[1]) - self.halcomp["psng_tp_xy_thickness"] - (0.5 * tooldiameter)
        else:
            yres = float(a[1]) - (0.5 * tooldiameter)

        # move to calculated point
        s = "G1 X%f" % (initial_x_position)
        if self.gcode(s) == -1:
            return

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmLxYmLy",
            xm=xres,
            lx=self.length_x(xm=xres),
            ym=yres,
            ly=self.length_y(ym=yres),
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offs_xyz"]:
            self._set_auto_zero_offset("XY")
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0


    # Button pressed Center X+ X- Y+ Y-
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_xy_center_out_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("center") == -1:
            self.warning_dialog("center canceled by user !")
            return

        # before using some self value from linuxcnc we need to poll
        self.stat.poll()
        initial_x_position = self.stat.position[0]

        # Start psng_start_z_probing_for_diam.ngc
        if self.ocode("o<psng_start_z_probing> call [1]") == -1:
            return

        # move to calculated point X clearance + up Z with latch value
        s = """G91
        G1 X-%f Z%f
        G90""" % (self.halcomp["psng_latch"] + tooldiameter, self.halcomp["psng_latch"])
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
        if self.ocode("o<psng_start_z_probing> call [2]") == -1:
            return

        # move to calculated point X clearance + up Z with latch value
        s = """G91
        G1 X%f Z%f
        G90""" % (self.halcomp["psng_latch"] + tooldiameter, self.halcomp["psng_latch"])
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

        # move Z temporary away from probing position
        if self.move_probe_z_up() == -1:
            return


        # go to the new center of X
        s = "G1 X%f" % (xcres)
        if self.gcode(s) == -1:
            return


        # before using some self value from linuxcnc we need to poll
        self.stat.poll()
        initial_y_position = self.stat.position[1]

        # Start psng_start_z_probing_for_diam.ngc
        if self.ocode("o<psng_start_z_probing> call [3]") == -1:
            return

        # move to calculated point Y clearance + up Z with latch value
        s = """G91
        G1 Y-%f Z%f
        G90""" % (self.halcomp["psng_latch"] + tooldiameter, self.halcomp["psng_latch"])
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
        if self.ocode("o<psng_start_z_probing> call [4]") == -1:
            return

        # move to calculated point Y clearance + up Z with latch value
        s = """G91
        G1 Y%f Z%f
        G90""" % (self.halcomp["psng_latch"] + tooldiameter, self.halcomp["psng_latch"])
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


        # Calculate result diameter
        diam = ymres - ypres
        diam = 0.5 * ((xpres - xmres) + (ypres - ymres))

        # show calculated point center
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmXcXpLxYmYcYpLyD",
            xm=xmres,
            xc=xcres,
            xp=xpres,
            lx=self.length_x(xm=xmres, xp=xpres),
            ym=ymres,
            yc=ycres,
            yp=ypres,
            ly=self.length_y(ym=ymres, yp=ypres),
            d=diam,
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offs_xyz"]:
            self._set_auto_zero_offset("XY")
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0




    # --------------------------
    #
    #  Command buttons Measurement inside
    #
    # --------------------------

    # Corners
    # Move Probe manual under corner 2-3 mm
    # Button pressed X+Y+
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_xpyp_in_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("xpyp_in") == -1:
            self.warning_dialog("xpyp_in canceled by user !")
            return

        # before using some self value from linuxcnc we need to poll
        self.stat.poll()
        initial_x_position = self.stat.position[0]
        initial_y_position = self.stat.position[1]

        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0]) + (0.5 * tooldiameter)

        # move to calculated point
        s = "G1 X%f" % (initial_x_position)
        if self.gcode(s) == -1:
            return

        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1]) + (0.5 * tooldiameter)

        # move to calculated point
        s = "G1 Y%f" % (initial_y_position)
        if self.gcode(s) == -1:
            return

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XpLxYpLy",
            xp=xres,
            lx=self.length_x(xp=xres),
            yp=yres,
            ly=self.length_y(yp=yres),
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offs_xyz"]:
            self._set_auto_zero_offset("XY")
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0

    # Button pressed X+Y-
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_xpym_in_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("xpym_in") == -1:
            self.warning_dialog("xpym_in canceled by user !")
            return

        # before using some self value from linuxcnc we need to poll
        self.stat.poll()
        initial_x_position = self.stat.position[0]
        initial_y_position = self.stat.position[1]

        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0]) + (0.5 * tooldiameter)

        # move to calculated point
        s = "G1 X%f" % (initial_x_position)
        if self.gcode(s) == -1:
            return

        # Start psng_yminus.ngc load var fromm hal
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1]) - (0.5 * tooldiameter)

        # move to calculated point
        s = "G1 Y%f" % (initial_y_position)
        if self.gcode(s) == -1:
            return

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XpLxYmLy",
            xp=xres,
            lx=self.length_x(xp=xres),
            ym=yres,
            ly=self.length_y(ym=yres),
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offs_xyz"]:
            self._set_auto_zero_offset("XY")
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0


    # Button pressed X-Y+
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_xmyp_in_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("xmyp_in") == -1:
            self.warning_dialog("xmyp_in canceled by user !")
            return

        # before using some self value from linuxcnc we need to poll
        self.stat.poll()
        initial_x_position = self.stat.position[0]
        initial_y_position = self.stat.position[1]

        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0]) - (0.5 * tooldiameter)

        # move to calculated point
        s = "G1 X%f" % (initial_x_position)
        if self.gcode(s) == -1:
            return

        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1]) + (0.5 * tooldiameter)

        # move to calculated point
        s = "G1 Y%f" % (initial_y_position)
        if self.gcode(s) == -1:
            return

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmLxYpLy",
            xm=xres,
            lx=self.length_x(xm=xres),
            yp=yres,
            ly=self.length_y(yp=yres),
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offs_xyz"]:
            self._set_auto_zero_offset("XY")
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0


    # Button pressed X-Y-
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_xmym_in_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("xmym_in") == -1:
            self.warning_dialog("xmym_in canceled by user !")
            return

        # before using some self value from linuxcnc we need to poll
        self.stat.poll()
        initial_x_position = self.stat.position[0]
        initial_y_position = self.stat.position[1]

        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0]) - (0.5 * tooldiameter)

        # move to calculated point
        s = "G1 X%f" % (initial_x_position)
        if self.gcode(s) == -1:
            return

        # Start psng_yminus.ngc load var fromm hal
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1]) - (0.5 * tooldiameter)

        # move to calculated point
        s = "G1 Y%f" % (initial_y_position)
        if self.gcode(s) == -1:
            return

        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # move to calculated point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offs_xyz"]:
            self._set_auto_zero_offset("XY")
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0


    # Button pressed Hole Xin- Xin+ Yin- Yin+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_xy_hole_in_released(self, gtkbutton):
        tooldiameter = self.halcomp["toolchange_diameter"] #float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("xy_hole") == -1:
            self.warning_dialog("xy_hole canceled by user !")
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


        # go to the new center of X
        s = "G1 X%f" % (xcres)
        if self.gcode(s) == -1:
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


        # go to the new center of Y
        s = "G1 Y%f" % (ycres)
        if self.gcode(s) == -1:
            return


        # move Z away from probing position
        if self.move_probe_z_up() == -1:
            return

        # Calculate result diameter
        diam = 0.5 * ((xpres - xmres) + (ypres - ymres))

        # show calculated point center
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmXcXpLxYmYcYpLyD",
            xm=xmres,
            xc=xcres,
            xp=xpres,
            lx=self.length_x(xm=xmres, xp=xpres),
            ym=ymres,
            yc=ycres,
            yp=ypres,
            ly=self.length_y(ym=ymres, yp=ypres),
            d=diam,
        )

        # Optional auto zero selectable from gui
        if self.halcomp["chk_use_auto_zero_offs_xyz"]:
            self._set_auto_zero_offset("XY")
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0
