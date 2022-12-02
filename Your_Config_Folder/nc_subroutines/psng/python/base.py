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

import math
import os
import sys
import time
from datetime import datetime
from functools import wraps
from subprocess import PIPE, Popen
import hal
import linuxcnc

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Pango

from .configparser import ProbeScreenConfigParser
from .util import restore_task_mode

from gladevcp.combi_dro import Combi_DRO  # we will need it to make the DRO

CONFIGPATH1 = os.environ["CONFIG_DIR"]


class ProbeScreenBase(object):
    # --------------------------
    #
    #  INIT
    #
    # --------------------------
    def __init__(self, halcomp, builder, useropts):
        self.builder = builder
        self.halcomp = halcomp

        # Load the machines INI file
        self.inifile = linuxcnc.ini(os.environ["INI_FILE_NAME"])
        if not self.inifile:
            self.warning_dialog("no INI File given")
            sys.exit(1)

        # Load Probe Screen Preferences
        self.prefs = ProbeScreenConfigParser(self.get_preference_file_path())

        # Which display is in use? AXIS / gmoccapy / unknown
        self.display = self.get_display() or "unknown"

        # LinuxCNC Command / Stat / Error Interfaces
        self.command = linuxcnc.command()
        self.stat = linuxcnc.stat()
        self.stat.poll()   # before using some self value from linuxcnc we need to poll

        # History Area
        textarea = builder.get_object("textview1")
        self.buffer = textarea.get_property("buffer")

        # Warning Dialog
        self.window = builder.get_object("window1")

        # VCP Reload Action
        self._vcp_action_reload = self.builder.get_object("vcp_action_reload")

        # Results Display
        self._result_box_xp = self.builder.get_object("result_box_xp")
        self._result_box_yp = self.builder.get_object("result_box_yp")
        self._result_box_xm = self.builder.get_object("result_box_xm")
        self._result_box_ym = self.builder.get_object("result_box_ym")
        self._result_box_lx = self.builder.get_object("result_box_lx")
        self._result_box_ly = self.builder.get_object("result_box_ly")
        self._result_box_z  = self.builder.get_object("result_box_z")
        self._result_box_d  = self.builder.get_object("result_box_d")
        self._result_box_xc = self.builder.get_object("result_box_xc")
        self._result_box_yc = self.builder.get_object("result_box_yc")
        self._result_box_a  = self.builder.get_object("result_box_a")

        self.frm_parents = self.builder.get_object("frm_parents")

        self._work_in_progress = 0

        #DO NOT CREATE HAL PIN HERE DUE TO MULTIPLE CALL

    # --------------------------
    #
    #  MDI Command Methods
    #
    # --------------------------
    @restore_task_mode
    def gcode(self, s):
        self.command.mode(linuxcnc.MODE_MDI)
        self.command.wait_complete()

        for l in s.split("\n"):
            # Search for G1 followed by a space, otherwise we'll catch G10 too.
            if "G1 " in l:
                l += " F%f" % (self.halcomp["psng_vel_for_travel"])
            self.command.mdi(l)
            rv = self.command.wait_complete(50)
            if rv == -1:
                message = _("command timed out")
                secondary = _("please check self.command.wait_complete timeout in psng base.py")
                self.warning_dialog(message, secondary=secondary)
                return -1
            if self.error_poll() == -1:
                return -1
        return 0

    @restore_task_mode
    def ocode(self, s):
        self.command.mode(linuxcnc.MODE_MDI)
        self.command.wait_complete()

        self.command.mdi(s)
        self.stat.poll()   # before using some self value from linuxcnc we need to poll
        while self.stat.interp_state != linuxcnc.INTERP_IDLE:
            if self.error_poll() == -1:
            #    print ("interp_err_status = %s" % (self.stat.interp_state))
            #    print ("interp_err_queue = %s" % (self.stat.queue))
            #    print ("interp_err_operator = %s" % (linuxcnc.OPERATOR_ERROR))
            #    print ("interp_err_nml = %s" % (linuxcnc.NML_ERROR))
                return -1
            self.command.wait_complete()
            self.stat.poll()   # before using some self value from linuxcnc we need to poll
        self.command.wait_complete()
        if self.error_poll() == -1:
        #    print ("interp_err2_status = %s" % (self.stat.interp_state))
        #    print ("interp_err2_queue = %s" % (self.stat.queue))
        #    print ("interp_err2_operator = %s" % (linuxcnc.OPERATOR_ERROR))
        #    print ("interp_err2_nml = %s" % (linuxcnc.NML_ERROR))
            return -1
        return 0

    def error_poll(self):
        stop_halui = hal.get_value("halui.abort")
        abort_halui = hal.get_value("halui.program.stop")
