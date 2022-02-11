# stdglue - canned prolog and epilog functions for the remappable builtin codes (T,M6,M61,S,F)
#
# we dont use argspec to avoid the generic error message of the argspec prolog and give more
# concise ones here

# cycle_prolog,cycle_epilog: generic code-independent support glue for oword sub cycles
#
# these are provided as starting point - for more concise error message you would better
# write a prolog specific for the code
#
# Usage:
#REMAP=G84.3  modalgroup=1 argspec=xyzqp prolog=cycle_prolog ngc=g843 epilog=cycle_epilog

import emccanon
import linuxcnc
from interpreter import *
from emccanon import MESSAGE
from subprocess import PIPE, Popen
throw_exceptions = 1
import hal
import hal_glib
import time

# REMAP=S   prolog=setspeed_prolog  ngc=setspeed epilog=setspeed_epilog
# exposed parameter: #<speed>

def setspeed_prolog(self,**words):
    try:
        c = self.blocks[self.remap_level]
        if not c.s_flag:
            self.set_errormsg("S requires a value")
            return INTERP_ERROR
        self.params["speed"] = c.s_number
    except Exception as e:
        self.set_errormsg("S/setspeed_prolog: %s)" % (e))
        return INTERP_ERROR
    return INTERP_OK

def setspeed_epilog(self,**words):
    try:
        if not self.value_returned:
            r = self.blocks[self.remap_level].executing_remap
            self.set_errormsg("the %s remap procedure %s did not return a value"
                             % (r.name,r.remap_ngc if r.remap_ngc else r.remap_py))
            return INTERP_ERROR
        if self.return_value < -TOLERANCE_EQUAL: # 'less than 0 within interp's precision'
            self.set_errormsg("S: remap procedure returned %f" % (self.return_value))
            return INTERP_ERROR
        if self.blocks[self.remap_level].builtin_used:
            pass
            #print "---------- S builtin recursion, nothing to do"
        else:
            self.speed = self.params["speed"]
            emccanon.enqueue_SET_SPINDLE_SPEED(self.speed)
        return INTERP_OK
    except Exception as e:
        self.set_errormsg("S/setspeed_epilog: %s)" % (e))
        return INTERP_ERROR
    return INTERP_OK

# REMAP=F   prolog=setfeed_prolog  ngc=setfeed epilog=setfeed_epilog
# exposed parameter: #<feed>

def setfeed_prolog(self,**words):
    try:
        c = self.blocks[self.remap_level]
        if not c.f_flag:
            self.set_errormsg("F requires a value")
            return INTERP_ERROR
        self.params["feed"] = c.f_number
    except Exception as e:
        self.set_errormsg("F/setfeed_prolog: %s)" % (e))
        return INTERP_ERROR
    return INTERP_OK

def setfeed_epilog(self,**words):
    try:
        if not self.value_returned:
            r = self.blocks[self.remap_level].executing_remap
            self.set_errormsg("the %s remap procedure %s did not return a value"
                             % (r.name,r.remap_ngc if r.remap_ngc else r.remap_py))
            return INTERP_ERROR
        if self.blocks[self.remap_level].builtin_used:
            pass
            #print "---------- F builtin recursion, nothing to do"
        else:
            self.feed_rate = self.params["feed"]
            emccanon.enqueue_SET_FEED_RATE(self.feed_rate)
        return INTERP_OK
    except Exception as e:
        self.set_errormsg("F/setfeed_epilog: %s)" % (e))
        return INTERP_ERROR
    return INTERP_OK

# REMAP=T   prolog=prepare_prolog ngc=prepare epilog=prepare_epilog
# exposed parameters: #<tool> #<pocket>

def prepare_prolog(self,**words):
    try:
        cblock = self.blocks[self.remap_level]
        if not cblock.t_flag:
            self.set_errormsg("T requires a tool number")
            return INTERP_ERROR
        tool  = cblock.t_number
        if tool:
            (status, pocket) = self.find_tool_pocket(tool)
            if status != INTERP_OK:
                self.set_errormsg("T%d: pocket not found" % (tool))
                return status
        else:
            pocket = -1 # this is a T0 - tool unload
        self.params["tool"] = tool
        self.params["pocket"] = pocket
        return INTERP_OK
    except Exception as e:
        self.set_errormsg("T%d/prepare_prolog: %s" % (int(words['t']), e))
        return INTERP_ERROR

def prepare_epilog(self, **words):
    try:
        if not self.value_returned:
            r = self.blocks[self.remap_level].executing_remap
            self.set_errormsg("the %s remap procedure %s did not return a value"
                             % (r.name,r.remap_ngc if r.remap_ngc else r.remap_py))
            return INTERP_ERROR
        if self.blocks[self.remap_level].builtin_used:
            #print "---------- T builtin recursion, nothing to do"
            return INTERP_OK
        else:
            if self.return_value > 0:
                self.selected_tool = int(self.params["tool"])
                self.selected_pocket = int(self.params["pocket"])
                emccanon.SELECT_TOOL(self.selected_tool)
                return INTERP_OK
            else:
                self.set_errormsg("T%d: aborted (return code %.1f)" % (int(self.params["tool"]),self.return_value))
                return INTERP_ERROR
    except Exception as e:
        self.set_errormsg("T%d/prepare_epilog: %s" % (tool,e))
        return INTERP_ERROR

# REMAP=M6  modalgroup=6 prolog=change_prolog ngc=change epilog=change_epilog
# exposed parameters:
#    #<current_tool>
#    #<selected_tool>
#    #<current_pocket>
#    #<selected_pocket>

def change_prolog(self, **words):
    try:
        # this is relevant only when using iocontrol-v2.
        if self.params[5600] > 0.0:
            if self.params[5601] < 0.0:
                self.set_errormsg("Toolchanger hard fault %d" % (int(self.params[5601])))
                return INTERP_ERROR
            print("change_prolog: Toolchanger soft fault %d" % int(self.params[5601]))

        if self.selected_pocket < 0:
            self.set_errormsg("M6: no tool prepared")
            return INTERP_ERROR
        if self.cutter_comp_side:
            self.set_errormsg("Cannot change tools with cutter radius compensation on")
            return INTERP_ERROR
        self.params["current_tool"] = self.current_tool
        self.params["selected_tool"] = self.selected_tool
        self.params["current_pocket"] = self.current_pocket
        self.params["selected_pocket"] = self.selected_pocket
        return INTERP_OK
    except Exception as e:
        self.set_errormsg("M6/change_prolog: %s" % (e))
        return INTERP_ERROR

def change_epilog(self, **words):
    try:
        if not self.value_returned:
            r = self.blocks[self.remap_level].executing_remap
            self.set_errormsg("the %s remap procedure %s did not return a value"
                             % (r.name,r.remap_ngc if r.remap_ngc else r.remap_py))
            yield INTERP_ERROR
        # this is relevant only when using iocontrol-v2.
        if self.params[5600] > 0.0:
            if self.params[5601] < 0.0:
                self.set_errormsg("Toolchanger hard fault %d" % (int(self.params[5601])))
                yield INTERP_ERROR
            print("change_epilog: Toolchanger soft fault %d" % int(self.params[5601]))

        if self.blocks[self.remap_level].builtin_used:
            #print "---------- M6 builtin recursion, nothing to do"
            yield INTERP_OK
        else:
            if self.return_value > 0.0:
                # commit change
                self.selected_pocket =  int(self.params["selected_pocket"])
                emccanon.CHANGE_TOOL(self.selected_pocket)
                self.current_pocket = self.selected_pocket
                self.selected_pocket = -1
                self.selected_tool = -1
                # cause a sync()
                self.set_tool_parameters()
                self.toolchange_flag = True
                yield INTERP_EXECUTE_FINISH
            else:
                self.set_errormsg("M6 aborted (return code %.1f)" % (self.return_value))
                yield INTERP_ERROR
    except Exception as e:
        self.set_errormsg("M6/change_epilog: %s" % (e))
        yield INTERP_ERROR

