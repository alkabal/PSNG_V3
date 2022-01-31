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

import gtk
import linuxcnc
import pango

from .configparser import ProbeScreenConfigParser
from .util import restore_task_mode

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
            message   = _("Error, no INI File given")
            self.warning_dialog(message)
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
        self._lb_probe_xp = self.builder.get_object("lb_probe_xp")
        self._lb_probe_yp = self.builder.get_object("lb_probe_yp")
        self._lb_probe_xm = self.builder.get_object("lb_probe_xm")
        self._lb_probe_ym = self.builder.get_object("lb_probe_ym")
        self._lb_probe_lx = self.builder.get_object("lb_probe_lx")
        self._lb_probe_ly = self.builder.get_object("lb_probe_ly")
        self._lb_probe_z  = self.builder.get_object("lb_probe_z")
        self._lb_probe_d  = self.builder.get_object("lb_probe_d")
        self._lb_probe_xc = self.builder.get_object("lb_probe_xc")
        self._lb_probe_yc = self.builder.get_object("lb_probe_yc")
        self._lb_probe_a  = self.builder.get_object("lb_probe_a")

        self.frm_parents = self.builder.get_object("frm_parents")

    # --------------------------
    #
    #  MDI Command Methods
    #
    # --------------------------
    @restore_task_mode
    def gcode(self, s, data=None):
        self.command.mode(linuxcnc.MODE_MDI)
        self.command.wait_complete()

        for l in s.split("\n"):
            # Search for G1 followed by a space, otherwise we'll catch G10 too.
            if "G1 " in l:
                l += " F#<_ini[TOUCH_DEVICE]VEL_FOR_TRAVEL>"
            self.command.mdi(l)
            self.command.wait_complete()
            if self.error_poll() == -1:
                return -1
        return 0

    @restore_task_mode
    def ocode(self, s, data=None):
        self.command.mode(linuxcnc.MODE_MDI)
        self.command.wait_complete()

        self.command.mdi(s)
        self.stat.poll()   # before using some self value from linuxcnc we need to poll
        while self.stat.interp_state != linuxcnc.INTERP_IDLE:
            if self.error_poll() == -1:
            #    print("interp_err_status = %s" % (self.stat.interp_state))
            #    print("interp_err_queue = %s" % (self.stat.queue))
            #    print("interp_err_operator = %s" % (linuxcnc.OPERATOR_ERROR))
            #    print("interp_err_nml = %s" % (linuxcnc.NML_ERROR))
                return -1
            self.command.wait_complete()
            self.stat.poll()   # before using some self value from linuxcnc we need to poll
        self.command.wait_complete()
        if self.error_poll() == -1:
        #    print("interp_err2_status = %s" % (self.stat.interp_state))
        #    print("interp_err2_queue = %s" % (self.stat.queue))
        #    print("interp_err2_operator = %s" % (linuxcnc.OPERATOR_ERROR))
        #    print("interp_err2_nml = %s" % (linuxcnc.NML_ERROR))
            return -1
        return 0

    def error_poll(self):
        abort_halui = Popen(
            "halcmd getp halui.abort ", shell=True, stdout=PIPE
        ).stdout.read()
        stop_halui = Popen(
            "halcmd getp halui.program.stop ", shell=True, stdout=PIPE
        ).stdout.read()

        if "axis" in self.display:
            # AXIS polls for errors every 0.2 seconds, so we wait slightly longer to make sure it's happened.
            time.sleep(0.25)
            error_pin = Popen(
                "halcmd getp axisui.error ", shell=True, stdout=PIPE
            ).stdout.read()
            abort_axisui = Popen(
                "halcmd getp axisui.abort ", shell=True, stdout=PIPE
            ).stdout.read()
        elif "gmoccapy" in self.display:
            # gmoccapy polls for errors every 0.25 seconds, OR whatever value is in the [DISPLAY]CYCLE_TIME ini
            # setting, so we wait slightly longer to make sure it's happened.
            ms = int(self.inifile.find("DISPLAY", "CYCLE_TIME") or 250) + 50
            time.sleep(ms / 1000)
            error_pin = Popen(
                "halcmd getp gmoccapy.error ", shell=True, stdout=PIPE
            ).stdout.read()

            # Something need to be done for add to gmoccapy a hal pin gmoccapy.abort
        else:
            #self.add_history_text("WARNING : Unable to poll %s GUI for errors" % (self.display))
            message   = _("Unable to poll %s GUI for errors" % (self.display))
            self.warning_dialog(message)
            return -1

        if "TRUE" in error_pin:
            self.add_history_text("ABORT: See notification popup")
            self.command.mode(linuxcnc.MODE_MANUAL)
            self.command.wait_complete()
            return -1
        elif "TRUE" in abort_axisui or "TRUE" in abort_halui or "TRUE" in stop_halui:
            #self.add_history_text("WARNING: OPERATION STOPPED BY USER")
            message   = _("OPERATION STOPPED BY USER")
            self.warning_dialog(message)
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
        print("****  probe_screen GETINIINFO **** \n Preference file path: %s" % (temp))
        return temp

    def vcp_reload(self):
        """ Realods the VCP - e.g. after changing changing changing origin/zero points """
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
        c = "{0: <10}".format(tool_tip_text)
        if "Xm" in s:
            c += "X-=%.4f " % (xm)
            self._lb_probe_xm.set_text("%.4f" % (xm))
        if "Xc" in s:
            c += "Xc=%.4f " % (xc)
            self._lb_probe_xc.set_text("%.4f" % (xc))
        if "Xp" in s:
            c += "X+=%.4f " % (xp)
            self._lb_probe_xp.set_text("%.4f" % (xp))
        if "Lx" in s:
            c += "Lx=%.4f " % (lx)
            self._lb_probe_lx.set_text("%.4f" % (lx))
        if "Ym" in s:
            c += "Y-=%.4f " % (ym)
            self._lb_probe_ym.set_text("%.4f" % (ym))
        if "Yc" in s:
            c += "Yc=%.4f " % (yc)
            self._lb_probe_yc.set_text("%.4f" % (yc))
        if "Yp" in s:
            c += "Y+=%.4f " % (yp)
            self._lb_probe_yp.set_text("%.4f" % (yp))
        if "Ly" in s:
            c += "Ly=%.4f " % (ly)
            self._lb_probe_ly.set_text("%.4f" % (ly))
        if "Z" in s:
            c += "Z=%.4f " % (z)
            self._lb_probe_z.set_text("%.4f" % (z))
        if "D" in s:
            c += "D=%.4f" % (d)
            self._lb_probe_d.set_text("%.4f" % (d))
        if "A" in s:
            c += "Angle=%.3f" % (a)
            self._lb_probe_a.set_text("%.3f" % (a))

        self.add_history_text(c)

    def add_history_text(self, text):
        # Prepend a timestamp to all History lines
        text = datetime.now().strftime("%H:%M:%S  ") + text

        # Remove the oldest history entries when we have a large
        # number of entries.
        i = self.buffer.get_end_iter()
        if i.get_line() > 1000:
            i.backward_line()
            self.buffer.delete(i, self.buffer.get_end_iter())

        # Add the line of text to the top of the history
        i.set_line(0)
        self.buffer.insert(i, "%s \n" % (text))

    def _dialog(self, gtk_type, gtk_buttons, message, secondary=None, title=_("Probe Screen NG")):
        """ displays a dialog """
        dialog = gtk.MessageDialog(
            self.window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk_type,
            gtk_buttons,
            message,
        )
        # if there is a secondary message then the first message text is bold
        if secondary:
            dialog.format_secondary_text(secondary)
        dialog.set_keep_above(True)
        dialog.show_all()
        dialog.set_title(title)
        responce = dialog.run()
        dialog.destroy()
        return responce == gtk.RESPONSE_OK

    def warning_dialog(self, message, secondary=None, title=_("Warning Probe Screen NG")):
        """ displays a warning dialog """
        if self.halcomp["chk_popup_style"] == True or Popen('halcmd getp motion.motion-enabled',stdout=PIPE,shell=True).communicate()[0].strip() == 'FALSE':
            return self._dialog(gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, message, secondary, title)
        else:
