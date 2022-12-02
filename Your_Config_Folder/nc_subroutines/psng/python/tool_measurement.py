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

        # connect the frame for allow to inhibit
        self.frm_tool_measurement = self.builder.get_object("frm_tool_measurement")

        # for manual tool change dialog
        self.halcomp.newpin("toolchange_number", hal.HAL_S32, hal.HAL_IN)
        self.halcomp.newpin("toolchange_prep_number", hal.HAL_S32, hal.HAL_IN)
        self.halcomp.newpin("toolchange_changed", hal.HAL_BIT, hal.HAL_OUT)
        pin = self.halcomp.newpin("toolchange_change", hal.HAL_BIT, hal.HAL_IN)
        hal_glib.GPin(pin).connect("value_changed", self.on_tool_change)

        self.halcomp.newpin("toolchange_diameter", hal.HAL_FLOAT, hal.HAL_IN)

        # make the Tickbox
        self.chk_use_tool_measurement = self.builder.get_object("chk_use_tool_measurement")
        self.chk_use_rot_spindle_reverse = self.builder.get_object("chk_use_rot_spindle_reverse")

        # make the LED
        self.hal_led_use_tool_measurement = self.builder.get_object("hal_led_use_tool_measurement")
        self.hal_led_use_rot_spindle_reverse = self.builder.get_object("hal_led_use_rot_spindle_reverse")

        # make the pins hal
        self.halcomp.newpin("ts_popup_tool_number", hal.HAL_S32, hal.HAL_OUT)
        self.halcomp.newpin("ts_popup_tool_diameter", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_popup_tool_is_spherical", hal.HAL_BIT, hal.HAL_OUT)

        self.halcomp.newpin("ts_pos_x", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_pos_y", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_vel_for_travel", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_vel_for_search", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_vel_for_probe", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_latch", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_latch_probed", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_height", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_clearance_xyz", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_max_tool_lgt", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_max_tool_dia", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_min_tool_dia", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_tool_rot_speed", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_pad_diameter", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_pad_diameter_offset", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_pad_thickness", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_pad_from_body", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_pad_is_hole", hal.HAL_BIT, hal.HAL_OUT)

        self.halcomp.newpin("chk_use_popup_style_toolchange", hal.HAL_BIT, hal.HAL_OUT)
        self.halcomp.newpin("toolchange_go_back_last_position", hal.HAL_BIT, hal.HAL_OUT)
        self.halcomp.newpin("toolchange_z_travel_position", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("toolchange_with_spindle_on", hal.HAL_BIT, hal.HAL_OUT)
        self.halcomp.newpin("toolchange_with_diam_measurement", hal.HAL_BIT, hal.HAL_OUT)
        self.halcomp.newpin("toolchange_quill_up", hal.HAL_BIT, hal.HAL_OUT)
        self.halcomp.newpin("toolchange_pos_x", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("toolchange_pos_y", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("toolchange_pos_z", hal.HAL_FLOAT, hal.HAL_OUT)

        self.halcomp.newpin("chk_use_tool_measurement", hal.HAL_BIT, hal.HAL_OUT)
        self.halcomp.newpin("chk_use_rot_spindle_reverse", hal.HAL_BIT, hal.HAL_OUT)


        # load value regarding to the pref saved
        self.chk_use_tool_measurement.set_active(self.prefs.getpref("chk_use_tool_measurement", False, bool))
        self.halcomp["chk_use_tool_measurement"] = self.chk_use_tool_measurement.get_active()
        self.hal_led_use_tool_measurement.hal_pin.set(self.halcomp["chk_use_tool_measurement"])

        if self.halcomp["chk_use_tool_measurement"]:
            self.frm_tool_measurement.set_sensitive(False)
        else:
            self.frm_tool_measurement.set_sensitive(True)

        # After getting value we need to init some of them
        self._init_tool_setter_data()


    # --------------------------
    #
    # Read the ini file config [TOOL_SETTER] section
    #
    # --------------------------
    def _init_tool_setter_data(self):
        ts_pos_x = self.inifile.find("TOOL_SETTER", "TS_POS_X")
        ts_pos_y = self.inifile.find("TOOL_SETTER", "TS_POS_Y")
        ts_height = self.inifile.find("TOOL_SETTER", "TS_HEIGHT")
        ts_vel_for_travel = self.inifile.find("TOOL_SETTER", "VEL_FOR_TRAVEL")
        ts_vel_for_search = self.inifile.find("TOOL_SETTER", "VEL_FOR_SEARCH")
        ts_vel_for_probe = self.inifile.find("TOOL_SETTER", "VEL_FOR_PROBE")
        ts_latch = self.inifile.find("TOOL_SETTER", "LATCH")
        ts_latch_probed = self.inifile.find("TOOL_SETTER", "LATCH_PROBED")
        ts_clearance_xyz = self.inifile.find("TOOL_SETTER", "CLEARANCE_XYZ")
        ts_max_tool_lgt = self.inifile.find("TOOL_SETTER", "TS_MAX_TOOL_LGT")
        ts_max_tool_dia = self.inifile.find("TOOL_SETTER", "TS_MAX_TOOL_DIA")
        ts_min_tool_dia = self.inifile.find("TOOL_SETTER", "TS_MIN_TOOL_DIA")
        ts_tool_rot_speed = self.inifile.find("TOOL_SETTER", "TOOL_ROT_SPEED")
        ts_pad_diameter = self.inifile.find("TOOL_SETTER", "PAD_DIAMETER")
        ts_pad_diameter_offset = self.inifile.find("TOOL_SETTER", "PAD_DIAMETER_OFFSET")
        ts_pad_thickness = self.inifile.find("TOOL_SETTER", "PAD_THICKNESS")
        ts_pad_from_body = self.inifile.find("TOOL_SETTER", "PAD_FROM_BODY")
        ts_pad_is_hole = self.inifile.find("TOOL_SETTER", "PAD_IS_HOLE")
        chk_use_popup_style_toolchange = self.inifile.find("TOOL_CHANGE", "POPUP_STYLE")
        toolchange_go_back_last_position = self.inifile.find("TOOL_CHANGE", "GO_BACK_LAST_POSITION")
        toolchange_z_travel_position = self.inifile.find("TOOL_CHANGE", "Z_TRAVEL_POSITION")
        toolchange_with_diam_measurement = self.inifile.find("TOOL_CHANGE", "WITH_DIAM_MEASUREMENT")
        toolchange_with_spindle_on = self.inifile.find("EMCIO", "TOOL_CHANGE_WITH_SPINDLE_ON")
        toolchange_quill_up = self.inifile.find("EMCIO", "TOOL_CHANGE_QUILL_UP")
        toolchange_pos_x = self.inifile.find("TOOL_CHANGE", "POS_X")
        toolchange_pos_y = self.inifile.find("TOOL_CHANGE", "POS_Y")
        toolchange_pos_z = self.inifile.find("TOOL_CHANGE", "POS_Z")

        if (
            ts_pos_x is None
            or ts_pos_y is None
            or ts_height is None
            or ts_vel_for_travel is None
            or ts_vel_for_search is None
            or ts_vel_for_probe is None
            or ts_latch is None
            or ts_latch_probed is None
            or ts_clearance_xyz is None
            or ts_max_tool_lgt is None
            or ts_max_tool_dia is None
            or ts_min_tool_dia is None
            or ts_tool_rot_speed is None
            or ts_pad_diameter is None
            or ts_pad_diameter_offset is None
            or ts_pad_thickness is None
            or ts_pad_from_body is None
            or ts_pad_is_hole is None
            or chk_use_popup_style_toolchange is None
            or toolchange_go_back_last_position is None
            or toolchange_z_travel_position is None
            or toolchange_with_diam_measurement is None
            or toolchange_with_spindle_on is None
            or toolchange_quill_up is None
            or toolchange_pos_x is None
            or toolchange_pos_y is None
            or toolchange_pos_z is None
           ):
            self.chk_use_tool_measurement.set_active(False)
            self.frm_tool_measurement.set_sensitive(False)

            self.warning_dialog("Invalidate REMAP M6", "Please check the TOOL_SETTER INI configurations", title=_("PSNG Manual Toolchange"))
            return 0
        else:

            self.halcomp["ts_pos_x"] = float(ts_pos_x)
            self.halcomp["ts_pos_y"] = float(ts_pos_y)
            self.halcomp["ts_height"] = float(ts_height)
            self.halcomp["ts_vel_for_travel"] = float(ts_vel_for_travel)
            self.halcomp["ts_vel_for_search"] = float(ts_vel_for_search)
            self.halcomp["ts_vel_for_probe"] = float(ts_vel_for_probe)
            self.halcomp["ts_latch"] = float(ts_latch)
            self.halcomp["ts_latch_probed"] = float(ts_latch_probed)
            self.halcomp["ts_clearance_xyz"] = float(ts_clearance_xyz)
            self.halcomp["ts_max_tool_lgt"] = float(ts_max_tool_lgt)
            self.halcomp["ts_max_tool_dia"] = float(ts_max_tool_dia)
            self.halcomp["ts_min_tool_dia"] = float(ts_min_tool_dia)
            self.halcomp["ts_tool_rot_speed"] = float(ts_tool_rot_speed)
            self.halcomp["ts_pad_diameter"] = float(ts_pad_diameter)
            self.halcomp["ts_pad_diameter_offset"] = float(ts_pad_diameter_offset)
            self.halcomp["ts_pad_thickness"] = float(ts_pad_thickness)
            self.halcomp["ts_pad_from_body"] = float(ts_pad_from_body)
            self.halcomp["ts_pad_is_hole"] = float(ts_pad_is_hole)
            self.halcomp["chk_use_popup_style_toolchange"] = float(chk_use_popup_style_toolchange)
            self.halcomp["toolchange_go_back_last_position"] = float(toolchange_go_back_last_position)
            self.halcomp["toolchange_z_travel_position"] = float(toolchange_z_travel_position)
            self.halcomp["toolchange_with_diam_measurement"] = float(toolchange_with_diam_measurement)
            self.halcomp["toolchange_with_spindle_on"] = float(toolchange_with_spindle_on)
            self.halcomp["toolchange_quill_up"] = float(toolchange_quill_up)
            self.halcomp["toolchange_pos_x"] = float(toolchange_pos_x)
            self.halcomp["toolchange_pos_y"] = float(toolchange_pos_y)
            self.halcomp["toolchange_pos_z"] = float(toolchange_pos_z)


    # --------------------------
    #
    # Thickbox for Remap M6 Buttons  (with saving pref)
    #
    # --------------------------
    def on_chk_use_tool_measurement_toggled(self, gtkcheckbutton):
        self.halcomp["chk_use_tool_measurement"] = gtkcheckbutton.get_active()
        self.hal_led_use_tool_measurement.hal_pin.set(gtkcheckbutton.get_active())
        self.prefs.putpref("chk_use_tool_measurement", gtkcheckbutton.get_active(), bool)
        if gtkcheckbutton.get_active():
            self.frm_tool_measurement.set_sensitive(False)
            self.add_history_text("Auto length for remap M6 is activated")
        else:
            self.frm_tool_measurement.set_sensitive(True)
            self.add_history_text("Auto length for remap M6 is not activated")

    # Tickbox from gui for enable rotating spindle (without saving pref)
    def on_chk_use_rot_spindle_reverse_toggled(self, gtkcheckbutton):
        self.halcomp["chk_use_rot_spindle_reverse"] = gtkcheckbutton.get_active()
        self.hal_led_use_rot_spindle_reverse.hal_pin.set(gtkcheckbutton.get_active())
        # self.prefs.putpref is not wanted for rotation
        if gtkcheckbutton.get_active():
            self.add_history_text("Auto spindle reverse rotation is activated")
        else:
            self.add_history_text("Auto spindle reverse rotation is not activated")


    # --------------------------
    #
    # Remap M6 Buttons
    #
    # --------------------------

    # Down probe to tool setter for measuring it vs table probing result
    @ProbeScreenBase.ensure_errors_dismissed
    @ProbeScreenBase.ensure_is_not_touchplate
    def on_btn_probe_tool_setter_released(self, gtkbutton):
        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [0] [1]") == -1:
            return
        if self.ocode("o<psng_hook> call [4]") == -1:
            return

        # ask confirm from popup
        if self._dialog_confirm("probe_tool_setter") == -1:
            self.warning_dialog("probe_tool_setter canceled by user !")
            return

        # Start psng_probe_setter_height
        if self.ocode("o<psng_probe_setter_height> call") == -1:
            return

        # Calculate Z result
        a = self.stat.probed_position
        tsres = (float(a[2]) - self.halcomp["offs_table_offset"])

        # save and show the probed point
        # update setter height gui value you need to edit manually ini file after that
        #self.halcomp["ts_height"] = tsres
        self.add_history_text("ts_height : %s" % (tsres))
        self.add_history_text("table_offset = %.4f" % (self.halcomp["offs_table_offset"]))
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "Z",
            z=tsres,
        )
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0


    # --------------------------
    #
    # TOOL TABLE CREATOR
    #
    # --------------------------

    # --------------------------
    # Down drill bit to tool setter for measuring it
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_tool_length_released(self, gtkbutton):
        tooltable = self.inifile.find("EMCIO", "TOOL_TABLE")
        if not tooltable:
            self.warning_dialog("Tool Measurement Error", "Did not find a toolfile file in [EMCIO] TOOL_TABLE", title=_("PSNG Manual Toolchange"))
            return

        # ask new tool number and diameter from popup
        if self._dialog_spbtn_ask_toolnumber() == -1:
            self.warning_dialog("Tool number to probe canceled by user !")
            return
        else:
            self.add_history_text("ts_popup_tool_number = %d" % (self.halcomp["ts_popup_tool_number"]))
            self.add_history_text("ts_popup_tool_diameter = %d" % (self.halcomp["ts_popup_tool_diameter"]))

        if self.halcomp["ts_pad_diameter"] < self.halcomp["ts_popup_tool_diameter"] :
            self.warning_dialog("Tool diameter is higher than pad TODO ADD A OFFSET FOR ALLOW TO MEASURE ON FLUTE !")
            if self.halcomp["ts_pad_is_hole"]:
                self.warning_dialog("Tool diameter is higher than pad hole so we can't measure it !")
                return

        s = "M61 Q%s" % (self.halcomp["ts_popup_tool_number"])
        if self.gcode(s) == -1:
            return

        # update and reload tool table
        s = "G10 L1 P#<_current_tool> R%f G43" % (0.5 * self.halcomp["ts_popup_tool_diameter"])
        if self.gcode(s) == -1:
            return

        # safety check
        if self.halcomp["ts_popup_tool_number"] != hal.get_value("iocontrol.0.tool-number"): #self.halcomp["toolchange_number"]:
            self.warning_dialog("Tool number mismatch !", title=_("PSNG Manual Toolchange"))
            return

        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [1] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [6]") == -1:
            return

        # Start psng_probe_tool_length
        if self.ocode("o<psng_probe_tool_length> call") == -1:
            return

        self.halcomp["ts_popup_tool_number"] = 0
        self.halcomp["ts_popup_tool_diameter"] = 0

        self.add_history_text("Measured tool_length = %f" % hal.get_value("halui.tool.length_offset.z")) #(float(Popen("halcmd getp halui.tool.length_offset.z", shell=True, stdout=PIPE).stdout.read())))
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0



    # --------------------------
    # TOOL DIA : use X only for find tool setter center and use after that more accurate Y center value for determinig tool diameter
    # + TOOL length Z and the whole sequence is saved as tooltable for later use
    # IMH this sequence need to be first with probe : first execute psng_down for determinate the table height with toolsetter and think about updating tool setter diameter or probe diameter at same time
    # IMH this sequence need to be done secondly with other tool using button Dia only off course
    # ALL OF THIS NEED TO EDIT TOOL TABLE MANUALLY FOR ADD NEW TOOL AND (approximative) KNOW DIAMETER
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_tool_dia_released(self, gtkbutton):
        tooltable = self.inifile.find("EMCIO", "TOOL_TABLE")
        if not tooltable:
            self.warning_dialog("Tool Measurement Error", "Did not find a toolfile file in [EMCIO] TOOL_TABLE", title=_("PSNG Manual Toolchange"))
            return

        # ask new tool number and diameter from popup
        if self._dialog_spbtn_ask_toolnumber_diameter() == -1:
            self.warning_dialog("Tool diameter to probe canceled by user !")
            return
        else:
            self.add_history_text("ts_popup_tool_number = %d" % (self.halcomp["ts_popup_tool_number"]))
            self.add_history_text("ts_popup_tool_diameter = %d" % (self.halcomp["ts_popup_tool_diameter"]))
            self.add_history_text("ts_popup_tool_is_spherical = %d" % (self.halcomp["ts_popup_tool_is_spherical"]))


        s = "M61 Q%s" % (self.halcomp["ts_popup_tool_number"])
        if self.gcode(s) == -1:
            return

        # update and reload tool table
        s = "G10 L1 P#<_current_tool> R%f G43" % (0.5 * self.halcomp["ts_popup_tool_diameter"])
        if self.gcode(s) == -1:
            return

        if self.halcomp["ts_max_tool_dia"] < self.halcomp["ts_popup_tool_diameter"] or (self.halcomp["ts_pad_is_hole"] and self.halcomp["ts_pad_diameter"] <= self.halcomp["ts_popup_tool_diameter"]) or self.halcomp["ts_max_tool_dia"] <= 0:
            self.warning_dialog("Tool diameter is higher than allowed by ini config or by pad_is_hole !")
            return

        if self.halcomp["ts_min_tool_dia"] > self.halcomp["ts_popup_tool_diameter"] or self.halcomp["ts_min_tool_dia"] > self.halcomp["ts_max_tool_dia"] or self.halcomp["ts_min_tool_dia"] <= 0:
            self.warning_dialog("Tool diameter is lower than allowed by ini config !")
            return

        if self.halcomp["ts_pad_diameter"] < self.halcomp["ts_popup_tool_diameter"] :
            self.warning_dialog("Tool diameter is higher than pad TODO ADD A OFFSET FOR ALLOW TO MEASURE ON FLUTE !")

        # safety check
        if self.halcomp["ts_popup_tool_number"] != hal.get_value("iocontrol.0.tool-number"): #self.halcomp["toolchange_number"]:
            self.warning_dialog("Tool number mismatch !")
            return

        if self.ocode("o<backup_status_saving> call") == -1:
            return
        if self.ocode("o<psng_load_var> call [1] [0]") == -1:
            return
        if self.ocode("o<psng_hook> call [2]") == -1:
            return

        # Start psng_probe_tool_length
        if self.ocode("o<psng_probe_tool_diameter> call") == -1:
            return

        self.halcomp["ts_popup_tool_number"] = 0
        self.halcomp["ts_popup_tool_diameter"] = 0
        self.halcomp["ts_popup_tool_is_spherical"] = 0

        self.add_history_text("Measured tool_length = %f" % hal.get_value("halui.tool.length_offset.z")) #(float(Popen("halcmd getp halui.tool.length_offset.z", shell=True, stdout=PIPE).stdout.read())))
        self.add_history_text("Measured tool_diameter = %f" % hal.get_value("halui.tool.diameter")) #self.halcomp["toolchange_diameter"](self.halcomp["toolchange_diameter"]))
        if self.ocode("o<backup_status_restore> call [321]") == -1:
            return
        self._work_in_progress = 0


    # --------------------------
    #
    # TOOL CHANGE WITH AUTOLENGTH REACTING TO M6
    #
    # --------------------------
    # Here we create a manual tool change dialog
    def on_tool_change(self, gtkbutton):

# One issue need to be corrected if you ask the same tool as actual tool probe start without any confirmation (patched in ocode with M0)(need a patch here if use stglue.py)

        if self.halcomp["toolchange_change"]:

            tooltable = self.inifile.find("EMCIO", "TOOL_TABLE")
            if not tooltable:
                self.warning_dialog("Tool Measurement", "Did not find a toolfile file in [EMCIO] TOOL_TABLE", title=_("PSNG Manual Toolchange"))
                return
            CONFIGPATH = os.environ["CONFIG_DIR"]
            toolfile = os.path.join(CONFIGPATH, tooltable)
            self.tooledit1.set_filename(toolfile)

            #self.add_history_text("tool-number = %s" % (hal.get_value("iocontrol.0.tool-number")))
            #self.add_history_text("tool_prep_number = %s" % (self.halcomp["toolchange_prep_number"]))

            if self.halcomp["chk_use_popup_style_toolchange"]:
            	  # we will get an error because can't get any tooldescription, so we avoid that case
                if self.halcomp["toolchange_prep_number"] == 0:
                    message   = _("Please remove the mounted tool and press OK when done or CLOSE popup for cancel")
                elif self.halcomp["toolchange_prep_number"] == hal.get_value("iocontrol.0.tool-number"): #self.halcomp["toolchange_number"]:
                    message   = _("Please check if the mounted tool is the good one and press OK when done or CLOSE popup for cancel")
                else:
                    tooldescr = self.tooledit1.get_toolinfo(self.halcomp["toolchange_prep_number"])[16]
                    message = _(
                        "Please change to tool\n\n# {0:d}     {1}\n\n then click OK or CLOSE popup for cancel"
                    ).format(self.halcomp["toolchange_prep_number"], tooldescr)

                result = self.warning_dialog(message, title=_("PSNG Manual Toolchange"))
            else:
                result = 1

            if result:
                #self.vcp_reload()                                     # DO NOT DO THAT OR AUTOLENGTH IS KILLED
                self.add_history_text("TOOL %s CHANGED CORRECTLY" % (self.halcomp["toolchange_prep_number"]))
                self.halcomp["toolchange_changed"] = True
            else:
                self.halcomp["toolchange_prep_number"] = hal.get_value("iocontrol.0.tool-number") #self.halcomp["toolchange_number"]
                self.halcomp["toolchange_change"] = False  # Is there any reason to do this to input pin ? i think yes for be sure to reset connected self.on_tool_change
                self.halcomp["toolchange_changed"] = True
                self.error_dialog("TOOLCHANGE ABORTED", title=_("PSNG Manual Toolchange"))
        else:
            self.halcomp["toolchange_changed"] = False