# REMAP=M61  modalgroup=6 prolog=settool_prolog ngc=settool epilog=settool_epilog
# exposed parameters: #<tool> #<pocket>

def settool_prolog(self,**words):
    try:
        c = self.blocks[self.remap_level]
        if not c.q_flag:
            self.set_errormsg("M61 requires a Q parameter")
            return INTERP_ERROR
        tool = int(c.q_number)
        if tool < -TOLERANCE_EQUAL: # 'less than 0 within interp's precision'
            self.set_errormsg("M61: Q value < 0")
            return INTERP_ERROR
        (status,pocket) = self.find_tool_pocket(tool)
        if status != INTERP_OK:
            self.set_errormsg("M61 failed: requested tool %d not in table" % (tool))
            return status
        self.params["tool"] = tool
        self.params["pocket"] = pocket
        return INTERP_OK
    except Exception as e:
        self.set_errormsg("M61/settool_prolog: %s)" % (e))
        return INTERP_ERROR

def settool_epilog(self,**words):
    try:
        if not self.value_returned:
            r = self.blocks[self.remap_level].executing_remap
            self.set_errormsg("the %s remap procedure %s did not return a value"
                             % (r.name,r.remap_ngc if r.remap_ngc else r.remap_py))
            return INTERP_ERROR

        if self.blocks[self.remap_level].builtin_used:
            #print "---------- M61 builtin recursion, nothing to do"
            return INTERP_OK
        else:
            if self.return_value > 0.0:
                self.current_tool = int(self.params["tool"])
                self.current_pocket = int(self.params["pocket"])
                emccanon.CHANGE_TOOL_NUMBER(self.current_pocket)
                # cause a sync()
                self.tool_change_flag = True
                self.set_tool_parameters()
            else:
                self.set_errormsg("M61 aborted (return code %.1f)" % (self.return_value))
                return INTERP_ERROR
    except Exception as e:
        self.set_errormsg("M61/settool_epilog: %s)" % (e))
        return INTERP_ERROR

# educational alternative: M61 remapped to an all-Python handler
# demo - this really does the same thing as the builtin (non-remapped) M61
#
# REMAP=M61 modalgroup=6 python=set_tool_number

def set_tool_number(self, **words):
    try:
        c = self.blocks[self.remap_level]
        if c.q_flag:
            toolno = int(c.q_number)
        else:
            self.set_errormsg("M61 requires a Q parameter")
            return status
        (status,pocket) = self.find_tool_pocket(toolno)
        if status != INTERP_OK:
            self.set_errormsg("M61 failed: requested tool %d not in table" % (toolno))
            return status
        self.current_pocket = pocket
        self.current_tool = toolno
        emccanon.CHANGE_TOOL_NUMBER(pocket)
        # cause a sync()
        self.tool_change_flag = True
        self.set_tool_parameters()
        self.execute("g43 h%d"% toolno)                      # added autolength correction
        return INTERP_OK
    except Exception as e:
        self.set_errormsg("M61/set_tool_number: %s" % (e))
        return INTERP_ERROR

_uvw = ("u","v","w","a","b","c")
_xyz = ("x","y","z","a","b","c")
# given a plane, return  sticky words, incompatible axis words and plane name
# sticky[0] is also the movement axis
_compat = {
    emccanon.CANON_PLANE_XY : (("z","r"),_uvw,"XY"),
    emccanon.CANON_PLANE_YZ : (("x","r"),_uvw,"YZ"),
    emccanon.CANON_PLANE_XZ : (("y","r"),_uvw,"XZ"),
    emccanon.CANON_PLANE_UV : (("w","r"),_xyz,"UV"),
    emccanon.CANON_PLANE_VW : (("u","r"),_xyz,"VW"),
    emccanon.CANON_PLANE_UW : (("v","r"),_xyz,"UW")}

# extract and pass parameters from current block, merged with extra parameters on a continuation line
# keep tjose parameters across invocations
# export the parameters into the oword procedure
def cycle_prolog(self,**words):
    # self.sticky_params is assumed to have been initialized by the
    # init_stgdlue() method below
    global _compat
    try:
        # determine whether this is the first or a subsequent call
        c = self.blocks[self.remap_level]
        r = c.executing_remap
        if c.g_modes[1] == r.motion_code:
            # first call - clear the sticky dict
            self.sticky_params[r.name] = dict()

        self.params["motion_code"] = c.g_modes[1]

        (sw,incompat,plane_name) =_compat[self.plane]
        for (word,value) in list(words.items()):
            # inject current parameters
            self.params[word] = value
            # record sticky words
            if word in sw:
                if self.debugmask & 0x00080000: print("%s: record sticky %s = %.4f" % (r.name,word,value))
                self.sticky_params[r.name][word] = value
            if word in incompat:
                return "%s: Cannot put a %s in a canned cycle in the %s plane" % (r.name, word.upper(), plane_name)

        # inject sticky parameters which were not in words:
        for (key,value) in list(self.sticky_params[r.name].items()):
            if not key in words:
                if self.debugmask & 0x00080000: print("%s: inject sticky %s = %.4f" % (r.name,key,value))
                self.params[key] = value

        if not "r" in self.sticky_params[r.name]:
            return "%s: cycle requires R word" % (r.name)
        else:
            if self.sticky_params[r.name] <= 0.0:
                return "%s: R word must be > 0 if used (%.4f)" % (r.name, words["r"])

        if "l" in words:
            # checked in interpreter during block parsing
            # if l <= 0 or l not near an int
            self.params["l"] = words["l"]

        if "p" in words:
            p = words["p"]
            if p < 0.0:
                return "%s: P word must be >= 0 if used (%.4f)" % (r.name, p)
            self.params["p"] = p

        if self.feed_rate == 0.0:
            return "%s: feed rate must be > 0" % (r.name)
        if self.feed_mode == INVERSE_TIME:
            return "%s: Cannot use inverse time feed with canned cycles" % (r.name)
        if self.cutter_comp_side:
            return "%s: Cannot use canned cycles with cutter compensation on" % (r.name)
        return INTERP_OK

    except Exception as e:
        raise
        return "cycle_prolog failed: %s" % (e)

# make sure the next line has the same motion code, unless overriden by a
# new G code
def cycle_epilog(self,**words):
    try:
        c = self.blocks[self.remap_level]
        self.motion_mode = c.executing_remap.motion_code # retain the current motion mode
        return INTERP_OK
    except Exception as e:
        return "cycle_epilog failed: %s" % (e)

# this should be called from TOPLEVEL __init__()
def init_stdglue(self):
    self.sticky_params = dict()

#####################################
# pure python remaps
#####################################

# REMAP=M6 python=ignore_m6
#
# m5 silently ignored
#
def ignore_m6(self,**words):
    try:
        return INTERP_OK
    except Exception as e:
        return "Ignore M6 failed: %s" % (e)

