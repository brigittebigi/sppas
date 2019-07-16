------------------------------------------------------------------------------

program:    classphones
author:     Brigitte Bigi
contact:    develop@sppas.org
date:       2019-07-16
version:    2.2
copyright:  Copyright (C) 2017-2019 Brigitte Bigi
license:    GNU Public License version 3 or any later version
brief:      SPPAS plugin to create tiers with the classification of phonemes.

This plugin allows to create annotations of the classification of phonemes:
place of articulation, manner of articulation, phonation, etc.
The classification is saved in a new file. Here is the list of tiers that
will be created:
 - Class: whether the phoneme is a vowel or a consonant
 - Height: open, open-mid, close, etc. of vowels
 - Backness: front, back, etc. of vowels
 - Roundness: whether the vowel is rounded or unrounded
 - Manner of articulation: in which way the sound is produced
 - Place of articulation:  where the major constriction happens inside the
   vocal tract
 - Phonation: whether the phoneme is voiced or unvoiced
 - Location: whether the consonant is oral or nasal
 - Position: central, front, back, etc. of a consonant
 - Airstream: whether the consonant is pulmonic or non-pulmonic

Requires a SPPAS alignment file, i.e. a file including a tier with name
"PhonAlign" based on the SAMPA phonemes encoding.

Any help to improve the quality of the classification file is welcome!
The classification file (phonemes.csv) is available in the plugin directory
and can be opened with any spreadsheet software.

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