#            if self.gcode("M160") == -1:         #o<clear-axis-info> call
#                return
            if secondary:
                self.add_history_text("WARNING: %s" % (message))
                self.add_history_text("WARNING: %s" % (secondary))
                #self.gcode("(DEBUG,**** %s ****)" % (message))
                #self.gcode("(DEBUG,**** %s ****)" % (secondary))
            else:
                self.add_history_text("WARNING: %s" % (message))
                #self.gcode("(DEBUG,**** %s ****)" % (message))


    def error_dialog(self, message, secondary=None, title=_("Error Probe Screen NG")):
        """ displays a error dialog and abort """
        if self.halcomp["chk_popup_style"] == True or Popen('halcmd getp motion.motion-enabled',stdout=PIPE,shell=True).communicate()[0].strip() == 'FALSE':
            #self._dialog(gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, message, secondary, title)
            return self._dialog(gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, message, secondary, title)
        else:
#            if self.gcode("M160") == -1:         #o<clear-axis-info> call
#                return
            if secondary:
                self.add_history_text("DEBUG: %s" % (message))
                self.add_history_text("ABORT: %s" % (secondary))
                self.gcode("(DEBUG,**** %s ****)" % (message))
                self.gcode("(ABORT,**** %s ****)" % (secondary))
            else:
                self.add_history_text("ABORT: %s" % (message))
                self.gcode("(ABORT,**** %s ****)" % (message))


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

            if Popen('halcmd getp motion.motion-enabled',stdout=PIPE,shell=True).communicate()[0].strip() == 'FALSE':
                message   = _("Please turn machine on")
                secondary = _("You can retry once done")
                self.warning_dialog(message, secondary)
                return -1


            if self.error_poll() == -1:
                message   = _("Please dismiss & act upon all errors")
                secondary = _("You can retry once done")
                self.warning_dialog(message, secondary)
                return -1

            # Execute wrapped function
            return f(self, *args, **kwargs)

        return wrapper



    @classmethod
    def ensure_is_not_touchplate(cls, f):
        """ Ensures is not touchplate selected, otherwise, shows a warning dialog """

        @wraps(f)
        def wrapper(self, *args, **kwargs):

            if self.halcomp["chk_touch_plate_selected"] == True:
                message   = _("You can't use this function using touchplate")
                self.warning_dialog(message)
                return -1

            # Execute wrapped function
            return f(self, *args, **kwargs)

        return wrapper


    # --------------------------
    #
    #  Generic Probe Movement Methods
    #
    # --------------------------
    def clearance_z_down(self, data=None):
        # move Z - clearance_z
        s = """G91
        G1 Z-%f
        G90""" % (self.halcomp["clearance_z"])
        if self.gcode(s) == -1:
            return -1
        return 0

    def clearance_z_up(self, data=None):
        # move Z + clearance_z
        s = """G91
        G1 Z%f
        G90""" % (self.halcomp["clearance_z"])
        if self.gcode(s) == -1:
            return -1
        return 0


    def probed_position_with_offsets(self):
        self.stat.poll()   # before using some self value from linuxcnc we need to poll
        probed_position = list(self.stat.probed_position)
        coord = list(self.stat.probed_position)
        g5x_offset = list(self.stat.g5x_offset)
        g92_offset = list(self.stat.g92_offset)
        tool_offset = list(self.stat.tool_offset)
        #print "g5x_offset  = ",g5x_offset
        #print "g92_offset  = ",g92_offset
        #print "tool_offset  = ",tool_offset
        #print "actual position  = ",self.stat.actual_position
        #print "position  = ",self.stat.position
        #print "joint_actual position  = ",self.stat.joint_actual_position
        #print "joint_position  = ",self.stat.joint_position
        #print "probed position  = ",self.stat.probed_position
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
            xm = self._lb_probe_xm.get_text()
            # Use None if no previous value exists
            if xm == "":
                xm = None
            else:
                xm = float(xm)

        # Use previous value for xp if not supplied
        if xp is None:
            xp = self._lb_probe_xp.get_text()
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
            ym = self._lb_probe_ym.get_text()
            # Use None if no previous value exists
            if ym == "":
                ym = None
            else:
                ym = float(ym)

        # Use previous value for yp if not supplied
        if yp is None:
            yp = self._lb_probe_yp.get_text()
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
    def set_zerro(self, s="XYZ", x=0.0, y=0.0, z=0.0):
        if self.halcomp["chk_set_zero"]:
            #  Z current position
            self.stat.poll()   # before using some self value from linuxcnc we need to poll
            tmpz = (
                self.stat.position[2]
                - self.stat.g5x_offset[2]
                - self.stat.g92_offset[2]
                - self.stat.tool_offset[2]
            )
            c = "G10 L20 P0"
            s = s.upper()
            if "X" in s:
                x += self.halcomp["offs_x"]
                c += " X%s" % (x)
            if "Y" in s:
                y += self.halcomp["offs_y"]
                c += " Y%s" % (y)
            if "Z" in s:
                tmpz = tmpz - z + self.halcomp["offs_z"]
                c += " Z%s" % (tmpz)
            if self.gcode(c) == -1:                                                                                 # Need your review choosing this or only self.gcode(c) timesleep
               return

    # --------------------------
    #
    #  Generic UI Methods
    #
    # --------------------------
    def on_common_spbtn_key_press_event(self, pin_name, gtkspinbutton, data=None):
        keyname = gtk.gdk.keyval_name(data.keyval)
        if keyname == "Return":
            # Drop the Italics
            gtkspinbutton.modify_font(pango.FontDescription("normal"))
        elif keyname == "Escape":
            # Restore the original value
            gtkspinbutton.set_value(self.halcomp[pin_name])

            # Drop the Italics
            gtkspinbutton.modify_font(pango.FontDescription("normal"))
        else:
            # Set to Italics
            gtkspinbutton.modify_font(pango.FontDescription("italic"))

    def on_common_spbtn_value_changed(self, pin_name, gtkspinbutton, data=None, _type=float):
        # Drop the Italics
        gtkspinbutton.modify_font(pango.FontDescription("normal"))

        # Update the pin
        self.halcomp[pin_name] = gtkspinbutton.get_value()

        # Update the preferences
        self.prefs.putpref(pin_name, gtkspinbutton.get_value(), _type)

        # Update history display
        self.add_history_text("%s = %.4f" % (pin_name, gtkspinbutton.get_value()))
