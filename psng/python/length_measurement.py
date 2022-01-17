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
from .base import ProbeScreenBase

from subprocess import Popen, PIPE

class ProbeScreenLengthMeasurement(ProbeScreenBase):
    # --------------------------
    #
    #  INIT
    #
    # --------------------------
    def __init__(self, halcomp, builder, useropts):
        super(ProbeScreenLengthMeasurement, self).__init__(halcomp, builder, useropts)

        self.lx_out = self.builder.get_object("lx_out")
        self.lx_in = self.builder.get_object("lx_in")
        self.ly_out = self.builder.get_object("ly_out")
        self.ly_in = self.builder.get_object("ly_in")

    # --------------
    # Length Buttons
    # --------------

    # Lx OUT
    @ProbeScreenBase.ensure_errors_dismissed
    def on_lx_out_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                          # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        # move X - edge_length- xy_clearance
        tmpx = self.halcomp["edge_length"] + self.halcomp["xy_clearance"]
        s = """G91
        G1 X-%f
        G90""" % (tmpx)
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_xplus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xpres = float(a[0] + 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            xpres = float(a[0] + self.halcomp["tp_lenght"] + 0.5 * tooldiameter)

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded  point X
        s = "G1 X%f" % (xpres)
        if self.gcode(s) == -1:
            return

        # move X + 2 edge_length +  xy_clearance
        tmpx = 2 * self.halcomp["edge_length"] + self.halcomp["xy_clearance"]
        s = """G91
        G1 X%f
        G90""" % (tmpx)
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_xminus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xmres = float(a[0] - 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            xmres = float(a[0] - self.halcomp["tp_lenght"] - 0.5 * tooldiameter)

        # find, show and move to finded point
        xcres = 0.5 * (xpres + xmres)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmXcXpLx",
            xm=xmres,
            xc=xcres,
            xp=xpres,
            lx=self.length_x(xm=xmres, xp=xpres),
        )

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # go to the new center of X
        s = "G1 X%f" % (xcres)
        if self.gcode(s) == -1:
            return
        self.set_zerro("X")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # Ly OUT
    @ProbeScreenBase.ensure_errors_dismissed
    def on_ly_out_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                          # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        # move Y - edge_length- xy_clearance
        tmpy = self.halcomp["edge_length"] + self.halcomp["xy_clearance"]
        s = """G91
        G1 Y-%f
        G90""" % (tmpy)
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_yplus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        ypres = float(a[1] + 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            ypres = float(a[1] + self.halcomp["tp_lenght"] + 0.5 * tooldiameter)

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded  point Y
        s = "G1 Y%f" % (ypres)
        if self.gcode(s) == -1:
            return

        # move Y + 2 edge_length +  xy_clearance
        tmpy = 2 * self.halcomp["edge_length"] + self.halcomp["xy_clearance"]
        s = """G91
        G1 Y%f
        G90""" % (tmpy)
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_yminus.ngc load var fromm hal
        if self.ocode("o<psng_yminus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        ymres = float(a[1] - 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            ymres = float(a[1] - self.halcomp["tp_lenght"] - 0.5 * tooldiameter)

        # find, show and move to finded point
        ycres = 0.5 * (ypres + ymres)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "YmYcYpLy",
            ym=ymres,
            yc=ycres,
            yp=ypres,
            ly=self.length_y(ym=ymres, yp=ypres),
        )

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # go to the new center of Y
        s = "G1 Y%f" % (ycres)
        if self.gcode(s) == -1:
            return
        self.set_zerro("Y")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return


    # Lx IN
    @ProbeScreenBase.ensure_errors_dismissed
    def on_lx_in_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                          # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        if self.z_clearance_down() == -1:
            return
        # move X - edge_length Y + xy_clearance
        tmpx = self.halcomp["edge_length"] - self.halcomp["xy_clearance"]
        s = """G91
        G1 X-%f
        G90""" % (tmpx)
        if self.gcode(s) == -1:
            return
        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_xminus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xmres = float(a[0] - 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            xmres = float(a[0] - self.halcomp["tp_lenght"] - 0.5 * tooldiameter)

        # move X +2 edge_length - 2 xy_clearance
        tmpx = 2 * (self.halcomp["edge_length"] - self.halcomp["xy_clearance"])
        s = """G91
        G1 X%f
        G90""" % (tmpx)
        if self.gcode(s) == -1:
            return
        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_xplus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xpres = float(a[0] + 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            xpres = float(a[0] + self.halcomp["tp_lenght"] + 0.5 * tooldiameter)

        # find, show and move to finded point
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
        # move Z to start point
        if self.z_clearance_up() == -1:
            return
        self.set_zerro("X")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return


    # Ly IN
    @ProbeScreenBase.ensure_errors_dismissed
    def on_ly_in_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                          # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        if self.z_clearance_down() == -1:
            return
        # move Y - edge_length + xy_clearance
        tmpy = self.halcomp["edge_length"] - self.halcomp["xy_clearance"]
        s = """G91
        G1 Y-%f
        G90""" % (tmpy)
        if self.gcode(s) == -1:
            return
        # Start psng_yminus.ngc load var fromm hal
        if self.ocode("o<psng_yminus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        ymres = float(a[1] - 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            ymres = float(a[1] - self.halcomp["tp_lenght"] - 0.5 * tooldiameter)

        # move Y +2 edge_length - 2 xy_clearance
        tmpy = 2 * (self.halcomp["edge_length"] - self.halcomp["xy_clearance"])
        s = """G91
        G1 Y%f
        G90""" % (tmpy)
        if self.gcode(s) == -1:
            return
        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_yplus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        ypres = float(a[1] + 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            ypres = float(a[1] + self.halcomp["tp_lenght"] + 0.5 * tooldiameter)

        # find, show and move to finded  point
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
        # move Z to start point
        if self.z_clearance_up() == -1:
            return
        self.set_zerro("Y")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return
