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

import linuxcnc  # to get our own error system

from .settings import ProbeScreenSettings
from .jog import ProbeScreenJog
from .zero import ProbeScreenZero
from .rotation import ProbeScreenRotation
from .tool_measurement import ProbeScreenToolMeasurement
from .workpiece_measurement import ProbeScreenWorkpieceMeasurement
from .length_measurement import ProbeScreenLengthMeasurement


def get_handlers(halcomp, builder, useropts):
    return [
        ProbeScreenSettings(halcomp, builder, useropts),
        ProbeScreenJog(halcomp, builder, useropts),
        ProbeScreenZero(halcomp, builder, useropts),
        ProbeScreenRotation(halcomp, builder, useropts),
        ProbeScreenToolMeasurement(halcomp, builder, useropts),
        ProbeScreenWorkpieceMeasurement(halcomp, builder, useropts),
        ProbeScreenLengthMeasurement(halcomp, builder, useropts),
    ]
