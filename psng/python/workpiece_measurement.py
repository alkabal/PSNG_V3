#!/usr/bin/env python
#
# Copyright (c) 2015 Serguei Glavatski ( verser  from cnc-club.ru )
# Copyright (c) 2020 Probe Screen NG Developers
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

class ProbeScreenWorkpieceMeasurement(ProbeScreenBase):

    # --------------------------
    #
    #  INIT
    #
    # --------------------------
    def __init__(self, halcomp, builder, useropts):
        super(ProbeScreenWorkpieceMeasurement, self).__init__(
            halcomp, builder, useropts
        )

        self.xpym = self.builder.get_object("xpym")
        self.ym = self.builder.get_object("ym")
        self.xmym = self.builder.get_object("xmym")
        self.xp = self.builder.get_object("xp")
        self.center = self.builder.get_object("center")
        self.xm = self.builder.get_object("xm")
        self.xpyp = self.builder.get_object("xpyp")
        self.yp = self.builder.get_object("yp")
        self.xmyp = self.builder.get_object("xmyp")
        self.hole = self.builder.get_object("hole")

    # --------------  Command buttons -----------------
    #               Measurement outside
    # -------------------------------------------------
    # X+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_xp_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        # move X - xy_clearance
        s = """G91
        G1 X-%f
        G90""" % (
            self.halcomp["xy_clearance"]
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_xplus.ngc
        if self.ocode("o<psng_xplus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0] + 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            xres = float(a[0] + self.halcomp["tp_lenght"] + 0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XpLx",
            xp=xres,
            lx=self.length_x(xp=xres),
        )

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded point
        s = "G1 X%f" % (xres)
        if self.gcode(s) == -1:
            return
        self.set_zerro("X")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # Y+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_yp_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        # move Y - xy_clearance
        s = """G91
        G1 Y-%f
        G90""" % (
            self.halcomp["xy_clearance"]
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_yplus.ngc
        if self.ocode("o<psng_yplus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1] + 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            yres = float(a[1] + self.halcomp["tp_lenght"] + 0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "YpLy",
            yp=yres,
            ly=self.length_y(yp=yres),
        )

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded point
        s = "G1 Y%f" % (yres)
        if self.gcode(s) == -1:
            return
        self.set_zerro("Y")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # X-
    @ProbeScreenBase.ensure_errors_dismissed
    def on_xm_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        # move X + xy_clearance
        s = """G91
        G1 X%f
        G90""" % (
            self.halcomp["xy_clearance"]
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_xminus.ngc
        if self.ocode("o<psng_xminus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0] - 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            xres = float(a[0] - self.halcomp["tp_lenght"] - 0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmLx",
            xm=xres,
            lx=self.length_x(xm=xres),
        )

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded point
        s = "G1 X%f" % (xres)
        if self.gcode(s) == -1:
            return
        self.set_zerro("X")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # Y-
    @ProbeScreenBase.ensure_errors_dismissed
    def on_ym_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        # move Y + xy_clearance
        s = """G91
        G1 Y%f
        G90""" % (
            self.halcomp["xy_clearance"]
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_yminus.ngc
        if self.ocode("o<psng_yminus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1] - 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            yres = float(a[1] - self.halcomp["tp_lenght"] - 0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "YmLy",
            ym=yres,
            ly=self.length_y(ym=yres),
        )

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded point
        s = "G1 Y%f" % (yres)
        if self.gcode(s) == -1:
            return
        self.set_zerro("Y")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # Corners
    # Move Probe manual under corner 2-3 mm
    # X+Y+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_xpyp_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        # move X - xy_clearance Y + edge_length
        s = """G91
        G1 X-%f Y%f
        G90""" % (
            self.halcomp["xy_clearance"],
            self.halcomp["edge_length"],
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_xplus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0] + 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            xres = float(a[0] + self.halcomp["tp_lenght"] + 0.5 * tooldiameter)

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return

        # move X + edge_length +xy_clearance,  Y - edge_length - xy_clearance
        tmpxy = self.halcomp["edge_length"] + self.halcomp["xy_clearance"]
        s = """G91
        G1 X%f Y-%f
        G90""" % (
            tmpxy,
            tmpxy,
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_yplus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1] + 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            yres = float(a[1] + self.halcomp["tp_lenght"] + 0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XpLxYpLy",
            xp=xres,
            lx=self.length_x(xp=xres),
            yp=yres,
            ly=self.length_y(yp=yres),
        )

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # X+Y-
    @ProbeScreenBase.ensure_errors_dismissed
    def on_xpym_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        # move X - xy_clearance Y + edge_length
        s = """G91
        G1 X-%f Y-%f
        G90""" % (
            self.halcomp["xy_clearance"],
            self.halcomp["edge_length"],
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_xplus.ngc
        if self.ocode("o<psng_xplus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0] + 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            xres = float(a[0] + self.halcomp["tp_lenght"] + 0.5 * tooldiameter)

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return

        # move X + edge_length +xy_clearance,  Y + edge_length + xy_clearance
        tmpxy = self.halcomp["edge_length"] + self.halcomp["xy_clearance"]
        s = """G91
        G1 X%f Y%f
        G90""" % (
            tmpxy,
            tmpxy,
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_yminus.ngc
        if self.ocode("o<psng_yminus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1] - 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            yres = float(a[1] - self.halcomp["tp_lenght"] - 0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XpLxYmLy",
            xp=xres,
            lx=self.length_x(xp=xres),
            ym=yres,
            ly=self.length_y(ym=yres),
        )

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # X-Y+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_xmyp_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        # move X + xy_clearance Y + edge_length
        s = """G91
        G1 X%f Y%f
        G90""" % (
            self.halcomp["xy_clearance"],
            self.halcomp["edge_length"],
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_xminus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0] - 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            xres = float(a[0] - self.halcomp["tp_lenght"] - 0.5 * tooldiameter)

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return

        # move X - edge_length - xy_clearance,  Y - edge_length - xy_clearance
        tmpxy = self.halcomp["edge_length"] + self.halcomp["xy_clearance"]
        s = """G91
        G1 X-%f Y-%f
        G90""" % (
            tmpxy,
            tmpxy,
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_yplus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1] + 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            yres = float(a[1] + self.halcomp["tp_lenght"] + 0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmLxYpLy",
            xm=xres,
            lx=self.length_x(xm=xres),
            yp=yres,
            ly=self.length_y(yp=yres),
        )

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # X-Y-
    @ProbeScreenBase.ensure_errors_dismissed
    def on_xmym_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        # move X + xy_clearance Y - edge_length
        s = """G91
        G1 X%f Y-%f
        G90""" % (
            self.halcomp["xy_clearance"],
            self.halcomp["edge_length"],
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_xminus.ngc
        if self.ocode("o<psng_xminus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0] - 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            xres = float(a[0] - self.halcomp["tp_lenght"] - 0.5 * tooldiameter)

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return

        # move X - edge_length - xy_clearance,  Y + edge_length + xy_clearance
        tmpxy = self.halcomp["edge_length"] + self.halcomp["xy_clearance"]
        s = """G91
        G1 X-%f Y%f
        G90""" % (
            tmpxy,
            tmpxy,
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_yminus.ngc
        if self.ocode("o<psng_yminus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1] - 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            yres = float(a[1] - self.halcomp["tp_lenght"] - 0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmLxYmLy",
            xm=xres,
            lx=self.length_x(xm=xres),
            ym=yres,
            ly=self.length_y(ym=yres),
        )

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # Center X+ X- Y+ Y-
    @ProbeScreenBase.ensure_errors_dismissed
    def on_xy_center_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        # move X - edge_length- xy_clearance
        tmpx = self.halcomp["edge_length"] + self.halcomp["xy_clearance"]
        s = """G91
        G1 X-%f
        G90""" % (
            tmpx
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_xplus.ngc
        if self.ocode("o<psng_xplus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xpres = float(a[0]) + 0.5 * self.halcomp["probe_diam"]

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return

        # move X + 2 edge_length + 2 xy_clearance
        tmpx = 2 * (self.halcomp["edge_length"] + self.halcomp["xy_clearance"])
        s = """G91
        G1 X%f
        G90""" % (
            tmpx
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_xminus.ngc
        if self.ocode("o<psng_xminus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xmres = float(a[0]) - 0.5 * self.halcomp["probe_diam"]
        xcres = 0.5 * (xpres + xmres)

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move X to new center
        s = "G1 X%f" % (xcres)
        if self.gcode(s) == -1:
            return

        # move Y - edge_length- xy_clearance
        tmpy = self.halcomp["edge_length"] + self.halcomp["xy_clearance"]
        s = """G91
        G1 Y-%f
        G90""" % (
            tmpy
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_yplus.ngc
        if self.ocode("o<psng_yplus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        ypres = float(a[1]) + 0.5 * self.halcomp["probe_diam"]

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return

        # move Y + 2 edge_length + 2 xy_clearance
        tmpy = 2 * (self.halcomp["edge_length"] + self.halcomp["xy_clearance"])
        s = """G91
        G1 Y%f
        G90""" % (
            tmpy
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return

        # Start psng_yminus.ngc
        if self.ocode("o<psng_yminus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        ymres = float(a[1]) - 0.5 * self.halcomp["probe_diam"]

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
        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded point
        s = "G1 Y%f" % (ycres)
        if self.gcode(s) == -1:
            return
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # --------------  Command buttons -----------------
    #               Measurement inside
    # -------------------------------------------------

    # Corners
    # Move Probe manual under corner 2-3 mm
    # X+Y+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_xpyp1_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        # move X - xy_clearance Y - edge_length
        s = """G91
        G1 X-%f Y-%f
        G90""" % (
            self.halcomp["xy_clearance"],
            self.halcomp["edge_length"],
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_xplus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0] + 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            xres = float(a[0] + self.halcomp["tp_lenght"] + 0.5 * tooldiameter)

        # move X - edge_length Y - xy_clearance
        tmpxy = self.halcomp["edge_length"] - self.halcomp["xy_clearance"]
        s = """G91
        G1 X-%f Y%f
        G90""" % (
            tmpxy,
            tmpxy,
        )
        if self.gcode(s) == -1:
            return
        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_yplus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1] + 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            yres = float(a[1] + self.halcomp["tp_lenght"] + 0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XpLxYpLy",
            xp=xres,
            lx=self.length_x(xp=xres),
            yp=yres,
            ly=self.length_y(yp=yres),
        )

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # X+Y-
    @ProbeScreenBase.ensure_errors_dismissed
    def on_xpym1_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        # move X - xy_clearance Y + edge_length
        s = """G91
        G1 X-%f Y%f
        G90""" % (
            self.halcomp["xy_clearance"],
            self.halcomp["edge_length"],
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_xplus.ngc load var fromm hal
        if self.ocode("o<psng_xplus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0] + 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            xres = float(a[0] + self.halcomp["tp_lenght"] + 0.5 * tooldiameter)

        # move X - edge_length Y + xy_clearance
        tmpxy = self.halcomp["edge_length"] - self.halcomp["xy_clearance"]
        s = """G91
        G1 X-%f Y-%f
        G90""" % (
            tmpxy,
            tmpxy,
        )
        if self.gcode(s) == -1:
            return
        # Start psng_yminus.ngc load var fromm hal
        if self.ocode("o<psng_yminus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1] - 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            yres = float(a[1] - self.halcomp["tp_lenght"] - 0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XpLxYmLy",
            xp=xres,
            lx=self.length_x(xp=xres),
            ym=yres,
            ly=self.length_y(ym=yres),
        )

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # X-Y+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_xmyp1_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        # move X + xy_clearance Y - edge_length
        s = """G91
        G1 X%f Y-%f
        G90""" % (
            self.halcomp["xy_clearance"],
            self.halcomp["edge_length"],
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_xminus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0] - 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            xres = float(a[0] - self.halcomp["tp_lenght"] - 0.5 * tooldiameter)

        # move X + edge_length Y - xy_clearance
        tmpxy = self.halcomp["edge_length"] - self.halcomp["xy_clearance"]
        s = """G91
        G1 X%f Y%f
        G90""" % (
            tmpxy,
            tmpxy,
        )
        if self.gcode(s) == -1:
            return
        # Start psng_yplus.ngc load var fromm hal
        if self.ocode("o<psng_yplus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1] + 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            yres = float(a[1] + self.halcomp["tp_lenght"] + 0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmLxYpLy",
            xm=xres,
            lx=self.length_x(xm=xres),
            yp=yres,
            ly=self.length_y(yp=yres),
        )

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # X-Y-
    @ProbeScreenBase.ensure_errors_dismissed
    def on_xmym1_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        # move X + xy_clearance Y + edge_length
        s = """G91
        G1 X%f Y%f
        G90""" % (
            self.halcomp["xy_clearance"],
            self.halcomp["edge_length"],
        )
        if self.gcode(s) == -1:
            return
        if self.z_clearance_down() == -1:
            return
        # Start psng_xminus.ngc load var fromm hal
        if self.ocode("o<psng_xminus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xres = float(a[0] - 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            xres = float(a[0] - self.halcomp["tp_lenght"] - 0.5 * tooldiameter)

        # move X + edge_length Y - xy_clearance
        tmpxy = self.halcomp["edge_length"] - self.halcomp["xy_clearance"]
        s = """G91
        G1 X%f Y-%f
        G90""" % (
            tmpxy,
            tmpxy,
        )
        if self.gcode(s) == -1:
            return
        # Start psng_yminus.ngc load var fromm hal
        if self.ocode("o<psng_yminus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        yres = float(a[1] - 0.5 * self.halcomp["probe_diam"])
        if self.halcomp["use_touch_plate"] == True:
            tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
            yres = float(a[1] - self.halcomp["tp_lenght"] - 0.5 * tooldiameter)

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XmLxYmLy",
            xm=xres,
            lx=self.length_x(xm=xres),
            ym=yres,
            ly=self.length_y(ym=yres),
        )

        # move Z to start point up
        if self.z_clearance_up() == -1:
            return
        # move to finded point
        s = "G1 X%f Y%f" % (xres, yres)
        if self.gcode(s) == -1:
            return
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # Hole Xin- Xin+ Yin- Yin+
    @ProbeScreenBase.ensure_errors_dismissed
    def on_xy_hole_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [7]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return                # CHECK HAL VALUE FROM GUI FOR CONSITANCY
        if self.z_clearance_down() == -1:
            return
        # move X - edge_length Y + xy_clearance
        tmpx = self.halcomp["edge_length"] - self.halcomp["xy_clearance"]
        s = """G91
        G1 X-%f
        G90""" % (
            tmpx
        )
        if self.gcode(s) == -1:
            return
        # Start psng_xminus.ngc
        if self.ocode("o<psng_xminus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xmres = float(a[0]) - 0.5 * self.halcomp["probe_diam"]

        # move X +2 edge_length - 2 xy_clearance
        tmpx = 2 * (self.halcomp["edge_length"] - self.halcomp["xy_clearance"])
        s = """G91
        G1 X%f
        G90""" % (
            tmpx
        )
        if self.gcode(s) == -1:
            return
        # Start psng_xplus.ngc
        if self.ocode("o<psng_xplus> call") == -1:
            return

        # Calculate X result
        a = self.probed_position_with_offsets()
        xpres = float(a[0]) + 0.5 * self.halcomp["probe_diam"]
        xcres = 0.5 * (xmres + xpres)

        # move X to new center
        s = """G1 X%f""" % (xcres)
        if self.gcode(s) == -1:
            return

        # move Y - edge_length + xy_clearance
        tmpy = self.halcomp["edge_length"] - self.halcomp["xy_clearance"]
        s = """G91
        G1 Y-%f
        G90""" % (
            tmpy
        )
        if self.gcode(s) == -1:
            return
        # Start psng_yminus.ngc
        if self.ocode("o<psng_yminus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        ymres = float(a[1]) - 0.5 * self.halcomp["probe_diam"]

        # move Y +2 edge_length - 2 xy_clearance
        tmpy = 2 * (self.halcomp["edge_length"] - self.halcomp["xy_clearance"])
        s = """G91
        G1 Y%f
        G90""" % (
            tmpy
        )
        if self.gcode(s) == -1:
            return
        # Start psng_yplus.ngc
        if self.ocode("o<psng_yplus> call") == -1:
            return

        # Calculate Y result
        a = self.probed_position_with_offsets()
        ypres = float(a[1]) + 0.5 * self.halcomp["probe_diam"]

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
        # move Z to start point
        if self.z_clearance_up() == -1:
            return
        self.set_zerro("XY")
        if self.ocode("o<backup_restore> call [999]") == -1:
            return