#        abort_halui = Popen(
#            "halcmd getp halui.abort ", shell=True, stdout=PIPE
#        ).stdout.read()
#        stop_halui = Popen(
#            "halcmd getp halui.program.stop ", shell=True, stdout=PIPE
#        ).stdout.read()

        if "axis" in self.display:
            # AXIS polls for errors every 0.2 seconds, so we wait slightly longer to make sure it's happened.
            time.sleep(0.35)
            error_pin = hal.get_value("axisui.error")
            abort_axisui = hal.get_value("axisui.abort")
#            error_pin = Popen(
#                "halcmd getp axisui.error ", shell=True, stdout=PIPE
#            ).stdout.read()
#            abort_axisui = Popen(
#                "halcmd getp axisui.abort ", shell=True, stdout=PIPE
#            ).stdout.read()
        elif "gmoccapy" in self.display:
            # gmoccapy polls for errors every 0.25 seconds, OR whatever value is in the [DISPLAY]CYCLE_TIME ini
            # setting, so we wait slightly longer to make sure it's happened.
            ms = int(self.inifile.find("DISPLAY", "CYCLE_TIME") or 250) + 50
            time.sleep(ms / 1000)
            error_pin = hal.get_value("gmoccapy.error")
#            error_pin = Popen(
#                "halcmd getp gmoccapy.error ", shell=True, stdout=PIPE
#            ).stdout.read()

            # Something need to be done for add to gmoccapy a hal pin gmoccapy.abort
        else:
            self.error_dialog("UNABLE TO POLL %s GUI FOR ERRORS") % (self.display)
            return -1

#        if "TRUE" in str(error_pin):
        if error_pin:
            self.add_history_text("ABORT: See notification popup")
            self.command.mode(linuxcnc.MODE_MANUAL)
            self.command.wait_complete()
            return -1
