# Probe Screen for LinuxCNC 2.8/2.9

## Info

Probe-Screen is currently being redesigned any help are welcome.

Added in this release :

-Possibility to swap from 3D touch probe to Touchplate with a simple tickbox.

-Manual tool change with auto length use now built in python stglue remap.

-You can bypass the auto length stuff with a simple tickbox.


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
   /psng
   /remap
   /nc_subroutines
   ```

## Use

Set the probe in the spindle.

Move manually probe for Z about 2-10 mm above the workpiece surface,
and for XY about the position indicated by the colored dot on the appropriate button Probe Screen.

Fill parameters. Meaning of the parameters should be clear from the names and pictures (the name pop up when approaching the mouse). If you change the parameters are automatically saved in .pref .

Hit **only** the button that corresponds to the position of the probe above the workpiece. For the other buttons - you **must** move the probe to another position above the workpiece.

You do not need to expose offsets for tool "Probe", the program desired zero offsets for the current tool makes herself, and G-code works off all in relative coordinates.
In fact, you can use the application immediately after the Home.

Any of the search ends at XY moving at the desired point (or edge, or corner, or center), Z remains in the original position.

More info <https://vers.by/en/blog/useful-articles/probe-screen>
Discussion on the forum linuxcnc.org: <https://forum.linuxcnc.org/49-basic-configuration/29187-work-with-probe>

## License

   This is a plugin for LinuxCNC
   Copyright 2015 Serguei Glavatski <info@vers.by>

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
