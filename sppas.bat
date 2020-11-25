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

WHERE pythonw3.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 (

    start "" pythonw3.exe -m sppas
    exit

) else (

    WHERE python3.exe >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        color 1E
        start "" python3.exe -m sppas
        exit
    ) else (

        color 04

        if exist C:\Python27\pythonw.exe (
            start "" C:\Python27\pythonw.exe .\sppas\bin\sppasgui.py
            exit
        ) else (
            if exist C:\Python27\python.exe (
                start "" C:\Python27\python.exe .\sppas\bin\sppasgui.py
                exit
            ) else (

                REM Perhaps python3 was installed with name "python"
                WHERE python.exe >nul 2>nul
                if %ERRORLEVEL% EQU 0 (
                    python.exe .\sppas\bin\checkpy.py
                    if %ERRORLEVEL% EQU 0 (
                        start "" python.exe -m sppas
                        exit
                    ) else (
                        start "" python.exe .\sppas\bin\sppasgui.py
                        exit
                    )

                ) else (
                        color 4E
                        echo Python is not an internal command of your operating system.
                        echo Install it first with the Windows Store or from http://www.python.org.
                )
            )
        )
    )
)

