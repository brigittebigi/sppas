------------------------------------------------------------------------------

program:    sampa2ipa
author:     Brigitte Bigi
contact:    develop@sppas.org
date:       2019-07-22
version:    2.2
copyright:  Copyright (C) 2017-2019  Brigitte Bigi
license:    GNU Public License version 3 or any later version
brief:      SPPAS plugin to convert SAMPA into IPA phonemes encoding.

This plugin allows to convert transcriptions between the SAMPA (Speech
Assessment Methods Phonetic Alphabet) annotation and the International
Phonetic Alphabet.

It can convert either individual time-aligned phonemes or time-aligned
strings of phonemes like syllables. The converted transcription is saved
in a new file. Any symbol in the transcription tier which is not in the
conversion file is not replaced.

In case of TextGrid files, it converts into the Praat version of the IPA.

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