# REMAP=T python=index_lathe_tool_with_wear
#
# uses T101 for tool 1, wear 1 no M6 needed
# tool offsets for tool 1 and tool 10001 are added together.
#
def index_lathe_tool_with_wear(self,**words):
    # only run this if we are really moving the machine
    # skip this if running task for the screen
    if not self.task:
        return INTERP_OK
    try:
        # check there is a tool number from the Gcode
        cblock = self.blocks[self.remap_level]
        if not cblock.t_flag:
            self.set_errormsg("T requires a tool number")
            return INTERP_ERROR
        tool_raw = int(cblock.t_number)

        # interpet the raw tool number into tool and wear number
        # If it's less then 100 someone forgot to add the wear #, so we added it automatically
        # separate out tool number (tool) and wear number (wear), add 10000 to wear number
        if tool_raw <100:
            tool_raw=tool_raw*100
        tool = int(tool_raw/100)
        wear = 10000 + tool_raw % 100

        # uncomment for debugging
        #print'***tool#',cblock.t_number,'toolraw:',tool_raw,'tool split:',tool,'wear split',wear
        if tool:
            # check for tool number entry in tool file
            (status, pocket) = self.find_tool_pocket(tool)
            if status != INTERP_OK:
                self.set_errormsg("T%d: tool entry not found" % (tool))
                return status
        else:
            tool = -1
            pocket = -1
            wear = -1
        self.params["tool"] = tool
        self.params["pocket"] = pocket
        self.params["wear"] =  wear

        # index tool immediately to tool number
        self.selected_tool = int(self.params["tool"])
        self.selected_pocket = int(self.params["pocket"])
        emccanon.SELECT_TOOL(self.selected_tool)
        if self.selected_pocket < 0:
            self.set_errormsg("T0 not valid")
            return INTERP_ERROR
        if self.cutter_comp_side:
            self.set_errormsg("Cannot change tools with cutter radius compensation on")
            return INTERP_ERROR
        self.params["current_tool"] = self.current_tool
        self.params["selected_tool"] = self.selected_tool
        self.params["current_pocket"] = self.current_pocket
        self.params["selected_pocket"] = self.selected_pocket

        # change tool
        try:
            self.selected_pocket =  int(self.params["selected_pocket"])
            emccanon.CHANGE_TOOL(self.selected_pocket)
            self.current_pocket = self.selected_pocket
            self.selected_pocket = -1
            self.selected_tool = -1
            # cause a sync()
            self.set_tool_parameters()
            self.toolchange_flag = True
        except:
            self.set_errormsg("T change aborted (return code %.1f)" % (self.return_value))
            return INTERP_ERROR

        # add tool offset
        self.execute("g43 h%d"% tool)
        # if the wear offset is specified, add it's offset
        if wear>10000:
            self.execute("g43.2 h%d"% wear)
        return INTERP_OK

    except Exception as e:
        print(e)
        self.set_errormsg("T%d index_lathe_tool_with_wear: %s" % (int(words['t']), e))
        return INTERP_ERROR



##******************************************
# Required HAL settings
##******************************************
#net manual-tool-change-loop    iocontrol.0.tool-change      => iocontrol.0.tool-changed
#net manual-tool-prep-loop      iocontrol.0.tool-prepare     => iocontrol.0.tool-prepared
##******************************************

##******************************************
# Optional HAL settings for config with 3D-PROBE
##******************************************
#loadrt or2                    names=or2.combined-touch
#loadrt and2                   names=and2.combined-probe
#loadrt and2                   names=and2.combined-setter
#loadrt debounce               cfg=1
#addf or2.combined-touch       servo-thread
#addf and2.combined-probe      servo-thread
#addf and2.combined-setter     servo-thread
#addf debounce.0               servo-thread
#
#net touch-probe               <= [HMOT](CARD0).gpio.001.in_not                        # probe is NC with pullup from 5v wire
#net touch-probe               => and2.combined-probe.in0
#setp                             and2.combined-probe.in1 1                            # for correct status at startup
#net touch-probe-on-off        => and2.combined-probe.in1                              # M165 activate / M166 inhibit output from custom Mcode
#net touch-probe-and2-psng     <= and2.combined-probe.out
#net touch-probe-and2-psng     => or2.combined-touch.in0
#
#net touch-setter              <= [HMOT](CARD0).gpio.002.in_not                        # setter is NC NPN 24v with pullup on the mesa card
#net touch-setter              => and2.combined-setter.in0
#setp                             and2.combined-setter.in1 1                           # for correct status at startup
#net touch-setter-on-off       => and2.combined-setter.in1                             # M167 activate / M168 inhibit output from custom Mcode
#net touch-setter-and2-psng    <= and2.combined-setter.out
#net touch-setter-and2-psng    => or2.combined-touch.in1
#
#net touch-device-muxed        <= or2.combined-touch.out
##net touch-device-muxed        => motion.probe-input
#
#setp                            debounce.0.delay 3
#net touch-device-muxed       => debounce.0.0.in
#net probe-in-debounced       <= debounce.0.0.out
#net probe-in-debounced       => motion.probe-input
##******************************************

##******************************************
# required INI settings exemple with metric unit mm (Abs coordinates/ machine based units)
##******************************************

##******************************************
#[RS274NGC]
#REMAP=M6   modalgroup=10 python=tool_probe_m6
##******************************************

##******************************************
#[DISPLAY]
##******************************************
## Used for clear gcode MSG DEBUG ERROR from axis GUI
#CLEAR_GUI_NOTIF_MCODE = 160
##******************************************

##******************************************
#[EMCIO]
#EMCIO = io
#TOOL_TABLE = *******.tbl
#TOOL_CHANGE_WITH_SPINDLE_ON = 0
#
## Optional allow to move to Z home before each tool change or move to tool setter with stglue remap_probe_m6
#TOOL_CHANGE_QUILL_UP = 0
#
## Do not use this setting with python remap !!!
##TOOL_CHANGE_POSITION = 0 0 0
##******************************************

##******************************************
#[TOOL_SETTER]
## Absolute XYZ G53 machine coordinates of the toolsetter pad
### you need to keep TS_HEIGHT + PROBE_MAX_Z value inside your machine limit range
#TS_POS_X = 0
#TS_POS_Y = 0
#TS_POS_Z = -35
#
## Maximum probing search distance
### you need to keep TS_HEIGHT + PROBE_MAX_Z value inside your machine limit range
#PROBE_MAX_Z = 60
#
## Fast first probe tool velocity : spring mounted touchplate/toolsetter allow faster speed
#VEL_FOR_SEARCH = 150
#
## Slow final probe velocity
#VEL_FOR_PROBE = 10
#
## ts_height is used only with "real toolsetter" or "touchplate" at fixed location
#TS_HEIGHT = 1.5
#
## Latched distance after probing use value like 1mm (more than the spring movement)
#LATCH = 2
#
## You can use latch_reverse_probing with G38.5 with value like 2mm (more than the distance needed for release the contact)
## or 0 if you want to inhibit G38.5)
#latch_reverse_probing = 2
##******************************************

##******************************************
#[TOOL_CHANGE]
## Allow user to chose original popup style dialog box for toolchange or new method using pause and Gcode message
#################TODO
#POPUP_STYLE = 1
#
## After tool change choose if you wan't to go back to last position or return to "Quil up" or "z travel position" and finally to XY change position
#GO_BACK_LAST_POSITION = 1
#
## Position absolue in machine coordinate for all XY rapid move G53 machine cooordinates
#Z_TRAVEL_POSITION = 0
#
## Abs coordinates for tool change point G53 machine cooordinates
#X = 0
#Y = 0
#Z = 0
##******************************************

