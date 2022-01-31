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

    # X+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_xp_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # move X - clearance_xy
        s = """G91
        G1 X-%f
        G90""" % (
            self.halcomp["clearance_xy"]
        )
        if self.gcode(s) == -1:
            return

        # Start psng_xplus.ngc
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0]) + (0.5 * tooldiameter)
        if self.halcomp["chk_touch_plate_selected"] == True:
            xres = float(a[0]) + self.halcomp["tp_XY_thickness"] + (0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XpLx",
            xp=xres,
            lx=self.length_x(xp=xres),
        )

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move to finded point
        s = "G1 X%f" % (xres)
        if self.gcode(s) == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("X")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # Y+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_yp_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # move Y - clearance_xy
        s = """G91
        G1 Y-%f
        G90""" % (
            self.halcomp["clearance_xy"]
        )
        if self.gcode(s) == -1:
            return

        # Start psng_yplus.ngc
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1]) + (0.5 * tooldiameter)
        if self.halcomp["chk_touch_plate_selected"] == True:
            yres = float(a[1]) + self.halcomp["tp_XY_thickness"] + (0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "YpLy",
            yp=yres,
            ly=self.length_y(yp=yres),
        )

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move to finded point
        s = "G1 Y%f" % (yres)
        if self.gcode(s) == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("Y")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # X-
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_xm_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # move X + clearance_xy
        s = """G91
        G1 X%f
        G90""" % (
            self.halcomp["clearance_xy"]
        )
        if self.gcode(s) == -1:
            return

        # Start psng_xminus.ngc
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0]) - (0.5 * tooldiameter)
        if self.halcomp["chk_touch_plate_selected"] == True:
            xres = float(a[0]) - self.halcomp["tp_XY_thickness"] - (0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmLx",
            xm=xres,
            lx=self.length_x(xm=xres),
        )

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move to finded point
        s = "G1 X%f" % (xres)
        if self.gcode(s) == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("X")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # Y-
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_ym_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # move Y + clearance_xy
        s = """G91
        G1 Y%f
        G90""" % (
            self.halcomp["clearance_xy"]
        )
        if self.gcode(s) == -1:
            return

        # Start psng_yminus.ngc
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1]) - (0.5 * tooldiameter)
        if self.halcomp["chk_touch_plate_selected"] == True:
            yres = float(a[1]) - self.halcomp["tp_XY_thickness"] - (0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "YmLy",
            ym=yres,
            ly=self.length_y(ym=yres),
        )

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move to finded point
        s = "G1 Y%f" % (yres)
        if self.gcode(s) == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("Y")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # --------------------------
    #
    #  Command buttons Measurement outside
    #
    # --------------------------

    # Corners
    # Move Probe manual under corner 2-3 mm
    # X+Y+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_xpyp_out_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # move X - clearance_xy Y + edge_length
        s = """G91
        G1 X-%f Y%f
        G90""" % (
            self.halcomp["clearance_xy"],
            self.halcomp["edge_length"],
        )
        if self.gcode(s) == -1:
            return

        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0]) + (0.5 * tooldiameter)
        if self.halcomp["chk_touch_plate_selected"] == True:
            xres = float(a[0]) + self.halcomp["tp_XY_thickness"] + (0.5 * tooldiameter)

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move X + edge_length +clearance_xy,  Y - edge_length - clearance_xy
        tmpxy = self.halcomp["edge_length"] + self.halcomp["clearance_xy"]
        s = """G91
        G1 X%f Y-%f
        G90""" % (
            tmpxy,
            tmpxy,
        )
        if self.gcode(s) == -1:
            return

        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1]) + (0.5 * tooldiameter)
        if self.halcomp["chk_touch_plate_selected"] == True:
            yres = float(a[1]) + self.halcomp["tp_XY_thickness"] + (0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XpLxYpLy",
            xp=xres,
            lx=self.length_x(xp=xres),
            yp=yres,
            ly=self.length_y(yp=yres),
        )

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move to finded point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # X+Y-
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_xpym_out_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # move X - clearance_xy Y + edge_length
        s = """G91
        G1 X-%f Y-%f
        G90""" % (
            self.halcomp["clearance_xy"],
            self.halcomp["edge_length"],
        )
        if self.gcode(s) == -1:
            return

        # Start psng_xplus.ngc
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0]) + (0.5 * tooldiameter)
        if self.halcomp["chk_touch_plate_selected"] == True:
            xres = float(a[0]) + self.halcomp["tp_XY_thickness"] + (0.5 * tooldiameter)

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move X + edge_length +clearance_xy,  Y + edge_length + clearance_xy
        tmpxy = self.halcomp["edge_length"] + self.halcomp["clearance_xy"]
        s = """G91
        G1 X%f Y%f
        G90""" % (
            tmpxy,
            tmpxy,
        )
        if self.gcode(s) == -1:
            return

        # move Z to probing position
        if self.clearance_z_down() == -1:
            return

        # Start psng_yminus.ngc
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1]) - (0.5 * tooldiameter)
        if self.halcomp["chk_touch_plate_selected"] == True:
            yres = float(a[1]) - self.halcomp["tp_XY_thickness"] - (0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XpLxYmLy",
            xp=xres,
            lx=self.length_x(xp=xres),
            ym=yres,
            ly=self.length_y(ym=yres),
        )

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move to finded point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # X-Y+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_xmyp_out_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # move X + clearance_xy Y + edge_length
        s = """G91
        G1 X%f Y%f
        G90""" % (
            self.halcomp["clearance_xy"],
            self.halcomp["edge_length"],
        )
        if self.gcode(s) == -1:
            return

        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0]) - (0.5 * tooldiameter)
        if self.halcomp["chk_touch_plate_selected"] == True:
            xres = float(a[0]) - self.halcomp["tp_XY_thickness"] - (0.5 * tooldiameter)

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move X - edge_length - clearance_xy,  Y - edge_length - clearance_xy
        tmpxy = self.halcomp["edge_length"] + self.halcomp["clearance_xy"]
        s = """G91
        G1 X-%f Y-%f
        G90""" % (
            tmpxy,
            tmpxy,
        )
        if self.gcode(s) == -1:
            return

        # move Z to probing position
        if self.clearance_z_down() == -1:
            return

        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1]) + (0.5 * tooldiameter)
        if self.halcomp["chk_touch_plate_selected"] == True:
            yres = float(a[1]) + self.halcomp["tp_XY_thickness"] + (0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmLxYpLy",
            xm=xres,
            lx=self.length_x(xm=xres),
            yp=yres,
            ly=self.length_y(yp=yres),
        )

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move to finded point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # X-Y-
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_xmym_out_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # move X + clearance_xy Y - edge_length
        s = """G91
        G1 X%f Y-%f
        G90""" % (
            self.halcomp["clearance_xy"],
            self.halcomp["edge_length"],
        )
        if self.gcode(s) == -1:
            return

        # Start psng_xminus.ngc
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0]) - (0.5 * tooldiameter)
        if self.halcomp["chk_touch_plate_selected"] == True:
            xres = float(a[0]) - self.halcomp["tp_XY_thickness"] - (0.5 * tooldiameter)

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move X - edge_length - clearance_xy,  Y + edge_length + clearance_xy
        tmpxy = self.halcomp["edge_length"] + self.halcomp["clearance_xy"]
        s = """G91
        G1 X-%f Y%f
        G90""" % (
            tmpxy,
            tmpxy,
        )
        if self.gcode(s) == -1:
            return

        # move Z to probing position
        if self.clearance_z_down() == -1:
            return

        # Start psng_yminus.ngc
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1]) - (0.5 * tooldiameter)
        if self.halcomp["chk_touch_plate_selected"] == True:
            yres = float(a[1]) - self.halcomp["tp_XY_thickness"] - (0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmLxYmLy",
            xm=xres,
            lx=self.length_x(xm=xres),
            ym=yres,
            ly=self.length_y(ym=yres),
        )

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move to finded point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # Center X+ X- Y+ Y-
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_xy_center_out_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # before using some self value from linuxcnc we need to poll
        self.stat.poll()
        temp_x_position = self.stat.position[0]

        # Start psng_start_z_probing_for_diam.ngc
        if self.ocode("o<psng_start_z_probing_for_diam> call") == -1:
            return

        self.stat.poll()   # before using some self value from linuxcnc we need to poll
        approximative_radius = temp_x_position - self.stat.position[0]

        # move X - edge_length - clearance_xy + up Z1 for allow the probe to noot touch the pieces with travel move
        s = """G91
        G1 X-%f Z%f
        G90""" % (
            tmpx,
            self.halcomp["latch"]
        )
        if self.gcode(s) == -1:
            return

        # move Z to probing position
        if self.clearance_z_down() == -1:
            return

        # Start psng_xplus.ngc
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xpres = float(a[0]) + (0.5 * tooldiameter)

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move X + 2 edge_length + 2 clearance_xy
        tmpx = 2 * (self.halcomp["clearance_xy"] + approximative_radius)
        s = """G91
        G1 X%f
        G90""" % (
            tmpx
        )
        if self.gcode(s) == -1:
            return

        # move Z to probing position
        if self.clearance_z_down() == -1:
            return

        # Start psng_xminus.ngc
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xmres = float(a[0]) - (0.5 * tooldiameter)
        xcres = 0.5 * (xpres + xmres)

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move X to new center
        s = "G1 X%f" % (xcres)
        if self.gcode(s) == -1:
            return

        # move Y - edge_length- clearance_xy
        tmpy = self.halcomp["clearance_xy"] + approximative_radius
        s = """G91
        G1 Y-%f
        G90""" % (
            tmpy
        )
        if self.gcode(s) == -1:
            return

        # move Z to probing position
        if self.clearance_z_down() == -1:
            return

        # Start psng_yplus.ngc
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        ypres = float(a[1]) + (0.5 * tooldiameter)

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move Y + 2 edge_length + 2 clearance_xy
        tmpy = 2 * (self.halcomp["clearance_xy"] + approximative_radius)
        s = """G91
        G1 Y%f
        G90""" % (
            tmpy
        )
        if self.gcode(s) == -1:
            return

        # move Z to probing position
        if self.clearance_z_down() == -1:
            return

        # Start psng_yminus.ngc
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        ymres = float(a[1]) - (0.5 * tooldiameter)

        # find, show and move to finded point
        ycres = 0.5 * (ypres + ymres)
        diam = ymres - ypres

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

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move to finded point
        s = "G1 Y%f" % (ycres)
        if self.gcode(s) == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return




    # --------------------------
    #
    #  Command buttons Measurement inside
    #
    # --------------------------

    # Corners
    # Move Probe manual under corner 2-3 mm
    # X+Y+
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_xpyp_in_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # move X - clearance_xy Y - edge_length
        s = """G91
        G1 X-%f Y-%f
        G90""" % (
            self.halcomp["clearance_xy"],
            self.halcomp["edge_length"],
        )
        if self.gcode(s) == -1:
            return

        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0]) + (0.5 * tooldiameter)

        # move X - edge_length Y - clearance_xy
        tmpxy = self.halcomp["edge_length"] - self.halcomp["clearance_xy"]
        s = """G91
        G1 X-%f Y%f
        G90""" % (
            tmpxy,
            tmpxy,
        )
        if self.gcode(s) == -1:
            return

        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1]) + (0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XpLxYpLy",
            xp=xres,
            lx=self.length_x(xp=xres),
            yp=yres,
            ly=self.length_y(yp=yres),
        )

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move to finded point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # X+Y-
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_xpym_in_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # move X - clearance_xy Y + edge_length
        s = """G91
        G1 X-%f Y%f
        G90""" % (
            self.halcomp["clearance_xy"],
            self.halcomp["edge_length"],
        )
        if self.gcode(s) == -1:
            return

        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0]) + (0.5 * tooldiameter)

        # move X - edge_length Y + clearance_xy
        tmpxy = self.halcomp["edge_length"] - self.halcomp["clearance_xy"]
        s = """G91
        G1 X-%f Y-%f
        G90""" % (
            tmpxy,
            tmpxy,
        )
        if self.gcode(s) == -1:
            return

        # Start psng_yminus.ngc load var fromm hal
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1]) - (0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XpLxYmLy",
            xp=xres,
            lx=self.length_x(xp=xres),
            ym=yres,
            ly=self.length_y(ym=yres),
        )

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move to finded point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # X-Y+
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_xmyp_in_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # move X + clearance_xy Y - edge_length
        s = """G91
        G1 X%f Y-%f
        G90""" % (
            self.halcomp["clearance_xy"],
            self.halcomp["edge_length"],
        )
        if self.gcode(s) == -1:
            return

        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0]) - (0.5 * tooldiameter)

        # move X + edge_length Y - clearance_xy
        tmpxy = self.halcomp["edge_length"] - self.halcomp["clearance_xy"]
        s = """G91
        G1 X%f Y%f
        G90""" % (
            tmpxy,
            tmpxy,
        )
        if self.gcode(s) == -1:
            return

        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1]) + (0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmLxYpLy",
            xm=xres,
            lx=self.length_x(xm=xres),
            yp=yres,
            ly=self.length_y(yp=yres),
        )

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move to finded point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # X-Y-
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_xmym_in_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
            return

        # move X + clearance_xy Y + edge_length
        s = """G91
        G1 X%f Y%f
        G90""" % (
            self.halcomp["clearance_xy"],
            self.halcomp["edge_length"],
        )
        if self.gcode(s) == -1:
            return

        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0]) - (0.5 * tooldiameter)

        # move X + edge_length Y - clearance_xy
        tmpxy = self.halcomp["edge_length"] - self.halcomp["clearance_xy"]
        s = """G91
        G1 X%f Y-%f
        G90""" % (
            tmpxy,
            tmpxy,
        )
        if self.gcode(s) == -1:
            return

        # Start psng_yminus.ngc load var fromm hal
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1]) - (0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmLxYmLy",
            xm=xres,
            lx=self.length_x(xm=xres),
            ym=yres,
            ly=self.length_y(ym=yres),
        )

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # move to finded point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # Hole Xin- Xin+ Yin- Yin+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_xy_hole_in_released(self, gtkbutton, data=None):
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_load_var_touch_probe> call") == -1:
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

        # Calculate X center
        xcres = 0.5 * (xmres + xpres)

        # move X to new center
        s = """G1 X%f""" % (xcres)
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

        # find, show and move to finded point
        ycres = 0.5 * (ymres + ypres)
        diam = 0.5 * ((xpres - xmres) + (ypres - ymres))

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

        # move to finded point
        s = "G1 Y%f" % (ycres)
        if self.gcode(s) == -1:
            return

        # move Z temporary away from probing position
        if self.clearance_z_up() == -1:
            return

        # Optional auto zerro selectable from gui
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return