#        elif "TRUE" in str(abort_axisui) or "TRUE" in str(abort_halui) or "TRUE" in str(stop_halui):
        elif abort_axisui or abort_halui or stop_halui:
            self.warning_dialog("OPERATION STOPPED BY USER")
            self.command.mode(linuxcnc.MODE_MANUAL)
            self.command.wait_complete()
            return -1

        return 0


    # --------------------------
    #
    #  Utility Methods
    #
    # --------------------------
    def get_display(self):
        # gmoccapy or axis ?
        temp = self.inifile.find("DISPLAY", "DISPLAY")
        if not temp:
            print(
                "****  PROBE SCREEN GET INI INFO **** \n Error recognition of display type : %s"
                % (temp)
            )
        return temp

    def get_preference_file_path(self):
        # we get the preference file, if there is none given in the INI
        # we use probe_screen.pref in the config dir
        temp = self.inifile.find("DISPLAY", "PREFERENCE_FILE_PATH")
        if not temp:
            machinename = self.inifile.find("EMC", "MACHINE")
            if not machinename:
                temp = os.path.join(CONFIGPATH1, "probe_screen.pref")
            else:
                machinename = machinename.replace(" ", "_")
                temp = os.path.join(CONFIGPATH1, "%s.pref" % (machinename))
        print ("****  probe_screen GETINIINFO **** \n Preference file path: %s" % (temp))
        return temp

    def vcp_reload(self):
        """ Realods the VCP - e.g. after changing origin/zero points """
        self._vcp_action_reload.emit("activate")


    # --------------------------
    #
    #  History and Logging Methods
    #
    # --------------------------
    def add_history(
        self,
        tool_tip_text,
        s="",
        xm=None,
        xc=None,
        xp=None,
        lx=None,
        ym=None,
        yc=None,
        yp=None,
        ly=None,
        z=None,
        d=None,
        a=None,
    ):
        c = "{0: <10} ".format(tool_tip_text)
        if "Xm" in s:
            c += "X-=%.4f " % (xm)
            self._result_box_xm.set_text("%.4f" % (xm))
        if "Xc" in s:
            c += "Xc=%.4f " % (xc)
            self._result_box_xc.set_text("%.4f" % (xc))
        if "Xp" in s:
            c += "X+=%.4f " % (xp)
            self._result_box_xp.set_text("%.4f" % (xp))
        if "Lx" in s:
            c += "Lx=%.4f " % (lx)
            self._result_box_lx.set_text("%.4f" % (lx))
        if "Ym" in s:
            c += "Y-=%.4f " % (ym)
            self._result_box_ym.set_text("%.4f" % (ym))
        if "Yc" in s:
            c += "Yc=%.4f " % (yc)
            self._result_box_yc.set_text("%.4f" % (yc))
        if "Yp" in s:
            c += "Y+=%.4f " % (yp)
            self._result_box_yp.set_text("%.4f" % (yp))
        if "Ly" in s:
            c += "Ly=%.4f " % (ly)
            self._result_box_ly.set_text("%.4f" % (ly))
        if "Z" in s:
            c += "Z=%.4f " % (z)
            self._result_box_z.set_text("%.4f" % (z))
        if "D" in s:
            c += "D=%.4f" % (d)
            self._result_box_d.set_text("%.4f" % (d))
        if "A" in s:
            c += "Angle=%.3f" % (a)
            self._result_box_a.set_text("%.3f" % (a))

        #self.add_history_text(c)


    def add_history_text(self, text):
        # Prepend a timestamp to all History lines
        text = datetime.now().strftime("%H:%M:%S  ") + text

        # Remove the oldest history entries when we have a large number of entries
        i = self.buffer.get_end_iter()
        if i.get_line() > 1000:
            i.backward_line()
            self.buffer.delete(i, self.buffer.get_end_iter())

        # Add the line of text to the top of the history
        i.set_line(0)
        self.buffer.insert(i, "%s \n" % (text))


    def warning_dialog(self, message, secondary=None, title=_("Warning PSNG")):
        """ displays a warning dialog """
        if self.halcomp["chk_use_popup_style_psng"] or hal.get_value("motion.motion-enabled") == 0:
            dialog = Gtk.MessageDialog(
                self.window,
                Gtk.DialogFlags.MODAL,
                Gtk.MessageType.WARNING,
                Gtk.ButtonsType.OK,
                message,
            )
            # if there is a secondary message then the first message text is bold
            if secondary:
                dialog.format_secondary_text(secondary)

            dialog.set_title(title)
            dialog.set_keep_above(True)
            dialog.show_all()

            response = dialog.run()
            if response == Gtk.ButtonsType.OK:
                dialog.destroy()
                return response
            else:
                dialog.destroy()
                return -1
        else:
            if secondary:
                self.gcode("(DEBUG,**** WARN : %s ****)" % (message))
                self.gcode("(DEBUG,**** WARN : %s ****)" % (secondary))
            else:
                self.gcode("(DEBUG,**** WARN : %s ****)" % (message))


    def error_dialog(self, message, secondary=None, title=_("Error PSNG")):
        """ displays a error dialog + backup_restore and abort """
        if self.halcomp["chk_use_popup_style_psng"] or hal.get_value("motion.motion-enabled") == 0:
            if self.ocode("o<backup_status_restore> call") == -1:
                dialog = Gtk.MessageDialog(
                    self.window,
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.CLOSE,
                    message,
                )
                # if there is a secondary message then the first message text is bold
                if secondary:
                    dialog.format_secondary_text(secondary)

                dialog.set_title(title)
                dialog.set_keep_above(True)
                dialog.show_all()

                response = dialog.run()
                if response == Gtk.MessageType.CLOSE:
                    dialog.destroy()
                    return response
                else:
                    dialog.destroy()
                    return -1
        else:
            if secondary:
                self.gcode("(DEBUG,**** ERROR : %s ****)" % (message))
                self.gcode("(ABORT,**** ERROR : %s ****)" % (secondary))
            else:
                self.gcode("(ABORT,**** ERROR : %s ****)" % (message))


    def _dialog_confirm(self, message):
        """ displays a confirm dialog """
        if self.halcomp["chk_use_popup_style_psng"]:
            dialog = Gtk.MessageDialog(
                                  self.window,
                                  Gtk.DialogFlags.MODAL,
                                  Gtk.MessageType.QUESTION,
                                  Gtk.ButtonsType.OK_CANCEL,
                              )

            label = Gtk.Label(message)
            dialog.vbox.pack_start(label, False, False, 0)

            label = Gtk.Label("are you sure ?")
            dialog.vbox.pack_start(label, False, False, 0)

            dialog.set_title(_("PSNG"))
            dialog.set_keep_above(True)
            dialog.show_all()

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                dialog.destroy()
                return response
            else:
                dialog.destroy()
                return -1
        # If not popup_style use pause



    def _dialog_spbtn_z_eoffset_compensation(self):
        """
        Display a dialog with a text entry.
        Returns the text, or None if canceled.
        """
        xcount  = 2
        ycount  = 2
        xlength = 50
        ylength = 50

        dialog = Gtk.MessageDialog(
                              self.window,
                              Gtk.DialogFlags.MODAL,
                              Gtk.MessageType.QUESTION,
                              Gtk.ButtonsType.OK_CANCEL,
                              )

        label = Gtk.Label("FIRST YOU NEED TO MOVE MACHINE XY")
        dialog.vbox.pack_start(label, False, False, 0)

        label = Gtk.Label("AT THE DESIRED START XY POSITION")
        dialog.vbox.pack_start(label, False, False, 0)

        label = Gtk.Label("Z START WHERE HE IS : MOVE IT NEAR")
        dialog.vbox.pack_start(label, False, False, 0)

        label = Gtk.Label("X count point number")
        dialog.vbox.pack_start(label, False, False, 5)
        adjustment = Gtk.Adjustment(
          value=xcount,
          lower=2,
          upper=999,
          step_incr=1,
          page_incr=2,
        )
        spin_button_xcount = Gtk.SpinButton(digits=0)
        spin_button_xcount.set_numeric(True)
        spin_button_xcount.set_adjustment(adjustment)
        spin_button_xcount.set_value(xcount)
        dialog.vbox.pack_start(spin_button_xcount, False, False, 0)

        label = Gtk.Label("Y count point number")
        dialog.vbox.pack_start(label, False, False, 0)
        adjustment = Gtk.Adjustment(
          value=ycount,
          lower=2,
          upper=999,
          step_incr=1,
          page_incr=2,
        )
        spin_button_ycount = Gtk.SpinButton(digits=0)
        spin_button_ycount.set_numeric(True)
        spin_button_ycount.set_adjustment(adjustment)
        spin_button_ycount.set_value(ycount)
        dialog.vbox.pack_start(spin_button_ycount, False, False, 0)

        label = Gtk.Label("X length of the gridd")
        dialog.vbox.pack_start(label, False, False, 0)
        adjustment = Gtk.Adjustment(
          value=xlength,
          lower=2,
          upper=999,
          step_incr=1,
          page_incr=2,
        )
        spin_button_xlength = Gtk.SpinButton(digits=0)
        spin_button_xlength.set_numeric(True)
        spin_button_xlength.set_adjustment(adjustment)
        spin_button_xlength.set_value(xlength)
        dialog.vbox.pack_start(spin_button_xlength, False, False, 0)

        label = Gtk.Label("Y length of the gridd")
        dialog.vbox.pack_start(label, False, False, 0)
        adjustment = Gtk.Adjustment(
          value=ylength,
          lower=2,
          upper=999,
          step_incr=1,
          page_incr=2,
        )
        spin_button_ylength = Gtk.SpinButton(digits=0)
        spin_button_ylength.set_numeric(True)
        spin_button_ylength.set_adjustment(adjustment)
        spin_button_ylength.set_value(ylength)
        dialog.vbox.pack_start(spin_button_ylength, False, False, 0)

        dialog.set_title(_("Z_EOFFSET_COMPENSATION"))
        dialog.set_keep_above(True)
        dialog.show_all()

        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            self.halcomp["compensat_xcount"]  = spin_button_xcount.get_value()
            self.halcomp["compensat_ycount"]  = spin_button_ycount.get_value()
            self.halcomp["compensat_xlength"] = spin_button_xlength.get_value()
            self.halcomp["compensat_ylength"] = spin_button_ylength.get_value()
            return response
        else:
            self.halcomp["compensat_xcount"]  = 0
            self.halcomp["compensat_ycount"]  = 0
            self.halcomp["compensat_xlength"] = 0
            self.halcomp["compensat_ylength"] = 0
            return -1

