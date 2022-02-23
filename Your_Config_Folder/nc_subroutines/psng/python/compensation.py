#!/usr/bin/env python2
"""Copyright (C) 2020 Scott Alford, scottalford75@gmail.com
Copyright (C) 2022 Alkabal for PSNG_V3

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU 2 General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

UPDATE_INTERVAL = 0.01 # this is how often the z external offset value is updated based on current x & y position

import sys
import os.path, time
import numpy as np
import hal, time
from scipy.interpolate import griddata
from enum import Enum, unique

import linuxcnc

@unique
class States(Enum):
    start = 1
    IDLE = 2
    LOADMAP = 3
    RUNNING = 4
    RESET = 5
    STOP = 6


class Compensation :
  def __init__(self) :
    self.comp = {}


    # make the pins hal
    self.halcomp = hal.component("probe.compensation")
    self.halcomp.newpin("fade-height", hal.HAL_FLOAT, hal.HAL_IN)
    self.halcomp.newpin("enable-in", hal.HAL_BIT, hal.HAL_IN)
    self.halcomp.newpin("enable-out", hal.HAL_BIT, hal.HAL_OUT)
    self.halcomp.newpin("scale-out", hal.HAL_FLOAT, hal.HAL_OUT)
    self.halcomp.newpin("counts-out", hal.HAL_S32, hal.HAL_OUT)
    self.halcomp.newpin("clear-out", hal.HAL_BIT, hal.HAL_OUT)
    self.halcomp.newpin("x-pos-cmd-in", hal.HAL_FLOAT, hal.HAL_IN)
    self.halcomp.newpin("y-pos-cmd-in", hal.HAL_FLOAT, hal.HAL_IN)
    self.halcomp.newpin("z-pos-cmd-in", hal.HAL_FLOAT, hal.HAL_IN)
    self.halcomp.newpin("z-axis-max", hal.HAL_FLOAT, hal.HAL_OUT)
    self.halcomp.newpin("z-axis-min", hal.HAL_FLOAT, hal.HAL_OUT)
    self.halcomp.newpin("z-eoffset", hal.HAL_FLOAT, hal.HAL_OUT)
    self.halcomp.newpin("z-eoffset-out-of-limit", hal.HAL_BIT, hal.HAL_OUT)
    self.halcomp.newpin("x-grid-start", hal.HAL_FLOAT, hal.HAL_OUT)
    self.halcomp.newpin("y-grid-start", hal.HAL_FLOAT, hal.HAL_OUT)
    self.halcomp.newpin("x-grid-end", hal.HAL_FLOAT, hal.HAL_OUT)
    self.halcomp.newpin("y-grid-end", hal.HAL_FLOAT, hal.HAL_OUT)
    self.halcomp.newpin("z-grid-min", hal.HAL_FLOAT, hal.HAL_OUT)
    self.halcomp.newpin("z-grid-max", hal.HAL_FLOAT, hal.HAL_OUT)
    self.halcomp.newpin("joint-0-is-homed", hal.HAL_BIT, hal.HAL_IN)
    self.halcomp.newpin("joint-1-is-homed", hal.HAL_BIT, hal.HAL_IN)
    self.halcomp.newpin("joint-2-is-homed", hal.HAL_BIT, hal.HAL_IN)
    self.halcomp.newpin("grid_precision", hal.HAL_FLOAT, hal.HAL_OUT)
    self.halcomp.newpin("latch-bed-compensation-in", hal.HAL_FLOAT, hal.HAL_IN)
    self.halcomp.ready()

    self.stat = linuxcnc.stat()


    # load value regarding to ini file
    self.inifile = linuxcnc.ini(os.environ["INI_FILE_NAME"])

    calc_method = self.inifile.find("TOUCH_DEVICE", "METHOD")
    file_name   = self.inifile.find("TOUCH_DEVICE", "FILE_NAME")
    scale_ini   = self.inifile.find("TOUCH_DEVICE", "COUNTS_SCALE")
    z_axis_max  =  self.inifile.find("AXIS_Z", "MAX_LIMIT")
    z_axis_min  =  self.inifile.find("AXIS_Z", "MIN_LIMIT")
    grid_precision  =  self.inifile.find("TOUCH_DEVICE", "GRID_PRECISION")

    if (
        calc_method is None
        or file_name is None
        or scale_ini is None
        or z_axis_max is None
        or z_axis_min is None
        or grid_precision is None
       ):# default to cubic if not specified
       self.method   = "cubic"
       self.filename = "probe-compensation-grid-results.txt"
       self.halcomp["scale-out"] = 0
       self.halcomp["z-axis-max"] = 0
       self.halcomp["z-axis-min"] = 0
       self.halcomp["grid_precision"] = 0
       if self.halcomp["scale-out"] == 0 :
           print " NOT FOUND INI SCALE : COMPENSATION INHIBITED ! "
       if self.halcomp["z-axis-max"] == 0 :
           print " NOT FOUND HAL AXIS Z MAX : COMPENSATION INHIBITED ! "
       if self.halcomp["z-axis-min"] == 0 :
           print " NOT FOUND HAL AXIS Z MIN : COMPENSATION INHIBITED ! "
       if self.halcomp["grid_precision"] == 0 :
           print " NOT FOUND INI GRID_PRECISION : COMPENSATION INHIBITED ! "
       SystemExit
    else:
        self.method = calc_method
        self.filename = file_name
        self.halcomp["scale-out"] = scale_ini
        self.halcomp["z-axis-max"] = z_axis_max
        self.halcomp["z-axis-min"] = z_axis_min
        self.halcomp["grid_precision"] = grid_precision


  def loadMap(self) :
    # data coordinates and values rounded to centieme .xx for xy and Z to micron .xxx
    self.data = np.loadtxt(self.filename, dtype=float, delimiter=" ", usecols=(0, 1, 2))
    self.X_data = np.around(self.data[:,0],2)
    self.Y_data = np.around(self.data[:,1],2)
    self.Z_data = np.around(self.data[:,2],3)

    # get the x and y, min and max values from the data
    self.X_start = np.min(self.X_data)
    self.Y_start = np.max(self.Y_data)
    self.X_end = np.max(self.X_data)
    self.Y_end = np.min(self.Y_data)
    self.Z_max = np.max(self.Z_data)
    self.Z_min = np.min(self.Z_data)

    # target grid to interpolate 1 centieme/gridd
    self.X_steps = int((abs(self.X_start-self.X_end)+1) / self.halcomp["grid_precision"])
    self.Y_steps = int((abs(self.Y_end-self.Y_start)+1) / self.halcomp["grid_precision"])
    self.X = np.round(np.linspace(self.X_start, self.X_end, self.X_steps), 2)
    self.Y = np.round(np.linspace(self.Y_start, self.Y_end, self.Y_steps), 2)

    self.Xi,self.Yi = np.meshgrid(self.X,self.Y)

    # interpolate, Z has all the offset values but need to be transposed to Zi rounded to micron
    self.Z = np.round(griddata((self.X_data,self.Y_data),self.Z_data,(self.Xi,self.Yi),method=self.method,fill_value=0.0), 3)
    self.Zi = np.transpose(self.Z)

    # update hal value and print value to terminal
    print " X_start = ", self.X_start
    print " Y_start = ", self.Y_start
    print " X_end = ", self.X_end
    print " Y_end = ", self.Y_end
    print " Z_min = ", self.Z_min
    print " Z_max = ", self.Z_max
    print " x_data = ", self.X_data
    print " y_data = ", self.Y_data
    print " Z_data = ", self.Z_data
    print " x_step = ", self.X_steps
    print " y_step = ", self.Y_steps
    print " X = ", self.X
    print " Y = ", self.Y
    print " Xi = ", self.Xi
    print " Yi = ", self.Yi
    print " Z = ", self.Z
    print " Zi = ", self.Zi


    self.halcomp["x-grid-start"] = self.X_start
    self.halcomp["x-grid-end"]   = self.X_end
    self.halcomp["y-grid-start"] = self.Y_start
    self.halcomp["y-grid-end"]  = self.Y_end
    self.halcomp["z-grid-min"] = self.Z_min
    self.halcomp["z-grid-max"] = self.Z_max



  def compensate(self) :
    # get our nearest integer position we rounf the value according to calculated step 1 centieme/gridd
    self.X_pos = round(self.halcomp['x-pos-cmd-in'], 2)
    self.Y_pos = round(self.halcomp['y-pos-cmd-in'], 2)

    # clamp the range : if actual position is outside of the grid area we do not want any offset
    if ((self.halcomp['x-pos-cmd-in'] > self.X_start and self.halcomp['x-pos-cmd-in'] < self.X_end) and (self.halcomp['y-pos-cmd-in'] < self.Y_start and self.halcomp['y-pos-cmd-in'] > self.Y_end)) :
        # load the corresponding xy position in the array
        self.Xn = int((self.X_pos - self.X_start) / self.halcomp["grid_precision"])
        self.Yn = int((self.Y_pos - self.Y_end) / self.halcomp["grid_precision"])

        # load calculated Z offset using meshgrid from xy position in the array 1 centieme/gridd
        self.halcomp["z-eoffset"] = self.Zi[self.Xn,self.Yn]
    else:
        # location is outside of the offset map array : max Z value as offset for prevent any contact outside of probed area
        if self.Z_max > 0 :
            self.halcomp["z-eoffset"] = self.halcomp["latch-bed-compensation-in"] + self.Z_max
        else :
            self.halcomp["z-eoffset"] = self.halcomp["latch-bed-compensation-in"]

    # check if offseted position is outside of axis Z range we do not send eoffset  (with 1mm clearence for allow time to the axis for move without error)
    if ((self.halcomp['z-pos-cmd-in'] + self.halcomp["z-eoffset"]) >= self.halcomp["z-axis-max"] - 1):
        compensation = 0
        if (self.halcomp["z-eoffset-out-of-limit"] == 0) :
            print " COMPENSATION SET TEMPORARY TO 0 DUE TO AXIS MAX LIMIT PROXIMITY ! "
            self.halcomp["z-eoffset-out-of-limit"] = 1
    elif ((self.halcomp['z-pos-cmd-in'] - self.halcomp["z-eoffset"]) <= self.halcomp["z-axis-min"] + 1):
        compensation = 0
        if (self.halcomp["z-eoffset-out-of-limit"] == 0) :
            print " COMPENSATION SET TEMPORARY TO 0 DUE TO AXIS MIN LIMIT PROXIMITY ! "
            self.halcomp["z-eoffset-out-of-limit"] = 1
    else :
        # get the nearest compensation offset and convert to counts (s32) with a scale (float)
        compensation = int(self.halcomp["z-eoffset"] / self.halcomp["scale-out"])
        if (self.halcomp["z-eoffset-out-of-limit"] == 1) :
            print " COMPENSATION RESTORED AFTER AXIS LIMIT PROXIMITY ! "
            self.halcomp["z-eoffset-out-of-limit"] = 0


    # use optional fade-height
    if self.halcomp["fade-height"] == 0 :
        compScale = 1
    elif self.halcomp["z-pos-cmd-in"] < self.halcomp["fade-height"]:
        compScale = (self.halcomp["fade-height"] - self.halcomp["z-pos-cmd-in"])/self.halcomp["fade-height"]
        if compScale > 1 :
            compScale = 1
    else :
        compScale = 0


    # finally we set the counts value and return the value to the loop
    counts = compensation * compScale
    return counts


  # loop with different status
  def run(self) :

    currentState = States.start
    prevState = States.STOP

    try:
      while True:
        time.sleep(UPDATE_INTERVAL)

        # get linuxcnc task_state status for machine on / off transitions
        self.stat.poll()

        if currentState == States.start :
          if currentState != prevState :
            print("\nCompensation entering start state")
            prevState = currentState

          # do start-up tasks
          print(" %s last modified: %s" % (self.filename, time.ctime(os.path.getmtime(self.filename))))

          # preload map at start
          self.loadMap()
          print(" Compensation map loaded at start")
          prevMapTime = os.path.getmtime(self.filename)
          #prevMapTime = 0
          self.halcomp["counts-out"] = 0

          # transition to IDLE state
          currentState = States.IDLE

        elif currentState == States.IDLE :
          if currentState != prevState :
            print("\nCompensation entering IDLE state")
            prevState = currentState

          # stay in IDLE state until compensation is enabled
          if self.halcomp["enable-in"] and self.halcomp["joint-0-is-homed"] and self.halcomp["joint-1-is-homed"] and self.halcomp["joint-2-is-homed"] :
            currentState = States.LOADMAP

        elif currentState == States.LOADMAP :
          if currentState != prevState :
            print("\nCompensation entering LOADMAP state")
            prevState = currentState

          mapTime = os.path.getmtime(self.filename)

          if mapTime != prevMapTime:
            self.loadMap()
            print(" Compensation map reloaded")
            prevMapTime = mapTime

          # transition to RUNNING state
          currentState = States.RUNNING

        elif currentState == States.RUNNING :
          if currentState != prevState :
            print("\nCompensation entering RUNNING state")
            prevState = currentState

          if self.halcomp["enable-in"] and self.halcomp["joint-0-is-homed"] and self.halcomp["joint-1-is-homed"] and self.halcomp["joint-2-is-homed"] :
            # enable external offsets
            self.halcomp["enable-out"] = 1

            if self.stat.task_state == linuxcnc.STATE_ON :
              # get the compensation if machine power is on, else set to 0
              # otherwise we loose compensation eoffset if machine power is cycled
              # when compensation is enable
              self.halcomp["counts-out"] = self.compensate()
            else :
              self.halcomp["counts-out"] = 0

          else :
            # transition to RESET state
            self.halcomp["counts-out"] = 0
            # wait until the axis is in position before stopping eoffsets
            #while self.halcomp["z-pos-cmd-in"] = ???
            #   time.sleep(0.1)
            time.sleep(1)
            currentState = States.RESET

        elif currentState == States.RESET :
          if currentState != prevState :
            print("\nCompensation entering RESET state")
            prevState = currentState

          # paranoid reset the eoffsets counts register so we don't accumulate
          self.halcomp["counts-out"] = 0

          # toggle the clear output
          self.halcomp["clear-out"] = 1;
          time.sleep(0.1)
          self.halcomp["clear-out"] = 0;

          # disable external offsets
          self.halcomp["enable-out"] = 0

          # transition to IDLE state
          currentState = States.IDLE

    except KeyboardInterrupt:
        raise SystemExit

comp = Compensation()
comp.run()
