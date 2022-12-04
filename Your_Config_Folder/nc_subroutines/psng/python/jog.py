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

import hal  # base hal class to react to hal signals
import linuxcnc

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from gladevcp.gladebuilder import GladeBuilder
from gladevcp.combi_dro import Combi_DRO  # we will need it to make the DRO

class ProbeScreenJog(ProbeScreenBase):
    # --------------------------
    #
    #  INIT
    #
    # --------------------------
    def __init__(self, halcomp, builder, useropts):
        super(ProbeScreenJog, self).__init__(halcomp, builder, useropts)

        # For JOG
        self.steps = self.builder.get_object("steps")
        self.incr_rbt_list = []  # we use this list to add hal pin to the button later
        self.jog_increments = []  # This holds the increment values
        self.distance = 0  # This global will hold the jog distance
        self.halcomp.newpin("psng_jog_increment", hal.HAL_FLOAT, hal.HAL_OUT)


        # After getting value we need to init some of them
        self._init_jog_increments_data()
        self._make_DRO()


    # --------------------------
    #
    # Init value etc
    #
    # --------------------------
    def _init_jog_increments_data(self):
        # Get the increments from INI File
        jog_increments = []
        increments = self.inifile.find("DISPLAY", "INCREMENTS")
        if increments:
            if "," in increments:
                for i in increments.split(","):
                    jog_increments.append(i.strip())
            else:
                jog_increments = increments.split()
            jog_increments.insert(0, 0)
        else:
            jog_increments = [0, "1,000", "0,100", "0,010", "0,001"]
            self.warning_dialog("No default jog increments entry found in [DISPLAY] of INI file", "Please check the DISPLAY INI configurations")

        self.jog_increments = jog_increments
        if len(self.jog_increments) > 6:
            print ("**** PROBE SCREEN INFO ****")
            print ("**** To many increments given in INI File for this screen ****")
            print ("**** Only the first 5 will be reachable through this screen ****")
            # we shorten the incrementlist to 5 (first is default = 0)
            self.jog_increments = self.jog_increments[0:5]


        # The first radio button is created to get a radio button group
        # The group is called according the name off  the first button
        # We use the pressed signal, not the toggled, otherwise two signals will be emitted
        # One from the released button and one from the pressed button
        # we make a list of the buttons to later add the hardware pins to them
        rbt0 = Gtk.ToggleButton(label="Cont",)
        rbt0.connect("toggled", self.on_increment_toggled, 0)
        self.steps.pack_start(rbt0, True, True, 0)
        rbt0.set_property("draw_indicator", False)
        rbt0.set_property("width_request", 30)
        rbt0.show()
        rbt0.modify_bg(Gtk.StateType.ACTIVE, Gdk.color_parse("#FFFF00")) # test pour GTK3
        rbt0.__name__ = "rbt0"
        self.incr_rbt_list.append(rbt0)


        # the rest of the buttons are now added to the group
        # self.no_increments is set while setting the hal pins with self._check_len_increments
        for item in range(1, len(self.jog_increments)):
            rbt = "rbt%d" % (item)
            rbt = Gtk.ToggleButton(rbt0, label=self.jog_increments[item])
            rbt.connect("toggled", self.on_increment_toggled, self.jog_increments[item])
            self.steps.pack_start(rbt, True, True, 0)
            rbt.set_property("draw_indicator", False)
            rbt.set_property("width_request", 30)
            rbt.show()
            rbt.modify_bg(Gtk.StateType.ACTIVE, Gdk.color_parse("#FFFF00")) # test pour GTK3
            rbt.__name__ = "rbt%d" % (item)
            self.incr_rbt_list.append(rbt)

        # finally activate the button
        self.active_increment = "rbt0"