####################################################

    def _dialog_spbtn_ask_toolnumber(self):
        """
        Display a dialog with a text entry.
        Returns the text, or None if canceled.
        """
        ts_popup_tool_number  = hal.get_value("iocontrol.0.tool-number") #self.halcomp["toolchange_number"]
        ts_popup_tool_diameter  = hal.get_value("halui.tool.diameter") #self.halcomp["toolchange_diameter"]

        dialog = Gtk.MessageDialog(
                              self.window,
                              Gtk.DialogFlags.MODAL,
                              Gtk.MessageType.QUESTION,
                              Gtk.ButtonsType.OK_CANCEL,
                              )

        label = Gtk.Label("Tool number mounted to probe :")
        dialog.vbox.pack_start(label, False, False, 0)

        adjustment = Gtk.Adjustment(
          value=ts_popup_tool_number,
          lower=1,
          upper=999,
          step_incr=1,
          page_incr=2,
        )
        spin_button_ts_popup_tool_number = Gtk.SpinButton(digits=0)
        spin_button_ts_popup_tool_number.set_numeric(True)
        spin_button_ts_popup_tool_number.set_adjustment(adjustment)
        spin_button_ts_popup_tool_number.set_value(ts_popup_tool_number)
        dialog.vbox.pack_start(spin_button_ts_popup_tool_number, False, False, 0)

        label = Gtk.Label("Exact tool diameter :")
        dialog.vbox.pack_start(label, False, False, 0)

        adjustment = Gtk.Adjustment(
          value=ts_popup_tool_diameter,
          lower=self.halcomp["ts_min_tool_dia"],
          upper=self.halcomp["ts_max_tool_dia"],
          step_incr=0.1,
          page_incr=1,
        )
        spin_button_ts_popup_tool_diameter = Gtk.SpinButton(digits=5)
        spin_button_ts_popup_tool_diameter.set_numeric(True)
        spin_button_ts_popup_tool_diameter.set_adjustment(adjustment)
        spin_button_ts_popup_tool_diameter.set_value(ts_popup_tool_diameter)
        dialog.vbox.pack_start(spin_button_ts_popup_tool_diameter, False, False, 0)

        dialog.set_title(_("TOOL LENGTH PROBE"))
        dialog.set_keep_above(True)
        dialog.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.halcomp["ts_popup_tool_number"] = spin_button_ts_popup_tool_number.get_value()
            self.halcomp["ts_popup_tool_diameter"] = spin_button_ts_popup_tool_diameter.get_value()
            dialog.destroy()
            return response
        else:
            self.halcomp["ts_popup_tool_number"]   = 0
            self.halcomp["ts_popup_tool_diameter"]   = 0
            dialog.destroy()
            return -1

