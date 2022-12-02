# PSNG master is for LinuxCNC 2.9/2.10
# PSNG 2.8 is for LinuxCNC 2.8

## Important things needed :

- This version require to have the machine table configured as G54 Z0 after M6 Tx G43 

- You also need to have really correctly configured min max for each axis in your ini file

- Probe need to be in the tool table with correct config in your ini file

- All Z start probing position are automatically calculated using axis length, block_heigth, table_offset, tool_offset, from machine table 0

- You need to place manually the Touch device on the wanted Z height for all XY probing

- The x_max y_max axis limit is changed automatically using your tool_setter XY position for take it in a safe area

- The z_min axis is changed automatically using tool length from tooltable for prevent colision with machine table


-TODO : when you une some function using self.ocode() the DRO is not updated

-TODO : if you change two value putpref save only the last value

-TODO : add 2 cycle for probing probe_rect_boss.ngc probe_rect_pocket.ngc like probe_basic

-TODO : prevent multiple click on the gui when something is already started self.work_in_progress do not work for now (something like that is done for compensation)


## Exemple positioning your tool setter in a Y protected area

[AXIS_Y]
- -13 for HOME_OFFSET distance from limit switch after homing
- 1 mm for limit switch clearence
- 12 mm for protected area tool_setter
- USING A TOOL_SENSOR OUTSIDE OF MACHINE AXIS AREA NEED TO EXTEND THE LIMIT AT M6
- user defeined Mcode M170/M171 REPLACE THE MACHINE Y LIMIT MAX  USING JOINT 1 VALUE

MIN_LIMIT = -332.11

MAX_LIMIT = 0.11



[JOINT_1]

AXIS = Y

MIN_LIMIT = -332.11

MAX_LIMIT = 12.11

HOME = 0

HOME_OFFSET = 13



[TOOL_SETTER]
- Absolute XYZ G53 machine coordinates for start auto tool measurement

TS_POS_X = 0

TS_POS_Y = 12



## Info

Probe-Screen is currently being redesigned any help are really welcome.

Added in this release :

-Possibility to swap from 3D touch probe to Touchplate with a simple tickbox.

-Manual tool change with auto length do not use anymore python stglue remap.

-You can bypass the auto length stuff with a simple tickbox.

-Config is done for use separate input for Touch Probe (or Touchplate) and Tool setter and the status is checked before each move.


## History

This repo was originally a fork of <https://github.com/verser-git/probe_screen_v2> by Serguei Glavatski / Vers.by. Hopefully, this will become a community maintained probe screen for LinuxCNC. Anyone with an interest in helping out, please submit PRs or ask to join the project via a GitHub issue.

## Install

1. See "psng/install_add_to_your.hal"# 
    You need to add this in your .hal files :

```sh
#******************************************
# MANUAL TOOLCHANGE with remap m6 probe using stdglue as standalone
#******************************************
net manual-tool-change-loop    iocontrol.0.tool-change      => iocontrol.0.tool-changed
net manual-tool-prep-loop      iocontrol.0.tool-prepare     => iocontrol.0.tool-prepared
net manual-tool-number         iocontrol.0.tool-number
net manual-tool-diameter                                    <= halui.tool.diameter
#******************************************
```

2. See "psng/install_add_to_your.ini" Add to your .ini settings, substitute your own constants.

3. The following folders from the archive are placed in configuration folder:

   ```sh
   /python
   /nc_subroutines
   /nc_subroutines/psng
   /nc_subroutines/remap
   ```

## Use

Set the probe in the spindle.

Move manually probe for Z about 2-10 mm above the workpiece surface,

Move manually probe fo XY to the position indicated by the colored dot on the appropriate button Probe Screen.

Fill parameters. Meaning of the parameters should be clear from the names and pictures (the name pop up when approaching the mouse). If you change the parameters are automatically saved in .pref .

Hit **only** the button that corresponds to the position of the probe above the workpiece. For the other buttons - you **must** move the probe to another position above the workpiece.

You do not need to expose offsets for tool "Probe", the program desired zero offsets for the current tool makes herself, and G-code works off all in relative coordinates.
In fact, you can use the application immediately after the Home.

Any of the search ends at XY moving at the desired point (or edge, or corner, or center), Z finish up using clearance value.

More info <https://vers.by/en/blog/useful-articles/probe-screen>
Discussion on the forum linuxcnc.org: <https://forum.linuxcnc.org/49-basic-configuration/29187-work-with-probe>

## License

   This is a plugin for LinuxCNC
   Copyright (c) 2015 Serguei Glavatski ( verser  from cnc-club.ru )
   Copyright (c) 2020 Probe Screen NG Developers
   Copyright (c) 2022 Alkabal

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
