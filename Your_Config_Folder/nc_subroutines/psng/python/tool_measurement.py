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

class ProbeScreenToolMeasurement(ProbeScreenBase):
    # --------------------------
    #
    #  INIT
    #
    # --------------------------
    def __init__(self, halcomp, builder, useropts):
        super(ProbeScreenToolMeasurement, self).__init__(halcomp, builder, useropts)

        self.tooledit1 = self.builder.get_object("tooledit1")

        self.frm_tool_measurement = self.builder.get_object("frm_tool_measurement")

        self.spbtn_setter_height = self.builder.get_object("spbtn_setter_height")

        self.hal_led_set_m6 = self.builder.get_object("hal_led_set_m6")
        self.hal_led_rotate_spindle = self.builder.get_object("hal_led_rotate_spindle")


        # for manual tool change dialog
        #self.halcomp.newpin("toolchange-number", hal.HAL_S32, hal.HAL_IN)
        #self.halcomp.newpin("toolchange-prep-number", hal.HAL_S32, hal.HAL_IN)
        #self.halcomp.newpin("toolchange-changed", hal.HAL_BIT, hal.HAL_OUT)
        #pin = self.halcomp.newpin("toolchange-change", hal.HAL_BIT, hal.HAL_IN)
        #hal_glib.GPin(pin).connect("value_changed", self.on_tool_change)


        # make the pins for tool measurement
        self.halcomp.newpin("ts_probed_table", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_probed_tool_z", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_probed_tool_diam", hal.HAL_FLOAT, hal.HAL_OUT)

        self.halcomp.newpin("ts_pos_x", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("ts_pos_y", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("ts_pos_z", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("ts_maxprobe_z", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("ts_maxprobe_xy", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("ts_vel_for_travel", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("ts_vel_for_search", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("ts_vel_for_probe", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("ts_height", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("ts_clearance_z", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("ts_clearance_xy", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("ts_latch", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("ts_latch_maxprobe", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("ts_diam_ext", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("ts_diam_hole", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("ts_diam_offset", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("ts_rot_speed", hal.HAL_FLOAT, hal.HAL_IN)

        # init Tickbox from gui for enable disable remap (with saving pref)
        self.halcomp.newpin("ts_chk_use_tool_measurement", hal.HAL_BIT, hal.HAL_OUT)
        self.chk_use_tool_measurement = self.builder.get_object("chk_use_tool_measurement")
        self.chk_use_tool_measurement.set_active(self.prefs.getpref("ts_chk_use_tool_measurement", False, bool))
        self.halcomp["ts_chk_use_tool_measurement"] = self.chk_use_tool_measurement.get_active()
        self.hal_led_set_m6.hal_pin.set(self.chk_use_tool_measurement.get_active())
        if self.chk_use_tool_measurement.get_active():
            self.frm_tool_measurement.set_sensitive(False)
        else:
            self.frm_tool_measurement.set_sensitive(True)

        # init Tickbox from gui for enable rotating spindle (without saving pref)
        self.halcomp.newpin("ts_chk_rot_spindle_reverse", hal.HAL_BIT, hal.HAL_OUT)
        self.chk_use_rotate_spindle = self.builder.get_object("chk_use_rotate_spindle")
        # reading/saving pref is not wanted for rotation so we want to start with 0
        self.halcomp["ts_chk_rot_spindle_reverse"] = 0
        self.hal_led_rotate_spindle.hal_pin.set(0)


        self._init_tool_setter_data()

    # Read the ini file config [TOOL_SETTER] section
    def _init_tool_setter_data(self):
        ts_pos_x = self.inifile.find("TOOL_SETTER", "X")
        ts_pos_y = self.inifile.find("TOOL_SETTER", "Y")
        ts_pos_z = self.inifile.find("TOOL_SETTER", "Z")
        ts_maxprobe_z = self.inifile.find("TOOL_SETTER", "MAXPROBE_Z")
        ts_maxprobe_xy = self.inifile.find("TOOL_SETTER", "MAXPROBE_XY")
        ts_vel_for_travel = self.inifile.find("TOOL_SETTER", "VEL_FOR_TRAVEL")
        ts_vel_for_search = self.inifile.find("TOOL_SETTER", "VEL_FOR_SEARCH")
        ts_vel_for_probe = self.inifile.find("TOOL_SETTER", "VEL_FOR_PROBE")
        ts_height = self.inifile.find("TOOL_SETTER", "TS_HEIGHT")
        ts_clearance_z = self.inifile.find("TOOL_SETTER", "CLEARANCE_Z")
        ts_clearance_xy = self.inifile.find("TOOL_SETTER", "CLEARANCE_XY")
        ts_latch = self.inifile.find("TOOL_SETTER", "LATCH")
        ts_latch_maxprobe = self.inifile.find("TOOL_SETTER", "LATCH_MAXPROBE")
        ts_diam_ext = self.inifile.find("TOOL_SETTER", "DIAMETER_EXT")
        ts_diam_hole = self.inifile.find("TOOL_SETTER", "DIAMETER_HOLE")
        ts_diam_offset = self.inifile.find("TOOL_SETTER", "DIAM_OFFSET")
        ts_rot_speed = self.inifile.find("TOOL_SETTER", "REV_ROT_SPEED")

        if (
            ts_pos_x is None
            or ts_pos_y is None
            or ts_pos_z is None
            or ts_maxprobe_z is None
            or ts_maxprobe_xy is None
            or ts_vel_for_travel is None
            or ts_vel_for_search is None
            or ts_vel_for_probe is None
            or ts_height is None
            or ts_clearance_z is None
            or ts_clearance_xy is None
            or ts_latch is None
            or ts_latch_maxprobe is None
            or ts_diam_ext is None
            or ts_diam_hole is None
            or ts_diam_offset is None
            or ts_rot_speed is None
           ):
            self.chk_use_tool_measurement.set_active(False)
            self.frm_tool_measurement.set_sensitive(False)

            message   = _("Invalidate REMAP M6")
            secondary = _("Please check the TOOL_SETTER INI configurations")
            self.warning_dialog(message, secondary)
            return 0
        else:

            self.halcomp["ts_pos_x"] = float(ts_pos_x)
            self.halcomp["ts_pos_y"] = float(ts_pos_y)
            self.halcomp["ts_pos_z"] = float(ts_pos_z)
            self.halcomp["ts_maxprobe_z"] = float(ts_maxprobe_z)
            self.halcomp["ts_maxprobe_xy"] = float(ts_maxprobe_xy)
            self.halcomp["ts_vel_for_travel"] = float(ts_vel_for_travel)
            self.halcomp["ts_vel_for_search"] = float(ts_vel_for_search)
            self.halcomp["ts_vel_for_probe"] = float(ts_vel_for_probe)
            self.halcomp["ts_height"] = float(ts_height)
            self.halcomp["ts_clearance_z"] = float(ts_clearance_z)
            self.halcomp["ts_clearance_xy"] = float(ts_clearance_xy)
            self.halcomp["ts_latch"] = float(ts_latch)
            self.halcomp["ts_latch_maxprobe"] = float(ts_latch_maxprobe)
            self.halcomp["ts_diam_ext"] = float(ts_diam_ext)
            self.halcomp["ts_diam_hole"] = float(ts_diam_hole)
            self.halcomp["ts_diam_offset"] = float(ts_diam_offset)
            self.halcomp["ts_rot_speed"] = float(ts_rot_speed)

            # at startup read the ini but alter the value with saved pref         "todo think about remove that
            self.spbtn_setter_height.set_value(self.prefs.getpref("ts_height", 0.0, float))
            self.spbtn_setter_height.set_value(self.halcomp["ts_height"])
            self.halcomp["ts_height"] = self.spbtn_setter_height.get_value()




    # --------------------------
    #
    #  Generic tool setter Movement Methods
    #
    # --------------------------
    def ts_clearance_z_down(self, data=None):
        # move Z - clearance_z
        s = """G91
        G1 Z-%f
        G90""" % (self.halcomp["ts_clearance_z"])
        if self.gcode(s) == -1:
            return -1
        return 0

    def ts_clearance_z_up(self, data=None):
        # move Z + clearance_z
        s = """G91
        G1 Z%f
        G90""" % (self.halcomp["ts_clearance_z"])
        if self.gcode(s) == -1:
            return -1
        return 0



    # --------------------------
    #
    # Remap M6 Buttons
    #
    # --------------------------

    # Spinbox for setter height with override value from GUI but at each startup use INI value
    def on_spbtn_setter_height_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("ts_height", gtkspinbutton, data)

    def on_spbtn_setter_height_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("ts_height", gtkspinbutton, data)

    # Tickbox from gui for enable disable remap (with saving pref)
    def on_chk_use_tool_measurement_toggled(self, gtkcheckbutton, data=None):
        self.halcomp["ts_chk_use_tool_measurement"] = gtkcheckbutton.get_active()
        self.hal_led_set_m6.hal_pin.set(gtkcheckbutton.get_active())
        self.prefs.putpref("ts_chk_use_tool_measurement", gtkcheckbutton.get_active(), bool)
        if gtkcheckbutton.get_active():
            self.frm_tool_measurement.set_sensitive(False)
        else:
            self.frm_tool_measurement.set_sensitive(True)

    # Tickbox from gui for enable rotating spindle (without saving pref)
    def on_chk_use_rotate_spindle_toggled(self, gtkcheckbutton, data=None):
        self.halcomp["ts_chk_rot_spindle_reverse"] = gtkcheckbutton.get_active()
        self.hal_led_rotate_spindle.hal_pin.set(gtkcheckbutton.get_active())
        # saving pref is not wanted  for rotation


    # Down probe to table for measuring it and use for calculate tool setter height and can set G10 L20 Z0 if you tick auto zero
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_probe_table_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [3]") == -1:
            return
        if self.ocode("o<psng_load_var_tool_setter> call") == -1:
            return
#        if self.ocode("o<psng_config_check> call") == -1:
#            return
        if self.ocode("o<psng_probe_table> call") == -1:
            return
        a = self.stat.probed_position
        ptres = float(a[2])
        if self.halcomp["chk_touch_plate_selected"] == True:
            ptresplate = float(a[2]) - self.halcomp["tp_z_full_thickness"]
            print("probed_table with TOUCH-PLATE  = ", ptresplate)
        self.halcomp["probed_table"] = ptres
        print("probed_table with 3D-PROBE  = ", ptres)
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "Z",
            z=ptres,
        )
        # Optional auto zerro selectable from gui
        self.set_zerro("Z", 0, 0, ptres)                                         # Using auto zero tickbox
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # Down probe to tool setter for measuring it vs table probing result
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_probe_tool_setter_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [4]") == -1:
            return
        if self.ocode("o<psng_load_var_tool_setter> call") == -1:
            return
#        if self.ocode("o<psng_config_check> call") == -1:
#            return
        if self.ocode("o<psng_probe_setter> call") == -1:
            return
        a = self.stat.probed_position
        tsres = (float(a[2]) - self.halcomp["ts_probed_table"])
        print("ts_height  = ", tsres)
        print("ts_probed_table  = ", self.halcomp["ts_probed_table"])
        self.spbtn_setter_height.set_value(tsres)
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "Z",
            z=tsres,
        )
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # Down drill bit to tool setter for measuring it
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_tool_length_released(self, gtkbutton, data=None):
        tooltable = self.inifile.find("EMCIO", "TOOL_TABLE")
        if not tooltable:
            message   = _("Tool Measurement Error")
            secondary = _("Did not find a toolfile file in [EMCIO] TOOL_TABLE")
            self.error_dialog(message, secondary=secondary)
            return
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [6]") == -1:
            return
        if self.ocode("o<psng_load_var_tool_setter> call") == -1:
            return
#        if self.ocode("o<psng_config_check> call") == -1:
#            return
        if self.ocode("o<psng_tool_length> call") == -1:
            return
        a = self.stat.probed_position
        tlres = (float(a[2]) - self.halcomp["ts_height"])
        self.halcomp["ts_probed_tool_z"] = tlres
        print("tool length  = ", tlres)
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "Z",
            z=tlres,
        )
        s = "G10 L1 P0 Z%f" % (tlres)
        if self.gcode(s) == -1:
            return
        if self.gcode(G43) == -1:
            return
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # --------------------------
    #
    # TOOL TABLE CREATOR
    #
    # --------------------------
    # TOOL DIA : use X only for find tool setter center and use after that more accurate Y center value for determinig tool diameter
    # + TOOL length Z and the whole sequence is saved as tooltable for later use
    # IMH this sequence need to be first with probe : first execute psng_down for determinate the table height with toolsetter and think about updating tool setter diameter or probe diameter at same time
    # IMH this sequence need to be done secondly with other tool using button Dia only off course
    # ALL OF THIS NEED TO EDIT TOOL TABLE MANUALLY FOR ADD NEW TOOL AND (approximative) KNOW DIAMETER
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_tool_dia_released(self, gtkbutton, data=None):
        tooltable = self.inifile.find("EMCIO", "TOOL_TABLE")
        if not tooltable:
            message   = _("Tool Measurement Error")
            secondary = _("Did not find a toolfile file in [EMCIO] TOOL_TABLE")
            self.error_dialog(message, secondary=secondary)
            return
        toolnumber = Popen("halcmd getp iocontrol.0.tool-number", shell=True, stdout=PIPE).stdout.read()
        tooldiameter = float(Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read())
        print("tool-number  = ", toolnumber)
        print("tooldiameter from halui  = ", tooldiameter)

        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [2]") == -1:
            return
        if self.ocode("o<psng_load_var_tool_setter> call") == -1:
            return
#        if self.ocode("o<psng_config_check> call") == -1:
#            return
        if self.ocode("o<psng_tool_diameter> call") == -1:
            return

        # show Z result
        a = self.probed_position_with_offsets()
        tlres = ((float(a[2])) - self.halcomp["ts_height"])
        self.halcomp["ts_probed_tool_z"] = tlres

        # move X +
        tmpx = (0.5 * (self.halcomp["ts_diam_ext"] + tooldiameter) + self.halcomp["ts_clearance_xy"])
        s = """G91
        G1 X-%f
        G90""" % (tmpx)
        if self.gcode(s) == -1:
            return

        if self.ocode("o<psng_tool_diameter_check> call") == -1:
            message   = _("TOOL DIAMETER MEASUREMENT STOPPED")
            self.error_dialog(message)
            return

        if self.ts_clearance_z_down() == -1:
            return
        # Start psng_xplus.ngc var already loaded from ini by Start psng_tool_diameter.ngc
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return
        # show X result
        a = self.probed_position_with_offsets()
        xpres = float(a[0]) + 0.5 * self.halcomp["ts_diam_ext"]
        #    print("xpres = ",xpres)
        # move Z temporary away from probing position
        if self.ts_clearance_z_up() == -1:
            return

        # move X -
        tmpx = (self.halcomp["ts_diam_ext"] + tooldiameter) + (2*self.halcomp["ts_clearance_xy"])
        s = """G91
        G1 X%f
        G90""" % (tmpx)
        if self.gcode(s) == -1:
            return
        if self.ts_clearance_z_down() == -1:
            return
        # Start psng_xminus.ngc var already loaded from ini by Start psng_tool_diameter.ngc
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return
        # show X result
        a = self.probed_position_with_offsets()
        xmres = float(a[0]) - 0.5 * self.halcomp["ts_diam_ext"]
        #    print("xmres = ",xmres)
        self.length_x()                                #used for clear display ??????????????
        xcres = 0.5 * (xpres + xmres)


        # move Z temporary away from probing position
        if self.ts_clearance_z_up() == -1:
            return
        # go to the new center of X
        s = "G1 X%f" % (xcres)
        print("xcenter = ",xcres)
        if self.gcode(s) == -1:
            return


        # move Y +
        tmpy = (0.5 * (self.halcomp["ts_diam_ext"] + tooldiameter) + self.halcomp["ts_clearance_xy"])
        s = """G91
        G1 Y-%f
        G90""" % (tmpy)
        if self.gcode(s) == -1:
            return
        if self.ts_clearance_z_down() == -1:
            return
        # Start psng_yplus.ngc var already loaded from ini by Start psng_tool_diameter.ngc
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return
        # show Y result
        a = self.probed_position_with_offsets()
        ypres = float(a[1]) + 0.5 * self.halcomp["ts_diam_ext"]
        print("simple probed pos Y+ = ",self.stat.probed_position)
        print("ypres = ",ypres)
        # move Z temporary away from probing position
        if self.ts_clearance_z_up() == -1:
            return

        # move Y -
        tmpy = (self.halcomp["ts_diam_ext"] + tooldiameter) + (2*self.halcomp["ts_clearance_xy"])
        s = """G91
        G1 Y%f
        G90""" % (tmpy)
        if self.gcode(s) == -1:
            return
        if self.ts_clearance_z_down() == -1:
            return
        # Start psng_yminus.ngc var already loaded from ini by Start psng_tool_diameter.ngc
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return

        # show Y result
        a = self.probed_position_with_offsets()
        ymres = float(a[1]) - 0.5 * self.halcomp["ts_diam_ext"]
        print("simple probed pos Y- = ", self.stat.probed_position)
        print("ymres = ",ymres)
        self.length_y()                                #used for clear display ??????????????
        ycres = 0.5 * (ypres + ymres)
        print("ycres = ",ycres)

        diamres = ymres - ypres
        diamwithofsset = diamres + (2*self.halcomp["ts_diam_offset"])
        self.halcomp["ts_probed_tool_diam"] = diamwithofsset
        self.add_history_text("old tooldiameter from tooltable = %.4f" % (tooldiameter))
        self.add_history_text("new tooldiameter measured = %.4f" % (diamres))
        self.add_history_text("new tooldiameter compensated set in tootlable = %.4f" % (diamwithofsset))

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XcYcZD",
            xc=xcres,
            yc=ycres,
            z=tlres,
            d=diamwithofsset,
        )
        s = "G10 L1 P0 Z%f R%f" % ((tlres),(0.5*diamwithofsset))           # 0.14 seem to be needed for my setter adding the necessary distance for radial triggering probe (0.07mm each direction)
        if self.gcode(s) == -1:
            return
        if self.gcode(G43) == -1:
            return
        if self.ocode("o<psng_tool_diameter_end> call") == -1:                          # replace Z clearence and goto new center Y with return to tool change positon
            return
        if self.ocode("o<backup_restore> call [999]") == -1:
            return



#    # Here we create a manual tool change dialog
#    def on_tool_change(self, gtkbutton, data=None):
#        change = self.halcomp["toolchange-change"]
#        toolnumber = Popen("halcmd getp iocontrol.0.tool-number", shell=True, stdout=PIPE).stdout.read()
#        toolprepnumber = self.halcomp["toolchange-prep-number"]
#        self.add_history_text("tool-number = %.4f" % (toolnumber))
#        self.add_history_text("tool_prep_number = %.4f" % (toolprepnumber))
#        print("tool-number = %.4f" % (toolnumber))
#        print("tool_prep_number = %.4f" % (toolprepnumber))
#        if self.usepopup == 0:
#                 result = 0
#
## One issue need to be corrected if you ask the same tool as actual tool probe start without any confirmation (patched in ocode with M0)
## One issue need to be corrected if you ask the same tool as actual tool probe start without any confirmation (need to patch here if use stglue.py)
#
#        if change:
#            # if toolprepnumber = 0 we will get an error because we will not be able to get
#            # any tooldescription, so we avoid that case
#            if toolprepnumber == 0:
#                if self.usepopup == 0:
#                      result = 1
#                elif self.usepopup == 1:
#                      message   = _("Please remove the mounted tool and press OK when done or CLOSE popup for cancel")
#                      self.warning_dialog(message, title=_("PSNG Manual Toolchange"))
#            elif toolprepnumber == toolnumber:
#                if self.usepopup == 0:
#                      result = 1
#                elif self.usepopup == 1:
#                      message   = _("Please check if the mounted tool is the good one and press OK when done or CLOSE popup for cancel")
#                      self.warning_dialog(message, title=_("PSNG Manual Toolchange"))
#            else:
#                tooltable = self.inifile.find("EMCIO", "TOOL_TABLE")
#                if not tooltable:
#                    message   = _("Tool Measurement Error")
#                    secondary = _("Did not find a toolfile file in [EMCIO] TOOL_TABLE")
#                    self.error_dialog(message, secondary, title=_("PSNG Manual Toolchange"))
#                    return
#                CONFIGPATH = os.environ["CONFIG_DIR"]
#                toolfile = os.path.join(CONFIGPATH, tooltable)
#                self.tooledit1.set_filename(toolfile)
#                tooldescr = self.tooledit1.get_toolinfo(toolprepnumber)[16]
#                if self.usepopup == 0:
#                      result = 1
#                elif self.usepopup == 1:
#                      message = _(
#                          "Please change to tool\n\n# {0:d}     {1}\n\n then click OK or CLOSE popup for cancel"
#                      ).format(toolprepnumber, tooldescr)
#
#            if self.usepopup == 1:
#                 result = self.warning_dialog(message, title=_("PSNG Manual Toolchange"))
#            if result:
#                #self.vcp_reload()                                     # DO NOT DO THAT OR AUTOLENGHT IS KILLED
#                self.add_history_text("TOOLCHANGED CORRECTLY")
#                self.halcomp["toolchange-changed"] = True
#            else:
#                self.halcomp["toolchange-prep-number"] = toolnumber
#                self.halcomp["toolchange-change"] = False  # Is there any reason to do this to input pin ?
#                self.halcomp["toolchange-changed"] = True
#                message = _("TOOLCHANGE ABORTED")
#                self.error_dialog(message, title=_("PSNG Manual Toolchange"))
#        else:
#            self.halcomp["toolchange-changed"] = False
