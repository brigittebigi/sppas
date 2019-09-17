------------------------------------------------------------------------------

program:    statsgroups
author:     Brigitte Bigi
contact:    contact@sppas.org
date:       2019-09-16
version:    1.0
copyright:  Copyright (C) 2019  Brigitte Bigi
license:    GNU Public License version 3 or any later version
brief:      SPPAS plugin to estimate stats on series of intervals

This plugin estimates statistics (occ, mean, stdev, intercep and
slope) on sequences of numerical intervals.

By default, only the tier with the numerical values is needed: the time
segments are automatically created when the numerical intervals are
separated by holes or by intervals with an empty label.
Optionally, another tier with the time segments can be given.

------------------------------------------------------------------------------

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

------------------------------------------------------------------------------