##******************************************
#[TOUCH_DEVICE]
##******************************************
## Allow user to define the toolnumber used for securing the probe (need to be in the tooltable)
## If you do not have a 3D Probe you need to set PROBE_NUMBER = 0
#PROBE_NUMBER = 999
#
## Used here for manage tool setter input
#PROBE_ON_MCODE = 165
#PROBE_Off_MCODE = 166
#
## Only used here for reactivate tool setter input if they are deactivated by other way like PSNG or user
#TOOL_SETTER_ON_MCODE = 167
#TOOL_SETTER_OFF_MCODE = 168
##******************************************

def tool_probe_m6(self, **words):

# only run this if we are really moving the machine so skip this if running task as simulation
    if not self.task:
        self.execute("(DEBUG,Remap tool_probe_m6 stglue inibited in simulation mode)")
        print("Remap tool_probe_m6 stglue inibited in simulation mode")
        yield INTERP_OK

#    # Safety check if ts_height is configured
#    if self.params["_ini[TOOL_SETTER]TS_HEIGHT"] <= 0:
#        clear_axis_all(self)
#        self.execute("(DEBUG,stglue tool_probe_m6 remap error : TOOLSETTER HEIGHT NOT CORRECTLY CONFIGURED)")
#        self.set_errormsg("stglue tool_probe_m6 remap error : TOOLSETTER HEIGHT NOT CORRECTLY CONFIGURED")
#        yield INTERP_ERROR

    try:
    # Safety check if ts_height is configured
        self.params["ts_height"] = float(self.params["_ini[TOOL_SETTER]TS_HEIGHT"])
        if self.params["ts_height"] <= 0:
            self.execute("(DEBUG,stglue tool_probe_m6 remap error : TOOLSETTER HEIGHT NOT CORRECTLY CONFIGURED)")
            self.set_errormsg("stglue tool_probe_m6 remap error : TOOLSETTER HEIGHT NOT CORRECTLY CONFIGURED")
            yield INTERP_ERROR
    except:
            self.execute("(DEBUG,stglue tool_probe_m6 remap error : TOOLSETTER MISSING FROM INI)")
            self.set_errormsg("stglue tool_probe_m6 remap error : TOOLSETTER MISSING FROM INI")
            yield INTERP_ERROR





## todo add all self.params["_ini
#self.params["_ini[EMCIO]TOOL_CHANGE_QUILL_UP"]
#self.params["_ini[EMCIO]TOOL_CHANGE_WITH_SPINDLE_ON"]
#self.params["_ini[EMCMOT]NUM_SPINDLES"]
#self.params["_ini[JOINT_2]HOME"]
#self.params["_ini[TOOL_CHANGE]Z_TRAVEL_POSITION"]
#self.params["_ini[TOOL_CHANGE]X"]
#self.params["_ini[TOOL_CHANGE]Z"]
#self.params["_ini[TOOL_CHANGE]POPUP_STYLE"]
#self.params["_ini[JOINT_0]MAX_LIMIT"]
#self.params["_ini[JOINT_1]MAX_LIMIT"]
#self.params["_ini[AXIS_Z]MIN_LIMIT"]
#self.params["_ini[TOOL_SETTER]TS_POS_X"]
#self.params["_ini[TOOL_SETTER]TS_POS_Y"]
#self.params["_ini[TOOL_SETTER]TS_POS_Z"]
#self.params["_ini[TOOL_SETTER]TS_MAX_TOOL_LGT"]
#self.params["_ini[TOOL_SETTER]CLEARANCE_Z"]
#self.params["_ini[TOOL_SETTER]PROBE_MAX_LATCH"]


    try:
        self.params["probe_number"] = int(self.params["_ini[TOUCH_DEVICE]PROBE_NUMBER"])
    except:
        print("!!!! PROBE_NUMBER CONFIG MISSING FROM INI, USE DEFAULT VALUE 999 !!!!")
        self.execute("(DEBUG,!!!! PROBE_NUMBER CONFIG MISSING FROM INI, USE DEFAULT VALUE 999 !!!!)")
        self.probe_number = 999

    try:
        self.params["probe_on_mcode"] = self.params["_ini[TOUCH_DEVICE]PROBE_ON_MCODE"]              # Custom Mcode do halcmd sets touch-probe-on-off 1    signal linked to and2.combined-probe.in1
    except:
        self.set_errormsg("tool_probe_m6 remap error: PROBE_ON_MCODE CONFIG MISSING FROM INI")
        yield INTERP_ERROR

    try:
        self.params["probe_off_mcode"] = self.params["_ini[TOUCH_DEVICE]PROBE_OFF_MCODE"]            # Custom Mcode do halcmd sets touch-probe-on-off 1    signal linked to and2.combined-probe.in1
    except:
        self.set_errormsg("tool_probe_m6 remap error: PROBE_OFF_MCODE CONFIG MISSING FROM INI")
        yield INTERP_ERROR

    try:
        self.params["tool_setter_on_mcode"] = self.params["_ini[TOUCH_DEVICE]TOOL_SETTER_ON_MCODE"]  # Custom Mcode do halcmd sets touch-setter-on-off 1   signal linked to and2.combined-setter.in1
    except:
        self.set_errormsg("tool_probe_m6 remap error: TOOL_SETTER_ON_MCODE CONFIG MISSING FROM INI")
        yield INTERP_ERROR

    try:
        self.params["clear_gui_notif_mcode"] = self.params["_ini[DISPLAY]CLEAR_GUI_NOTIF_MCODE"]  # Custom Mcode do halcmd sets touch-setter-on-off 1   signal linked to and2.combined-setter.in1
    except:
        self.set_errormsg("tool_probe_m6 remap error: CLEAR_GUI_NOTIF_MCODE CONFIG MISSING FROM INI")
        yield INTERP_ERROR

    try:
        self.params["change_x_limit_mcode"] = self.params["_ini[TOOL_SETTER]CHANGE_X_LIMIT_MCODE"]  # Custom Mcode do halcmd halcmd setp ini.y.max_limit $jointlength
    except:
        self.set_errormsg("tool_probe_m6 remap error: CHANGE_X_LIMIT_MCODE CONFIG MISSING FROM INI")
        yield INTERP_ERROR

    try:
        self.params["change_y_limit_mcode"] = self.params["_ini[TOOL_SETTER]CHANGE_Y_LIMIT_MCODE"]  # Custom Mcode do halcmd halcmd setp ini.y.max_limit $jointlength
    except:
        self.set_errormsg("tool_probe_m6 remap error: CHANGE_Y_LIMIT_MCODE CONFIG MISSING FROM INI")
        yield INTERP_ERROR


    # create a connection to the linuxcnc status and command channel
    self.cmd  = linuxcnc.command()
    self.stat = linuxcnc.stat()
    self.stat.poll()# get current Linuxcnc.stat values

    # Saving the machine unit at startup
    METRIC_BASED = (bool(self.params['_metric_machine']))     # do not work prior to linuxcnc 2.8.3

    # Saving G90 G91 at startup
    ABSOLUTE_FLAG = (bool(self.params["_absolute"]))

    # Saving feed at startup
    FEED_BACKUP = (bool(self.params["_feed"]))

    # cancel tool offset
    self.execute("G49")

    # Force to stop mist and flood
    self.execute("M9")

    # record current position XYZ but Z
    initial_X = emccanon.GET_EXTERNAL_POSITION_X()
    initial_Y = emccanon.GET_EXTERNAL_POSITION_Y()
    initial_Z = emccanon.GET_EXTERNAL_POSITION_Z()

    # turn off all spindles if required                        #(commented out usage possible for 2.9)