##############################################

    def _dialog_spbtn_ask_toolnumber_diameter(self):
            """
            Display a dialog with a text entry.
            Returns the text, or None if canceled.
            """
            ts_popup_tool_number  = int(math.ceil(hal.get_value("iocontrol.0.tool-number")))  #rounf up tool diameter
            ts_popup_tool_diameter  = hal.get_value("halui.tool.diameter") #self.halcomp["toolchange_diameter"]
            self.tool_is_spherical = 0

            dialog = Gtk.MessageDialog(
                                  self.window,
                                  Gtk.DialogFlags.MODAL,
                                  Gtk.MessageType.QUESTION,
                                  Gtk.ButtonsType.OK_CANCEL,
                                  )

            label = Gtk.Label("Tool number mounted to probe :")
            dialog.vbox.pack_start(label, False, False, 5)

            adjustment = Gtk.Adjustment(
              value=ts_popup_tool_number,
              lower=1,
              upper=999,
              step_incr=1,
              page_incr=2,
            )
            spin_button_ts_popup_tool_number = Gtk.SpinButton(digits=0)
            spin_button_ts_popup_tool_number.set_numeric(True)
            spin_button_ts_popup_tool_number.set_adjustment(adjustment)
            spin_button_ts_popup_tool_number.set_value(ts_popup_tool_number)
            dialog.vbox.pack_start(spin_button_ts_popup_tool_number, False, False, 0)

            label = Gtk.Label("Tool diameter round up :")
            dialog.vbox.pack_start(label, False, False, 0)

            adjustment = Gtk.Adjustment(
              value=ts_popup_tool_diameter,
              lower=self.halcomp["ts_min_tool_dia"],
              upper=self.halcomp["ts_max_tool_dia"],
              step_incr=1,
              page_incr=1,
            )
            spin_button_ts_popup_tool_diameter = Gtk.SpinButton(digits=0)
            spin_button_ts_popup_tool_diameter.set_numeric(True)
            spin_button_ts_popup_tool_diameter.set_adjustment(adjustment)
            spin_button_ts_popup_tool_diameter.set_value(ts_popup_tool_diameter)
            dialog.vbox.pack_start(spin_button_ts_popup_tool_diameter, False, False, 0)

            label = Gtk.Label("set ON for spherical tool :")
            dialog.vbox.pack_start(label, False, False, 0)

            switch_button_ts_popup_tool_is_spherical = Gtk.Switch()
            switch_button_ts_popup_tool_is_spherical.connect("notify::active", self.on_switch_activated)
            switch_button_ts_popup_tool_is_spherical.set_active(False)
            dialog.vbox.pack_start(switch_button_ts_popup_tool_is_spherical, True, True, 0)

            dialog.set_title(_("TOOL DIAMETER MEASUREMENT"))
            dialog.set_keep_above(True)
            dialog.show_all()

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.halcomp["ts_popup_tool_number"] = spin_button_ts_popup_tool_number.get_value()
                self.halcomp["ts_popup_tool_diameter"] = spin_button_ts_popup_tool_diameter.get_value()
                self.halcomp["ts_popup_tool_is_spherical"] = self.tool_is_spherical
                dialog.destroy()
                return response
            else:
                self.halcomp["ts_popup_tool_number"] = 0
                self.halcomp["ts_popup_tool_diameter"] = 0
                self.halcomp["ts_popup_tool_is_spherical"] = 0
                dialog.destroy()
                return -1

    def on_switch_activated(self, switch, gparam):
            if switch.get_active():
                state = "on"
                self.tool_is_spherical = 1
            else:
                state = "off"
                self.tool_is_spherical = 0


    # --------------------------
    #
    #  Generic Method Wrappers
    #
    # --------------------------
    @classmethod
    def ensure_errors_dismissed(cls, f):
        """ Ensures all errors have been dismissed, otherwise, shows a warning dialog """

        @wraps(f)
        def wrapper(self, *args, **kwargs):

