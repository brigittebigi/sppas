------------------------------------------------------------------------------
program:    audioconc
author:     Christian chanard
contact:    develop@sppas.org
date:       2019-03-18
version:    1.0
copyright:  Copyright (C) 2018 Brigitte Bigi
license:    GNU Public License version 3 or any later version
brief:      SPPAS plugin for AudioWordConcatener.

Word Concatener is a tool to concatenate into a new audio file, the audio chunks
corresponding to the occurrences of a word or sequence in an audio file.
Bounds of the tracks are indicated in an annotated file of any format supported by
SPPAS (xra, TextGrid, eaf, ...).
An offset can be chosen to add a few milliseconds to the left and right of the sound corresponding
to the searched word or sequence.
An extra blank can be added to separate the chunks
An SPPAS annotation file is also created that helps to localize each occurrences

------------------------------------------------------------------------------
#
# this program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# this program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
------------------------------------------------------------------------------