#    if not self.tool_change_with_spindle_on:
#        for s in range(0,self.num_spindles):
#            emccanon.STOP_SPINDLE_TURNING(s)

    if not self.params["_ini[EMCIO]TOOL_CHANGE_WITH_SPINDLE_ON"]:
        for s in range(0,int(self.params["_ini[EMCMOT]NUM_SPINDLES"])):
            emccanon.STOP_SPINDLE_TURNING(s)
            wait(self)

    # Bypass measure can be used if you create the tool table with PSNG so for some repetable tool you can bypass autolength
    # You can use PSNG for control this pin or you can create your own with pyvcp or similar
    if Popen('halcmd getp probe.ts_chk_use_tool_measurement',stdout=PIPE,shell=True).communicate()[0].strip() == 'FALSE':
        BYPASS_MEASURE = 1
    else:
        BYPASS_MEASURE = 0
        print("If you get message (<commandline>:0: pin or parameter 'probe.ts_chk_use_tool_measurement' not found) do not take care without PSNG you can't bypass auto tool lengt")


    try:
        # we need to be in machine based units
        # if we aren't - switch
        BACKUP_METRIC_FLAG = self.params["_metric"]
        if BACKUP_METRIC_FLAG != METRIC_BASED:
            print("not right Units: {}".format(bool(self.params["_metric"])))
            if METRIC_BASED:
                print("switched Units to metric")
                self.execute("G21")
            else:
                print("switched Units to imperial")
                self.execute("G20")

        self.params["current_tool"] = self.current_tool # int(Popen('halcmd getp iocontrol.0.tool-number',stdout=PIPE,shell=True).communicate()[0].strip())
        self.params["selected_tool"] = self.selected_tool
        self.params["current_pocket"] = self.current_pocket
        self.params["selected_pocket"] = self.selected_pocket

        # allow to restore the 3D-PROBE and TOOL-SETTER input to motionprobe-input
        # TODO most wanted is allow this sub to call a external file for easy user customisation
        tool_probe_manager_restore_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
        yield INTERP_EXECUTE_FINISH # without that the inhibit probe is not aknowledge before starting to move

        # allow to inhibit the 3D probe and to check tool setter status
        # TODO most wanted is allow this sub to call a external file for easy user customisation
        self.params["call_number"] = 1       # For differenciate probe check sub
        tool_probe_manager_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
        yield INTERP_EXECUTE_FINISH # without that the inhibit probe is not aknowledge before starting to move

        # Force absolute for G53 move
        self.execute("G90")
        # Z up first : #(commented out usage possible for 2.9)
#        if self.tool_change_quill_up:
        if self.params["_ini[EMCIO]TOOL_CHANGE_QUILL_UP"]:
            self.execute("G53 G0 Z{:.5f}".format(self.params["_ini[JOINT_2]HOME"]))
            wait(self)
        else:
            self.execute("G53 G0 Z{:.5f}".format(self.params["_ini[TOOL_CHANGE]Z_TRAVEL_POSITION"]))
            wait(self)

        self.execute("G53 G0 X{:.5f} Y{:.5f}".format(self.params["_ini[TOOL_CHANGE]X"],self.params["_ini[TOOL_CHANGE]Y"]))
        wait(self)
        self.execute("G53 G0 Z{:.5f}".format(self.params["_ini[TOOL_CHANGE]Z"]))
        wait(self)

        # allow to restore the 3D-PROBE and TOOL-SETTER input to motion.probe-input
        # TODO most wanted is allow this sub to call a external file for easy user customisation
        tool_probe_manager_restore_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
        yield INTERP_EXECUTE_FINISH # without that the inhibit probe is not aknowledge before starting to move

        # Now we check if M6T0 or same tool as actual or correct tool number
        clear_axis_all(self)

        if self.params["selected_tool"] == 0:
            if self.params["probe_number"] == int(Popen('halcmd getp iocontrol.0.tool-number',stdout=PIPE,shell=True).communicate()[0].strip()) and self.params["probe_number"] > 0:
                #if not self.params["_ini[TOOL_CHANGE]POPUP_STYLE"]:    # TODO
                self.execute("(DEBUG,PLEASE REMOVE THE 3D-PROBE #<current_tool> + NEED TO UNPAUSE OR ABORT)")
            else:
                #if not self.params["_ini[TOOL_CHANGE]POPUP_STYLE"]:    # TODO
                self.execute("(DEBUG,PLEASE REMOVE THE TOOL #<current_tool> + NEED TO UNPAUSE OR ABORT)")

            emccanon.PROGRAM_STOP()# Acted like a pause thanks a lot to c-morley
            yield INTERP_EXECUTE_FINISH # without that the inhibit probe is not aknowledge before starting to move

            clear_axis_all(self)
            tool_probe_restore_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
            tool_probe_changed_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
            yield INTERP_EXECUTE_FINISH
            yield INTERP_OK

        elif self.params["selected_tool"] == int(Popen('halcmd getp iocontrol.0.tool-number',stdout=PIPE,shell=True).communicate()[0].strip()):
              if self.params["probe_number"] == int(Popen('halcmd getp iocontrol.0.tool-number',stdout=PIPE,shell=True).communicate()[0].strip()) and self.params["probe_number"] > 0:
                  #if not self.params["_ini[TOOL_CHANGE]POPUP_STYLE"]:    # TODO
                  self.execute("(DEBUG,SAME 3D-PROBE #<selected_tool> AS ACTUAL #<current_tool> PLEASE CHECK + NEED TO UNPAUSE OR ABORT)")
              else:
                  #if not self.params["_ini[TOOL_CHANGE]POPUP_STYLE"]:    # TODO
                  self.execute("(DEBUG,SAME TOOL #<selected_tool> AS ACTUAL #<current_tool> PLEASE CHECK + NEED TO UNPAUSE OR ABORT)")
              emccanon.PROGRAM_STOP()
              yield INTERP_EXECUTE_FINISH # without that the inhibit probe is not aknowledge before starting to move
              clear_axis_all(self)

        elif self.params["selected_tool"] > 0:
              if self.params["selected_tool"] == self.params["probe_number"] and self.params["probe_number"] > 0:
                  #if not self.params["_ini[TOOL_CHANGE]POPUP_STYLE"]:    # TODO
                  self.execute("(DEBUG,PLEASE MOUNT AND CONNECT THE 3D-PROBE #<selected_tool> + NEED TO UNPAUSE OR ABORT)")
              else:
                  #if not self.params["_ini[TOOL_CHANGE]POPUP_STYLE"]:    # TODO
                  self.execute("(DEBUG,PLEASE CHANGE TO TOOL #<selected_tool> + NEED TO UNPAUSE OR ABORT)")
              emccanon.PROGRAM_STOP()
              yield INTERP_EXECUTE_FINISH # without that the inhibit probe is not aknowledge before starting to move
              clear_axis_all(self)

        else:
            clear_axis_all(self)
            tool_probe_restore_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
            self.set_errormsg("tool_probe_m6 remap error: UNKNOW ERROR OCCURED FOR TOOLCHANGE") # like a negative tool number
            yield INTERP_ERROR


        # bypass option for restoring simple manual mode without autolength
        if BYPASS_MEASURE:
            clear_axis_all(self)
            self.execute("(MSG,BYPASSED AUTO TOOL MEASUREMENT)")
            wait(self)

            # apply tool offset after succesfull toolchange without measure
            self.execute("G43")
            wait(self)                        #added 2022

            # RESTORE THE MACHINE XY LIMIT MAX USING JOINT 1 - TS_POS VALUE FOR ALLOW GOTO TOOLSENSOR
            self.execute("M%s P%s" % (self.params["change_x_limit_mcode"], (self.params["_ini[JOINT_0]MAX_LIMIT"] - self.params["_ini[TOOL_SETTER]TS_POS_X"])))
            self.execute("M%s P%s" % (self.params["change_y_limit_mcode"], (self.params["_ini[JOINT_1]MAX_LIMIT"] - self.params["_ini[TOOL_SETTER]TS_POS_Y"])))

            # unfortunatly i can't do here the REPLACE THE MACHINE Z LIMIT MIN ACCORDING TO TOOL LENGTH FOR PREVENT TABLE COLISION

            # Using act tool change as a sub allow user to cancel tool change correctly
            tool_probe_restore_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
            tool_probe_changed_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
            yield INTERP_EXECUTE_FINISH
            yield INTERP_OK


        # Using act tool change as a sub allow user to cancel tool change correctly
        tool_probe_changed_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
        yield INTERP_EXECUTE_FINISH

        try:

            # allow to inhibit the 3D probe and to check tool setter status
            # TODO most wanted is allow this sub to call a external file for easy user customisation
            self.params["call_number"] = 2       # For differenciate probe check sub
            tool_probe_manager_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
            yield INTERP_EXECUTE_FINISH # without that the inhibit probe is not aknowledge before starting to move

            # move to tool setter position (from INI)
            self.execute("G90")

            # REPLACE THE MACHINE XY LIMIT MAX  USING JOINT 1 VALUE FOR ALLOW GOTO TOOLSENSOR
            self.execute("M%s P%s" % (self.params["change_x_limit_mcode"], self.params["_ini[JOINT_0]MAX_LIMIT"]))
            self.execute("M%s P%s" % (self.params["change_y_limit_mcode"], self.params["_ini[JOINT_1]MAX_LIMIT"]))

            # Z up first
