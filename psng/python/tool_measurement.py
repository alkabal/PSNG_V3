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

import os
import sys

import hal
import hal_glib

class ProbeScreenToolMeasurement(ProbeScreenBase):
    # --------------------------
    #
    #  INIT
    #
    # --------------------------
    def __init__(self, halcomp, builder, useropts):
        super(ProbeScreenToolMeasurement, self).__init__(halcomp, builder, useropts)

        self.hal_led_rotate_spindle = self.builder.get_object("hal_led_rotate_spindle")
        self.hal_led_set_m6 = self.builder.get_object("hal_led_set_m6")
        self.frm_tool_measurement = self.builder.get_object("frm_tool_measurement")
        self.spbtn_setter_height = self.builder.get_object("spbtn_setter_height")
        self.spbtn_block_height = self.builder.get_object("spbtn_block_height")
        self.btn_probe_tool_setter = self.builder.get_object("btn_probe_tool_setter")
        self.btn_probe_workpiece = self.builder.get_object("btn_probe_workpiece")
        self.btn_tool_dia = self.builder.get_object("btn_tool_dia")
        self.btn_tool_length = self.builder.get_object("btn_tool_length")
        self.tooledit1 = self.builder.get_object("tooledit1")
        self.chk_use_tool_measurement = self.builder.get_object("chk_use_tool_measurement")
        self.chk_use_rotate_spindle = self.builder.get_object("chk_use_rotate_spindle")

        self.chk_use_tool_measurement.set_active(self.prefs.getpref("use_tool_measurement", False, bool))


        # make the pins for tool measurement
        self.halcomp.newpin("probedtable", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("ts_height", hal.HAL_FLOAT, hal.HAL_OUT)
        self.halcomp.newpin("blockheight", hal.HAL_FLOAT, hal.HAL_OUT)
        
        # for manual tool change dialog
        #self.halcomp.newpin("toolchange-number", hal.HAL_S32, hal.HAL_IN)
        #self.halcomp.newpin("toolchange-prep-number", hal.HAL_S32, hal.HAL_IN)
        #self.halcomp.newpin("toolchange-changed", hal.HAL_BIT, hal.HAL_OUT)
        #pin = self.halcomp.newpin("toolchange-change", hal.HAL_BIT, hal.HAL_IN)
        #hal_glib.GPin(pin).connect("value_changed", self.on_tool_change)

        self.halcomp.newpin("use_tool_measurement", hal.HAL_BIT, hal.HAL_OUT)
        self.halcomp.newpin("use_rotate_spindle", hal.HAL_BIT, hal.HAL_OUT)

        if self.chk_use_tool_measurement.get_active():
            self.halcomp["use_tool_measurement"] = True
            self.hal_led_set_m6.hal_pin.set(1)

        if self.chk_use_rotate_spindle.get_active():
            self.halcomp["use_rotate_spindle"] = True
            self.hal_led_rotate_spindle.hal_pin.set(1)


        self.halcomp.newpin("tp_height", hal.HAL_FLOAT, hal.HAL_IN)
        self.halcomp.newpin("tp_lenght", hal.HAL_FLOAT, hal.HAL_IN)

        self.hal_led_use_touch_plate = self.builder.get_object("hal_led_use_touch_plate")

        self.chk_use_touch_plate = self.builder.get_object("chk_use_touch_plate")
        self.chk_use_touch_plate.set_active(self.prefs.getpref("use_touch_plate", False, bool))
        self.halcomp.newpin("use_touch_plate", hal.HAL_BIT, hal.HAL_OUT)

        if self.chk_use_touch_plate.get_active():
            self.halcomp["use_touch_plate"] = True
            self.hal_led_use_touch_plate.hal_pin.set(1)


        self._init_tool_setter_data()


        #
        #
        #
        #
        #
        #
        ############# NEED TO VERIFY IF this file need to convert some self.xy_ self.z_ and other like that vs other file use self.halcomp["xy_
        ############# I DO NOT REMENBER IF THIS IS WANTED FOR DIFFERENCIATE PROBE VS TOOLSETTER
        #
        #
        #
        #
        #
        #


    # Read the ini file config [TOOL_SETTER] section
    def _init_tool_setter_data(self):
        xpos = self.inifile.find("TOOL_SETTER", "X")
        ypos = self.inifile.find("TOOL_SETTER", "Y")
        zpos = self.inifile.find("TOOL_SETTER", "Z")
        z_maxprobe = self.inifile.find("TOOL_SETTER", "Z_MAXPROBE")
        xy_maxprobe = self.inifile.find("TOOL_SETTER", "XY_MAXPROBE")
        shearch_vel = self.inifile.find("TOOL_SETTER", "SEARCH_VEL")
        probe_vel = self.inifile.find("TOOL_SETTER", "PROBE_VEL")
        ts_height = self.inifile.find("TOOL_SETTER", "TS_HEIGHT")
        z_clearance = self.inifile.find("TOOL_SETTER", "Z_CLEARANCE")
        xy_clearance = self.inifile.find("TOOL_SETTER", "XY_CLEARANCE")
        latch = self.inifile.find("TOOL_SETTER", "LATCH")
        reverse_latch = self.inifile.find("TOOL_SETTER", "REVERSE_LATCH")
        ts_diam = self.inifile.find("TOOL_SETTER", "DIAMETER")
        ts_offset = self.inifile.find("TOOL_SETTER", "DIAM_OFFSET")
        revrott = self.inifile.find("TOOL_SETTER", "REV_ROT_SPEED")
        tp_height = self.inifile.find("TOOL_SETTER", "Z_PLATE_THICKNESS")
        tp_lenght = self.inifile.find("TOOL_SETTER", "XY_PLATE_THICKNESS")

        if (
            xpos is None
            or ypos is None
            or zpos is None
            or z_maxprobe is None
            or xy_maxprobe is None
            or shearch_vel is None
            or probe_vel is None
            or ts_height is None
            or z_clearance is None
            or xy_clearance is None
            or latch is None
            or reverse_latch is None
            or ts_diam is None
            or ts_offset is None
            or revrott is None
            or tp_height is None
            or tp_lenght is None
           ):
            self.chk_use_tool_measurement.set_active(False)
            self.frm_tool_measurement.set_sensitive(False)

            message   = _("Invalidate TOOL_SETTER and REMAP M6")
            secondary = _("Please check the TOOL_SETTER INI configurations")
            self.warning_dialog(message, secondary=secondary)
            return 0
        else:
            self.xpos = float(xpos)
            self.ypos = float(ypos)
            self.zpos = float(zpos)
            self.z_maxprobe = float(z_maxprobe)
            self.xy_maxprobe = float(xy_maxprobe)
            self.shearch_vel = float(shearch_vel)
            self.probe_vel = float(probe_vel)
            self.ts_height = float(ts_height)
            self.z_clearance = float(z_clearance)
            self.xy_clearance = float(xy_clearance)
            self.latch = float(latch)
            self.reverse_latch = float(reverse_latch)
            self.ts_diam = float(ts_diam)
            self.ts_offset = float(ts_offset)
            self.revrott = float(revrott)
            self.tp_height = float(tp_height)
            self.tp_lenght = float(tp_lenght)

            self.halcomp["tp_height"] = float(tp_height)
            self.halcomp["tp_lenght"] = float(tp_lenght)

            #self.spbtn_setter_height.set_value(self.prefs.getpref("ts_height", 0.0, float))
            # at startup read the ini but you can alter the value when machine is running or found the height with probing table + probing setter
            self.spbtn_setter_height.set_value(self.ts_height)
            self.halcomp["ts_height"] = self.spbtn_setter_height.get_value()

            self.spbtn_block_height.set_value(self.prefs.getpref("blockheight", 0.0, float))
            self.halcomp["blockheight"] = self.spbtn_block_height.get_value()


            # to set the hal pin with correct values we emit a toggled
            if self.chk_use_tool_measurement.get_active():
                self.frm_tool_measurement.set_sensitive(False)
                self.halcomp["use_tool_measurement"] = True
            else:
                self.frm_tool_measurement.set_sensitive(True)
                self.chk_use_tool_measurement.set_sensitive(True)

            # to set the hal pin with correct values we emit a toggled
            if self.chk_use_touch_plate.get_active():
                self.halcomp["use_touch_plate"] = True
                self.hal_led_use_touch_plate.hal_pin.set(1)
            else:
                self.halcomp["use_touch_plate"] = False
                self.hal_led_use_touch_plate.hal_pin.set(0)


    def ts_clearance_down(self, data=None):
        # move Z - z_clearance
        s = """G91
        G1 Z-%f
        G90""" % (self.z_clearance)
        if self.gcode(s) == -1:
            return -1
        return 0

    def ts_clearance_up(self, data=None):
        # move Z + z_clearance
        s = """G91
        G1 Z%f
        G90""" % (self.z_clearance)
        if self.gcode(s) == -1:
            return -1
        return 0



    # ----------------
    # Remap M6 Buttons
    # ----------------
    # Tickbox from gui for enable disable remap (with saving pref)
    # Logic is now inverted for set.sensitive this is more logic : when remap is enabled you can't change settings so setting need to be done before activate remap.
    def on_chk_use_tool_measurement_toggled(self, gtkcheckbutton, data=None):
        if gtkcheckbutton.get_active():
            self.frm_tool_measurement.set_sensitive(False)
            self.halcomp["use_tool_measurement"] = True
        else:
            self.frm_tool_measurement.set_sensitive(True)
            self.halcomp["use_tool_measurement"] = False
        self.prefs.putpref("use_tool_measurement", gtkcheckbutton.get_active(), bool)
        self.hal_led_set_m6.hal_pin.set(gtkcheckbutton.get_active())

    # Set rotating spindle check (without saving pref)
    def on_chk_use_rotate_spindle_toggled(self, gtkcheckbutton, data=None):
        if gtkcheckbutton.get_active():
            self.halcomp["use_rotate_spindle"] = True
        else:
            self.halcomp["use_rotate_spindle"] = False
        # saving pref is not wanted here
        self.hal_led_rotate_spindle.hal_pin.set(gtkcheckbutton.get_active())

    # Set basic touchplate in place of 3D-PROBE
    def on_chk_use_touch_plate_toggled(self, gtkcheckbutton, data=None):
        if gtkcheckbutton.get_active():
            self.halcomp["use_touch_plate"] = True
        else:
            self.halcomp["use_touch_plate"] = False
        self.prefs.putpref("use_touch_plate", gtkcheckbutton.get_active(), bool)
        self.hal_led_use_touch_plate.hal_pin.set(gtkcheckbutton.get_active())



    # Spinbox for setter height with override value from GUI but at each startup use INI value
    def on_spbtn_setter_height_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("ts_height", gtkspinbutton, data)

    def on_spbtn_setter_height_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("ts_height", gtkspinbutton, data)
        self.add_history_text("TS Height = %.4f" % (gtkspinbutton.get_value()))

    # Spinbox for block height with autosave value inside machine pref file
    def on_spbtn_block_height_key_press_event(self, gtkspinbutton, data=None):
        self.on_common_spbtn_key_press_event("blockheight", gtkspinbutton, data)

    def on_spbtn_block_height_value_changed(self, gtkspinbutton, data=None):
        self.on_common_spbtn_value_changed("blockheight", gtkspinbutton, data)
        # set coordinate system to new origin                                      # think about using or not using if self.halcomp["set_zero"]: for make it optional
        if self.gcode("G10 L2 P0 Z%s" % (gtkspinbutton.get_value())) == -1:
            return
        # set coordinate system to new origin
        #if self.gcode("G10 L2 P0 Z%s" % (gtkspinbutton.get_value()))
        #self.vcp_reload()
        self.add_history_text("Workpiece Height = %.4f" % (gtkspinbutton.get_value()))

    # Down probe to table for measuring it and use for calculate tool setter height and can set G10 L20 Z0 if you tick auto zero
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_probe_table_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [3]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return
        if self.ocode("o<psng_probe_table> call") == -1:
            return
        a = self.stat.probed_position
        ptres = float(a[2])
        if self.halcomp["use_touch_plate"] == True:
            ptresplate = float(a[2]) - self.halcomp["tp_height"]
            print("probedtable with TOUCH-PLATE =", ptresplate)
        self.halcomp["probedtable"] = ptres
        print("probedtable with 3D-PROBE =", ptres)
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "Z",
            z=ptres,
        )
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
        if self.ocode("o<psng_config_check> call") == -1:
            return
        if self.ocode("o<psng_probe_setter> call") == -1:
            return
        a = self.stat.probed_position
        tsres = (float(a[2]) - self.halcomp["probedtable"])
        print("ts_height =", tsres)
        print("probedtable =", self.halcomp["probedtable"])
        self.spbtn_setter_height.set_value(tsres)
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "Z",
            z=tsres,
        )
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # Down probe to workpiece for measuring it vs Know tool setter height
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_probe_workpiece_released(self, gtkbutton, data=None):
        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [5]") == -1:
            return
        if self.ocode("o<psng_config_check> call") == -1:
            return
        if self.ocode("o<psng_probe_workpiece> call") == -1:
            return
        a = self.probed_position_with_offsets()
        pwres = float(a[2])
        if self.halcomp["use_touch_plate"] == True:
            pwresplate = float(a[2]) - self.halcomp["tp_height"]
            print("workpiecesheight with TOUCH-PLATE =", pwresplate)
        print("workpiecesheight with 3D-PROBE =", pwres)
        print("ts_height", self.halcomp["ts_height"])
        self.spbtn_block_height.set_value(pwres)                                           # this call update automatically the offset for workpiece
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "Z",
            z=pwres,
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
        # o<psng_config_check> call IS NOT WANTED HERE DUE TO USE INI SETTING
        if self.ocode("o<psng_tool_length> call") == -1:
            return
        a = self.stat.probed_position
        tlres = (float(a[2]) - self.halcomp["ts_height"])
        print("tool length =", tlres)
        self.add_history(
            gtkbutton.get_tooltip_text(),
            "Z",
            z=tlres,
        )
        if self.ocode("o<backup_restore> call [999]") == -1:
            return

    # TOOL TABLE CREATOR
    # TOOL DIA : use X only for find tool setter center and use only after that more accurate Y center value for determinig tool diameter
    # + TOOL length Z and the whole sequence is saved as tooltable for later use
    # IMH this sequence need to be first with probe : first execute psng_down for determinate the table height with toolsetter and think about updating tool setter diameter or probe diameter at same time
    # IMH this sequence need to be done secondly with other tool using button Dia only off course
    # ALL OF THIS NEED TO EDIT TOOL TABLE MANUALLY FOR ADD NEW TOOL AND KNOW DIAMETER
    @ProbeScreenBase.ensure_errors_dismissed
    def on_btn_tool_dia_released(self, gtkbutton, data=None):
        tooltable = self.inifile.find("EMCIO", "TOOL_TABLE")
        if not tooltable:
            message   = _("Tool Measurement Error")
            secondary = _("Did not find a toolfile file in [EMCIO] TOOL_TABLE")
            self.error_dialog(message, secondary=secondary)
            return
        #toolnumber = self.halcomp["toolchange-number"]
        toolnumber = Popen("halcmd getp iocontrol.0.tool-number", shell=True, stdout=PIPE).stdout.read()
        tooldiameter = Popen("halcmd getp halui.tool.diameter", shell=True, stdout=PIPE).stdout.read()
        print("tool-number =", toolnumber)
        print("tooldiameter from halui =", tooldiameter)

        if self.ocode("o<backup_status> call") == -1:
            return
        if self.ocode("o<psng_hook> call [2]") == -1:
            return
        # o<psng_config_check> call IS NOT WANTED HERE DUE TO USE INI SETTING
        if self.ocode("o<psng_tool_diameter> call") == -1:
            return

        # show Z result
        a = self.probed_position_with_offsets()
        zres = ((float(a[2])) - self.halcomp["ts_height"])

        # move X +
        tmpx = (0.5 * (self.ts_diam + tooldiameter) + self.xy_clearance)
        s = """G91
        G1 X-%f
        G90""" % (tmpx)
        if self.gcode(s) == -1:
            return

        if self.ocode("o<psng_tool_diameter_check> call") == -1:
            message   = _("TOOL DIAMETER MEASUREMENT STOPPED")
            self.error_dialog(message)
            return

        if self.ts_clearance_down() == -1:
            return
        # Start psng_xplus.ngc var already loaded from ini by Start psng_tool_diameter.ngc
        if self.ocode("o<psng_start_xplus_probing> call") == -1:
            return
        # show X result
        a = self.probed_position_with_offsets()
        xpres = float(a[0]) + 0.5 * self.ts_diam
        #    print("xpres = ",xpres)
        # move Z to start point up
        if self.ts_clearance_up() == -1:
            return

        # move X -
        tmpx = (self.ts_diam + tooldiameter) + (2*self.xy_clearance)
        s = """G91
        G1 X%f
        G90""" % (tmpx)
        if self.gcode(s) == -1:
            return
        if self.ts_clearance_down() == -1:
            return
        # Start psng_xminus.ngc var already loaded from ini by Start psng_tool_diameter.ngc
        if self.ocode("o<psng_start_xminus_probing> call") == -1:
            return
        # show X result
        a = self.probed_position_with_offsets()
        xmres = float(a[0]) - 0.5 * self.ts_diam
        #    print("xmres = ",xmres)
        self.length_x()
        xcres = 0.5 * (xpres + xmres)


        # move Z to start point up
        if self.ts_clearance_up() == -1:
            return
        # go to the new center of X
        s = "G1 X%f" % (xcres)
        print("xcenter = ",xcres)
        if self.gcode(s) == -1:
            return


        # move Y +
        tmpy = (0.5 * (self.ts_diam + tooldiameter) + self.xy_clearance)
        s = """G91
        G1 Y-%f
        G90""" % (tmpy)
        if self.gcode(s) == -1:
            return
        if self.ts_clearance_down() == -1:
            return
        # Start psng_yplus.ngc var already loaded from ini by Start psng_tool_diameter.ngc
        if self.ocode("o<psng_start_yplus_probing> call") == -1:
            return
        # show Y result
        a = self.probed_position_with_offsets()
        ypres = float(a[1]) + 0.5 * self.ts_diam
        print("simple probed pos Y+ = ",self.stat.probed_position)
        print("ypres = ",ypres)
        # move Z to start point up
        if self.ts_clearance_up() == -1:
            return

        # move Y -
        tmpy = (self.ts_diam + tooldiameter) + (2*self.xy_clearance)
        s = """G91
        G1 Y%f
        G90""" % (tmpy)
        if self.gcode(s) == -1:
            return
        if self.ts_clearance_down() == -1:
            return
        # Start psng_yminus.ngc var already loaded from ini by Start psng_tool_diameter.ngc
        if self.ocode("o<psng_start_yminus_probing> call") == -1:
            return
        # show Y result
        a = self.probed_position_with_offsets()
        ymres = float(a[1]) - 0.5 * self.ts_diam
        print("simple probed pos Y- = ", self.stat.probed_position)
        print("ymres = ",ymres)
        self.length_y()
        ycres = 0.5 * (ypres + ymres)
        print("ycres = ",ycres)

        diam = ymres - ypres
        diamwithofsset = diam + (2*self.ts_offset)
        self.add_history_text("old tooldiameter from tooltable = %.4f" % (tooldiameter))
        self.add_history_text("new tooldiameter measured = %.4f" % (diam))
        self.add_history_text("new tooldiameter compensated set in tootlable = %.4f" % (diamwithofsset))

        self.add_history(
            gtkbutton.get_tooltip_text(),
            "XcYcZD",
            xc=xcres,
            yc=ycres,
            z=zres,
            d=diamwithofsset,
        )
        s = "G10 L1 P%f R%f" % (Popen("halcmd getp iocontrol.0.tool-number", shell=True, stdout=PIPE).stdout.read(),(0.5*diamwithofsset))           # 0.14 seem to be needed for my setter adding the necessary distance for radial triggering probe (0.07mm each direction)
        if self.gcode(s) == -1:
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
#                    self.error_dialog(message, secondary=secondary, title=_("PSNG Manual Toolchange"))
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