#            if Popen('halcmd getp motion.motion-enabled',stdout=PIPE,shell=True).communicate()[0].strip() == 'FALSE':
            if hal.get_value("motion.motion-enabled") == 0:
                self.warning_dialog("Please turn machine on", "You can retry once done")
                return -1


            if self.error_poll() == -1:
                self.warning_dialog("Please dismiss & act upon all errors", "You can retry once done")
                return -1

#            if self._work_in_progress == 1:
#                self.warning_dialog("Please try again after actual job is finished", "You can retry once done")
#                #return -1
#            else:
#               self._work_in_progress = 1

            # Execute wrapped function
            return f(self, *args, **kwargs)

        return wrapper



    @classmethod
    def ensure_is_not_touchplate(cls, f):
        """ Ensures is not touchplate selected, otherwise, shows a warning dialog """

        @wraps(f)
        def wrapper(self, *args, **kwargs):

            if self.halcomp["chk_use_touch_plate"]:
                self.warning_dialog("You can't use this function using touchplate")
                return -1

            # Execute wrapped function
            return f(self, *args, **kwargs)

        return wrapper


    # --------------------------
    #
    #  Load the corresponding calculated value to hal
    #
    # --------------------------
    def _preload_var_hal_ts(self):
        return

    def _preload_var_hal_probing(self):
        return


    # --------------------------
    #
    #  Generic Probe Movement Methods
    #
    # --------------------------
    def move_probe_z_down(self):
        if self.ocode("o<psng_move_z_down> call") == -1:
            return -1
        return 0


    def move_probe_z_up(self):
        if self.ocode("o<psng_move_z_up> call") == -1:
            return -1
        return 0


    def probed_position_with_offsets(self):
        self.stat.poll()   # before using some self value from linuxcnc we need to poll
        probed_position = list(self.stat.probed_position)
        coord = list(self.stat.probed_position)
        g5x_offset = list(self.stat.g5x_offset)
        g92_offset = list(self.stat.g92_offset)
        tool_offset = list(self.stat.tool_offset)
        #print ("g5x_offset  = ",g5x_offset)
        #print ("g92_offset  = ",g92_offset)
        #print ("tool_offset  = ",tool_offset)
        #print ("actual position  = ",self.stat.actual_position)
        #print ("position  = ",self.stat.position)
        #print ("joint_actual position  = ",self.stat.joint_actual_position)
        #print ("joint_position  = ",self.stat.joint_position)
        #print ("probed position  = ",self.stat.probed_position)
        for i in range(0, len(probed_position) - 1):
            coord[i] = (probed_position[i] - g5x_offset[i] - g92_offset[i] - tool_offset[i])
        angl = self.stat.rotation_xy
        res = self._rott00_point(coord[0], coord[1], -angl)
        coord[0] = res[0]
        coord[1] = res[1]
        return coord


    def _rott00_point(self, x1=0.0, y1=0.0, a1=0.0):
        """ rotate around 0,0 point coordinates """
        coord = [x1, y1]
        if a1 != 0:
            t = math.radians(a1)
            coord[0] = x1 * math.cos(t) - y1 * math.sin(t)
            coord[1] = x1 * math.sin(t) + y1 * math.cos(t)
        return coord


    def length_x(self, xm=None, xp=None):
        """ Calculates a length in the X direction """
        # Use previous value for xm if not supplied
        if xm is None:
            xm = self._result_box_xm.get_text()
            # Use None if no previous value exists
            if xm == "":
                xm = None
            else:
                xm = float(xm)

        # Use previous value for xp if not supplied
        if xp is None:
            xp = self._result_box_xp.get_text()
            # Use None if no previous value exists
            if xp == "":
                xp = None
            else:
                xp = float(xp)

        res = 0

        if xm is None or xp is None:
            return res

        if xm < xp:
            res = xp - xm
        else:
            res = xm - xp

        return res


    def length_y(self, ym=None, yp=None):
        """ Calculates a length in the Y direction """
        # Use previous value for ym if not supplied
        if ym is None:
            ym = self._result_box_ym.get_text()
            # Use None if no previous value exists
            if ym == "":
                ym = None
            else:
                ym = float(ym)

        # Use previous value for yp if not supplied
        if yp is None:
            yp = self._result_box_yp.get_text()
            # Use None if no previous value exists
            if yp == "":
                yp = None
            else:
                yp = float(yp)

        res = 0

        if ym is None or yp is None:
            return res

        if ym < yp:
            res = yp - ym
        else:
            res = ym - yp

        return res


    # --------------------------
    #
    #  Generic Position Calculations
    #
    # --------------------------
    def _set_auto_zero_offset(self, s="XYZ"):
        c = "G10 L2 P0"
        s = s.upper()
        if "X" in s:
            c += " X%s" % (self.halcomp["offs_x"])
            self.add_history_text("_set_auto_zero_offset_x = %.4f" % (self.halcomp["offs_x"]))
        if "Y" in s:
            c += " Y%s" % (self.halcomp["offs_y"])
            self.add_history_text("_set_auto_zero_offset_y = %.4f" % (self.halcomp["offs_y"]))
        if "Z" in s:
            c += " Z%s" % (self.halcomp["offs_z"] + self.halcomp["offs_table_offset"] + self.halcomp["offs_block_height"])
            self.add_history_text("_set_auto_zero_offset_z = %.4f" % (self.halcomp["offs_z"]))
        if "R" in s:
            c += " R%s" % (self.halcomp["offs_angle"])
            self.add_history_text("_set_auto_zero_offset_angle = %.4f" % (self.halcomp["offs_angle"]))
        if self.gcode(c) == -1:
            self.error_dialog("SET_ZERO_OFFSET_BOX NOT APPLIED CORRECTLY")
            return


    # --------------------------
    #
    #  Generic UI Methods
    #
    # --------------------------
    def common_spbtn_key_press_event(self, pin_name, gtkspinbutton, data=None):
        keyname = Gdk.keyval_name(data.keyval)
        if keyname == "Return":
            # Drop the Italics
            gtkspinbutton.modify_font(Pango.FontDescription("normal"))
            # Update the preferences
            #self.prefs.putpref(pin_name, gtkspinbutton.get_value())
        elif keyname == "Escape":
            # Restore the original value
            gtkspinbutton.set_value(self.halcomp[pin_name])

            # Drop the Italics
            gtkspinbutton.modify_font(Pango.FontDescription("normal"))
        else:
            # Set to Italics
            gtkspinbutton.modify_font(Pango.FontDescription("italic"))


    def common_spbtn_value_changed(self, pin_name, gtkspinbutton, _type=float):
        # Drop the Italics
        gtkspinbutton.modify_font(Pango.FontDescription("normal"))

        ## Update the pin
        #self.halcomp[pin_name] = gtkspinbutton.get_value()
        #
        ## Update the preferences
        #self.prefs.putpref(pin_name, gtkspinbutton.get_value(), _type)

    def settings_spbtn_value_changed(self, pin_name, gtkspinbutton, _type=float):
        # Drop the Italics
        gtkspinbutton.modify_font(Pango.FontDescription("normal"))

        # Update the pin
        self.halcomp[pin_name] = gtkspinbutton.get_value()

        # Update the preferences
        self.prefs.putpref(pin_name, gtkspinbutton.get_value(), _type)