#            if self.tool_change_quill_up:
            if self.params["_ini[EMCIO]TOOL_CHANGE_QUILL_UP"]:
                self.execute("G53 G0 Z{:.5f}".format(self.params["_ini[JOINT_2]HOME"]))
                wait(self)
            else:
                self.execute("G53 G0 Z{:.5f}".format(self.params["_ini[TOOL_CHANGE]Z_TRAVEL_POSITION"]))
            wait(self)
            self.execute("G53 G0 X#<_ini[TOOL_SETTER]TS_POS_X> Y#<_ini[TOOL_SETTER]TS_POS_Y>")
            wait(self)



            #self.execute("G53 G0 Z#<_ini[TOOL_SETTER]TS_POS_Z>")
            self.execute("G53 G0 Z{:.5f}".format(self.params["_ini[TOOL_SETTER]TS_POS_Z"]))
# TODO
            #TS_POS_Z = [#<_psng_z_axis_length_abs>  - [[#<_psng_ts_height> + #<_psng_probe_max_z>] - #<_psng_latch>]]



            #wait(self)
            yield INTERP_EXECUTE_FINISH

            # set incremental mode
            self.execute("G91")

            # allow to inhibit the 3D probe and to check tool setter status
            # TODO most wanted is allow this sub to call a external file for easy user customisation
            self.params["call_number"] = 3       # For differenciate probe check sub
            tool_probe_manager_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
            yield INTERP_EXECUTE_FINISH # without that the inhibit probe is not aknowledge before starting to move

            # Fast Search probe   # Take care about possible error message move on line 0 exceed the Z positive axis limit can appears if tool setter is already triggered
            #self.execute("G38.3 Z-#<_ini[TOOL_SETTER]PROBE_MAX_Z> F#<_ini[TOOL_SETTER]VEL_FOR_SEARCH>")
            self.execute("G38.3 Z-{:.5f} F#<_ini[TOOL_SETTER]VEL_FOR_SEARCH>".format(self.params["_ini[TOOL_SETTER]TS_MAX_TOOL_LGT"] + self.params["_ini[TOOL_SETTER]CLEARANCE_Z"]))
            #print("Wait for probe ending")
            yield INTERP_EXECUTE_FINISH
            # Check if we have get contact or not
            tool_probe_result_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
            wait(self)

            if self.params["_ini[TOOL_SETTER]PROBE_MAX_LATCH"] > 0:
                self.execute("G38.5 Z#<_ini[TOOL_SETTER]PROBE_MAX_LATCH> F[#<_ini[TOOL_SETTER]VEL_FOR_SEARCH>*0.5]")
                # print("Latch probe wait end")
                yield INTERP_EXECUTE_FINISH
                # Check if we have get contact or not
                tool_probe_result_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
                wait(self)

            # Retract Latch
            self.execute("G1 Z#<_ini[TOOL_SETTER]LATCH> F[#<_ini[TOOL_SETTER]VEL_FOR_SEARCH>]")
            #This clear and yeld Mostly used for prevent correctly execution of call_number 4 before move is done
            clear_axis_all(self)
            yield INTERP_EXECUTE_FINISH

            # allow to inhibit the 3D probe and to check tool setter status
            # TODO most wanted is allow this sub to call a external file for easy user customisation
            self.params["call_number"] = 4       # For differenciate probe check sub
            tool_probe_manager_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
            yield INTERP_EXECUTE_FINISH # without that the inhibit probe is not aknowledge before starting to move

            # Final probe
            self.execute("G38.3 Z-[#<_ini[TOOL_SETTER]LATCH>*1.3] F#<_ini[TOOL_SETTER]VEL_FOR_PROBE>")
            #print("Wait for final probe ending")
            yield INTERP_EXECUTE_FINISH
            # Check if we have get contact or not
            tool_probe_result_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
            wait(self)

            # Save the probe result now due to possible use of G38.5 for retract
            proberesult = self.params[5063]

            if self.params["_ini[TOOL_SETTER]PROBE_MAX_LATCH"] > 0:
                self.execute("G38.5 Z#<_ini[TOOL_SETTER]PROBE_MAX_LATCH> F[#<_ini[TOOL_SETTER]VEL_FOR_SEARCH>*0.5]")
                #print("Final latch probe wait end")
                yield INTERP_EXECUTE_FINISH
                # Check if we have get contact or not
                tool_probe_result_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
                wait(self)

            # Retract Latch
            self.execute("G1 Z#<_ini[TOOL_SETTER]LATCH> F[#<_ini[TOOL_SETTER]VEL_FOR_SEARCH>]")
            #This clear and yeld Mostly used for prevent correctly execution of call_number 4 before move is done
            clear_axis_all(self)
            yield INTERP_EXECUTE_FINISH

            # Force absolute for G53 move
            self.execute("G90")

            # allow to inhibit the 3D probe and to check tool setter status
            # TODO most wanted is allow this sub to call a external file for easy user customisation
            self.params["call_number"] = 5       # For differenciate probe check sub
            tool_probe_manager_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
            yield INTERP_EXECUTE_FINISH # without that the inhibit probe is not aknowledge before starting to move

            # calculations for tool offset saved in the tooltable
            tool_offset_calculated = proberesult - self.params["ts_height"] + self.stat.g5x_offset[2]     # TODO Your welcome for other solution !    # TODO what about self.stat.g92_offset[2]
            self.execute("G10 L1 P#<selected_tool> Z{}".format(tool_offset_calculated))                   # REGISTER NEW TOOL LENGTH in the tooltable

            # apply tool offset after succesfull probing
            self.execute("G43")

            # Z up first before move to last pos or to change pos                                        ##### ADD QUIL UP HERE OR NOT ADD QUIL UP HERE IS A GOOD QUESTION
            self.execute("G53 G0 Z{:.5f}".format(self.params["_ini[TOOL_CHANGE]Z_TRAVEL_POSITION"]))
            wait(self)
            if self.params["_ini[TOOL_CHANGE]GO_BACK_LAST_POSITION"]:
                self.execute("G53 G0 X{:.5f} Y{:.5f}".format(initial_X,initial_Y))
                wait(self)
                ## imo better to not restore Z
                #self.execute("G53 G0 Z{:.5f}".format(initial_Z))
                #wait(self)
            else:
                self.execute("G53 G0 X{:.5f} Y{:.5f}".format(self.params["_ini[CHANGE_POSITION]X"],self.params["_ini[CHANGE_POSITION]Y"]))
                wait(self)
                ## imo better to not restore Z due to possible use of [CHANGE_POSITION]Z for some special user case
                #self.execute("G53 G0 Z{:.5f}".format(self.params["_ini[CHANGE_POSITION]Z"]))
                #wait(self)


            # Ended correctly so if we switched units for tool change - switch back and act ok to interpreter
            clear_axis_all(self)
            yield INTERP_EXECUTE_FINISH # without that the inhibit probe is not aknowledge before starting to move
            tool_probe_restore_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
            yield INTERP_OK

            # RESTORE THE MACHINE XY LIMIT MAX USING JOINT 1 - TS_POS VALUE FOR ALLOW GOTO TOOLSENSOR
            self.execute("M%s P%s" % (self.params["change_x_limit_mcode"], (self.params["_ini[JOINT_0]MAX_LIMIT"] - self.params["_ini[TOOL_SETTER]TS_POS_X"])))
            self.execute("M%s P%s" % (self.params["change_y_limit_mcode"], (self.params["_ini[JOINT_1]MAX_LIMIT"] - self.params["_ini[TOOL_SETTER]TS_POS_Y"])))


        except InterpreterException as e:
            clear_axis_all(self)
            tool_probe_restore_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
            msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
            print(msg)
            self.set_errormsg("tool_probe_m6 remap error: nothing restored or unknown state : %s" % (msg))
            yield INTERP_ERROR

    except Exception as e:
        clear_axis_all(self)
        tool_probe_restore_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
        print(e)
        self.set_errormsg("tool_probe_m6 remap error: nothing restored or unknown state : %s" % (e))
        yield INTERP_ERROR


