GOTO EndHeader
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    sppas.bat
    ~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi
    :summary:      SPPAS for Windows.

"""
:EndHeader

@echo off

SET PYTHONIOENCODING=UTF-8

if exist pythonw3.exe (

        start "" pythonw3.exe .\sppas\bin\sppasgui.py

) else (

    if exist python3.exe (
        start "" python3.exe .\sppas\bin\sppasgui.py

    ) else (

        if exist C:\Python27\pythonw.exe (
            start "" C:\Python27\pythonw.exe .\sppas\bin\sppasgui.py
        ) else (
            if exist C:\Python27\python.exe (
                start "" C:\Python27\python.exe .\sppas\bin\sppasgui.py
            ) else (
                start "" python.exe .\sppas\bin\sppasgui.py
            )
        )
    )
)

exit