# Thanks a lot to Cmorley for pointing to this code, and thanks for gmoccapy code !
    def _make_DRO(self):

        from gmoccapy import widgets       # a class to handle the widgets
        from gmoccapy import getiniinfo    # this handles the INI File reading so checking is done in that module

        # we build one DRO for each axis
        self.dro_size = 30           # The size of the DRO, user may want them bigger on bigger screen

        self.widgets = widgets.Widgets(self.builder)

        # the colors of the DRO
        self.abs_color = self.prefs.getpref("abs_color", "#0000FF", str)         # blue
        self.rel_color = self.prefs.getpref("rel_color", "#000000", str)         # black
        self.dtg_color = self.prefs.getpref("dtg_color", "#FFFF00", str)         # yellow
        self.homed_color = self.prefs.getpref("homed_color", "#00FF00", str)     # green
        self.unhomed_color = self.prefs.getpref("unhomed_color", "#FF0000", str) # red

        self.get_ini_info = getiniinfo.GetIniInfo()
        self.axis_list = self.get_ini_info.get_axis_list()

        self.joint_axis_dic, self.double_axis_letter = self.get_ini_info.get_joint_axis_relation()
        self.dro_dic = {}
        for pos, axis in enumerate(self.axis_list):
            joint = self._get_joint_from_joint_axis_dic(axis)
            dro = Combi_DRO()
            dro.set_joint_no(joint)
            dro.set_axis(axis)
            dro.change_axisletter(axis.upper())
            dro.show()
            dro.set_property("name", "Combi_DRO_{0}".format(pos))
            dro.set_property("abs_color", self._get_RGBA_color(self.abs_color))
            dro.set_property("rel_color", self._get_RGBA_color(self.rel_color))
            dro.set_property("dtg_color", self._get_RGBA_color(self.dtg_color))
            dro.set_property("homed_color", self._get_RGBA_color(self.homed_color))
            dro.set_property("unhomed_color", self._get_RGBA_color(self.unhomed_color))
            dro.set_property("actual", self.get_ini_info.get_position_feedback_actual())
            dro.set_property("font_size", self.dro_size)
            dro.connect("clicked", self._on_DRO_clicked)
            self.dro_dic[dro.get_property("name")] = dro

        # TODO if we more than 4 axis, we only want to display the XYZ
        self._place_in_table(len(self.dro_dic),1, self.dro_size)


    def _get_RGBA_color(self, color_str):
        color = Gdk.RGBA()
        color.parse(color_str)
        return Gdk.RGBA(color.red, color.green, color.blue, color.alpha)


    def _get_joint_from_joint_axis_dic(self, value):
        # if the selected axis is a double axis we will get the joint from the master axis, which should end with 0
        if value in self.double_axis_letter:
            value = value + "0"
        return list(self.joint_axis_dic.keys())[list(self.joint_axis_dic.values()).index(value)]


    def _on_DRO_clicked(self, widget, joint, order):
        for dro in self.dro_dic:
            self.dro_dic[dro].set_order(order)
        return


    def _place_in_table(self, rows, cols, dro_size):
        print("**** PSNG_V3 INFO Place in table ****")
        print(len(self.dro_dic))

        self.widgets.tbl_DRO.resize(rows, cols)
        col = 0
        row = 0

        dro_order = sorted(self.dro_dic.keys())
        for dro, dro_name in enumerate(dro_order):
            self.widgets.tbl_DRO.attach(self.dro_dic[dro_name], col, col+1, row, row + 1, ypadding = 0)
            if cols > 1:
                # calculate if we have to place in the first or the second column
                if (dro % 2 == 1):
                    col = 0
                    row +=1
                else:
                    col += 1
            else:
                row += 1


    # --------------------------
    #
    # JOG BUTTONS
    #
    # --------------------------
    def on_increment_toggled(self, widget=None, data=None):
        if data == 0:
            self.distance = 0
        else:
            self.distance = self._parse_increment(data)
        self.halcomp["psng_jog_increment"] = self.distance
        self.active_increment = widget.get_property("name")   #widget.__name__

    def _from_internal_linear_unit(self, v, unit=None):
        if unit is None:
            unit = self.stat.linear_units
        lu = (unit or 1) * 25.4
        return v * lu

    def _parse_increment(self, jogincr):
        if jogincr.endswith("mm"):
            scale = self._from_internal_linear_unit(1 / 25.4)
        elif jogincr.endswith("cm"):
            scale = self._from_internal_linear_unit(10 / 25.4)
        elif jogincr.endswith("um"):
            scale = self._from_internal_linear_unit(0.001 / 25.4)
        elif jogincr.endswith("in") or jogincr.endswith("inch"):
            scale = self._from_internal_linear_unit(1.0)
        elif jogincr.endswith("mil"):
            scale = self._from_internal_linear_unit(0.001)
        else:
            scale = 1
        jogincr = jogincr.rstrip(" inchmuil")
        if "/" in jogincr:
            p, q = jogincr.split("/")
            jogincr = float(p) / float(q)
        else:
            jogincr = float(jogincr)
        return jogincr * scale

    def on_btn_jog_pressed(self, widget, data=None):
        # only in manual mode we will allow jogging the axis at this development state
        self.command.mode(linuxcnc.MODE_MANUAL)
        self.command.wait_complete()
        self.stat.poll()   # before using some self value from linuxcnc we need to poll
        if not self.stat.task_mode == linuxcnc.MODE_MANUAL:
            return

        axisletter = widget.get_label()[0]
        if not axisletter.lower() in "xyzabcuvw":
            self.warning_dialog("unknown axis %s") % (axisletter)
            return

        # get the axisnumber
        axisnumber = "xyzabcuvws".index(axisletter.lower())

        # if data = True, then the user pressed SHIFT for Jogging and
        # want's to jog at 0.2 speed
        if data:
            value = 0.2
        else:
            value = 1

        velocity = float(self.inifile.find("TRAJ", "DEFAULT_LINEAR_VELOCITY"))

        dir = widget.get_label()[1]
        if dir == "+":
            direction = 1
        else:
            direction = -1

        self.command.teleop_enable(1)
        if self.distance != 0:  # incremental jogging
            self.command.jog(
                linuxcnc.JOG_INCREMENT,
                False,
                axisnumber,
                direction * velocity,
                self.distance,
            )
        else:  # continuous jogging
            self.command.jog(
                linuxcnc.JOG_CONTINUOUS, False, axisnumber, direction * velocity
            )

    def on_btn_jog_released(self, widget):
        axisletter = widget.get_label()[0]
        if not axisletter.lower() in "xyzabcuvw":
            self.warning_dialog("unknown axis %s") % (axisletter)
            return

        axis = "xyzabcuvw".index(axisletter.lower())

        self.command.teleop_enable(1)
        if self.distance != 0:
            pass
        else:
            self.command.jog(linuxcnc.JOG_STOP, False, axis)