# Using act tool change as a sub allow user to cancel tool change correctly
def tool_probe_changed_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG):
        #print("Acting tool change is ok")
        self.selected_pocket =  int(self.params["selected_pocket"])
        emccanon.CHANGE_TOOL(self.selected_pocket)
        self.current_pocket = self.selected_pocket
        self.selected_pocket = -1
        self.selected_tool = -1
        # cause a sync()
        self.set_tool_parameters()
        self.toolchange_flag = True
        clear_axis_all(self)

# Check if we have get contact or not
def tool_probe_result_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG):
            #print("Check contact found or not found")
            if self.params[5070] == 0 or self.return_value > 0.0:
                tool_probe_restore_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
                print("Probe contact not found")
                self.execute("(DEBUG,Probe contact not found)")
                emccanon.PROGRAM_STOP()
                wait(self)

# if we switched units for tool change - switch back
def tool_probe_restore_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG):
            #clear_axis_all(self)                                                                # Really unwanted here for manage different situation
            print("restore Units", ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
            if ABSOLUTE_FLAG:
                self.execute("G90")
            else:
                self.execute("G91")

            if BACKUP_METRIC_FLAG:
                self.execute("G21")
                print("switched Units back to metric")
            else:
                self.execute("G20")
                print("switched Units back to imperial")

            self.params["feed"] = FEED_BACKUP


            # RESTORE THE MACHINE XY LIMIT MAX USING JOINT 1 - TS_POS VALUE FOR ALLOW GOTO TOOLSENSOR
            self.execute("M%s P%f" % (self.params["change_x_limit_mcode"], (self.params["_ini[JOINT_0]MAX_LIMIT"] - self.params["_ini[TOOL_SETTER]TS_POS_X"])))
            self.execute("M%s P%f" % (self.params["change_y_limit_mcode"], (self.params["_ini[JOINT_1]MAX_LIMIT"] - self.params["_ini[TOOL_SETTER]TS_POS_Y"])))

            # allow to restore the 3D-PROBE and TOOL-SETTER input to motionprobe-input
            # TODO most wanted is allow this sub to call a external file for easy user customisation
            tool_probe_manager_restore_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG)
            print("tool length at restore ", self.stat.tool_offset)

def tool_probe_manager_restore_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG):
            if self.params["probe_number"] > 0:
                self.execute("M%s" % (self.params["probe_on_mcode"]))        # Custom Mcode do halcmd sets touch-probe-on-off 1    signal linked to and2.combined-probe.in1
                self.execute("M%s" % (self.params["tool_setter_on_mcode"]))  # Custom Mcode do halcmd sets touch-setter-on-off 1   signal linked to and2.combined-setter.in1
                print("RESTORE ALL PROBE INPUT STATES")
                #self.execute("(MSG,RESTORE ALL PROBE INPUT STATES)")
                wait(self)

# 3D Probe and Tool Setter management
def tool_probe_manager_sub(self, ABSOLUTE_FLAG, FEED_BACKUP, BACKUP_METRIC_FLAG):
            clear_axis_all(self)
            #print("ini tool number", self.params["probe_number"])
            #print("tool in spindle", int(Popen('halcmd getp iocontrol.0.tool-number',stdout=PIPE,shell=True).communicate()[0].strip()))
            #print("current tool", self.params["current_tool"])
            #print("selected tool number", self.params["selected_tool"])
            #print("call number", self.params["call_number"])

            if self.params["probe_number"] > 0:
                # Before goto change position
                if self.params["call_number"] == 1:
                    if Popen('halcmd getp motion.probe-input',stdout=PIPE,shell=True).communicate()[0].strip() == 'TRUE':
                        #if self.params["selected_tool"] == self.params["probe_number"] or self.params["probe_number"] == int(Popen('halcmd getp iocontrol.0.tool-number',stdout=PIPE,shell=True).communicate()[0].strip()):
                        if self.params["probe_number"] == int(Popen('halcmd getp iocontrol.0.tool-number',stdout=PIPE,shell=True).communicate()[0].strip()):
                            print("!!!! GOTO CHANGE POS 3D-PROBE/TOOL-SETTER TRIGGERED/MISSING : PLEASE CHECK BEFORE UNPAUSE OR CANCEL !!!!")
                            self.execute("(DEBUG,!!!! GOTO CHANGE 3D-PROBE/TOOL-SETTER TRIGGERED/MISSING : PLEASE CHECK BEFORE UNPAUSE OR CANCEL !!!!)")
                            emccanon.PROGRAM_STOP()
                            wait(self)
                        else:
                            self.execute("M%s" % (self.params["probe_off_mcode"]))     # Custom Mcode do halcmd sets touch-probe-on-off 0    signal linked to and2.combined-probe.in1
                            print("!!! GOTO CHANGE POS UNUSED 3D-PROBE INHIBITED DUE TO TRIGGERED OR UNCONNECTED STATUS !!!!")
                            self.execute("(DEBUG,!!!! GOTO CHANGE POS UNUSED 3D-PROBE INHIBITED DUE TO TRIGGERED OR UNCONNECTED STATUS !!!!)")
                    else:
                        print("GOTO CHANGE POS WITH 3D-PROBE STATUS OK OR INHIBITED")
                        self.execute("(DEBUG,GOTO CHANGE POS WITH 3D-PROBE STATUS OK OR INHIBITED)")

                # Before goto tool_setter position
                if self.params["call_number"] == 2:
                    if Popen('halcmd getp motion.probe-input',stdout=PIPE,shell=True).communicate()[0].strip() == 'TRUE':
                        if self.params["probe_number"] == int(Popen('halcmd getp iocontrol.0.tool-number',stdout=PIPE,shell=True).communicate()[0].strip()):
                            print("!!!! TRAVEL MOVE 3D-PROBE IN SPINDLE TRIGGERED/MISSING : PLEASE CHECK BEFORE UNPAUSE OR CANCEL !!!!")
                            self.execute("(DEBUG,!!!! TRAVEL MOVE 3D-PROBE IN SPINDLE TRIGGERED/MISSING : PLEASE CHECK BEFORE UNPAUSE OR CANCEL !!!!)")
                            emccanon.PROGRAM_STOP()
                            wait(self)
                        else:
                            self.execute("M%s" % (self.params["probe_off_mcode"]))     # Custom Mcode do halcmd sets touch-probe-on-off 0    signal linked to and2.combined-probe.in1
                            print("!!! TRAVEL MOVE FOR TOOL WITH 3D-PROBE INHIBITED !!!!")
                            self.execute("(DEBUG,!!!! TRAVEL MOVE FOR TOOL WITH 3D-PROBE INHIBITED !!!!)")
                    elif self.params["probe_number"] == int(Popen('halcmd getp iocontrol.0.tool-number',stdout=PIPE,shell=True).communicate()[0].strip()):
                          print("TRAVEL MOVE 3D-PROBE IN SPINDLE FORCE ACTIVATION")
                          self.execute("(DEBUG,TRAVEL MOVE 3D-PROBE IN SPINDLE FORCE ACTIVATION)")
                    else:
                        print("TRAVEL MOVE FOR TOOL WITH 3D-PROBE STATUS OK OR INHIBITED")
                        self.execute("(DEBUG,TRAVEL MOVE FOR TOOL WITH 3D-PROBE STATUS OK OR INHIBITED)")

                # Before first probe
                if self.params["call_number"] == 3:
                    if Popen('halcmd getp motion.probe-input',stdout=PIPE,shell=True).communicate()[0].strip() == 'TRUE':
                        if self.params["probe_number"] == int(Popen('halcmd getp iocontrol.0.tool-number',stdout=PIPE,shell=True).communicate()[0].strip()):
                            print("!!!! PROBE MOVE 3D-PROBE IN SPINDLE TRIGGERED/MISSING : PLEASE CHECK BEFORE UNPAUSE OR CANCEL !!!!")
                            self.execute("(DEBUG,!!!! PROBE MOVE 3D-PROBE IN SPINDLE TRIGGERED/MISSING : PLEASE CHECK BEFORE UNPAUSE OR CANCEL !!!!)")
                            emccanon.PROGRAM_STOP()
                            wait(self)
                    else:
                        print("PROBE MOVE FOR TOOL WITH 3D-PROBE STATUS OK OR INHIBITED")
                        self.execute("(DEBUG,PROBE MOVE FOR TOOL WITH 3D-PROBE STATUS OK OR INHIBITED)")

                # Before final probe
                if self.params["call_number"] == 4:
                    if Popen('halcmd getp motion.probe-input',stdout=PIPE,shell=True).communicate()[0].strip() == 'TRUE':
                        if self.params["probe_number"] == int(Popen('halcmd getp iocontrol.0.tool-number',stdout=PIPE,shell=True).communicate()[0].strip()):
                            print("!!!! FINAL PROBE MOVE 3D-PROBE IN SPINDLE TRIGGERED/MISSING : PLEASE CHECK BEFORE UNPAUSE OR CANCEL !!!!")
                            self.execute("(DEBUG,!!!! FINAL PROBE MOVE 3D-PROBE IN SPINDLE TRIGGERED/MISSING : PLEASE CHECK BEFORE UNPAUSE OR CANCEL !!!!)")
                            emccanon.PROGRAM_STOP()
                            wait(self)
                    else:
                        print("FINAL PROBE MOVE FOR TOOL WITH 3D-PROBE STATUS OK OR INHIBITED")
                        self.execute("(DEBUG,FINAL PROBE MOVE FOR TOOL WITH 3D-PROBE STATUS OK OR INHIBITED)")

                # Before last travel
                if self.params["call_number"] == 5:
                    if Popen('halcmd getp motion.probe-input',stdout=PIPE,shell=True).communicate()[0].strip() == 'TRUE':
                        if self.params["probe_number"] == int(Popen('halcmd getp iocontrol.0.tool-number',stdout=PIPE,shell=True).communicate()[0].strip()):
                            print("!!!! LAST TRAVEL MOVE 3D-PROBE IN SPINDLE TRIGGERED/MISSING : PLEASE CHECK BEFORE UNPAUSE OR CANCEL !!!!")
                            self.execute("(DEBUG,!!!! LAST TRAVEL MOVE 3D-PROBE IN SPINDLE TRIGGERED/MISSING : PLEASE CHECK BEFORE UNPAUSE OR CANCEL !!!!)")
                            emccanon.PROGRAM_STOP()
                            wait(self)
                    else:
                        print("LAST TRAVEL MOVE FOR TOOL WITH 3D-PROBE STATUS OK OR INHIBITED")
                        self.execute("(DEBUG,LAST TRAVEL MOVE FOR TOOL WITH 3D-PROBE STATUS OK OR INHIBITED)")


            # If probe is not configured check setter only
            elif Popen('halcmd getp motion.probe-input',stdout=PIPE,shell=True).communicate()[0].strip() == 'TRUE':
                clear_axis_all(self)
                print("!!!! SETTER TRIGGERED/MISSING BEFORE TRAVEL/LATCH/PROBE MOVE : PLEASE CHECK BEFORE UNPAUSE OR CANCEL !!!!")
                self.execute("(DEBUG,SETTER TRIGGERED/MISSING BEFORE TRAVEL/LATCH/PROBE MOVE : PLEASE CHECK BEFORE UNPAUSE OR CANCEL)")
                emccanon.PROGRAM_STOP()
                wait(self)

def wait(self):
     self.stat.poll()
     while self.stat.interp_state == linuxcnc.INTERP_IDLE:
        #print("interpret out from wait")
        return

def clear_axis_all(self):
    self.execute("M%s" % (self.params["clear_gui_notif_mcode"]))     # Custom Mcode doing and clearing halcmd setp axisui.notifications-clear-error 1


