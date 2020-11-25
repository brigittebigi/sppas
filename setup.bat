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

    setup.bat
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
color 0F
SET PYTHONIOENCODING=UTF-8

REM Make sure we have admin right
set "params=%*"
cd /d "%~dp0" && ( if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs" ) && fsutil dirty query %systemdrive% 1>nul 2>nul || (  echo Set UAC = CreateObject^("Shell.Application"^) : UAC.ShellExecute "cmd.exe", "/k cd ""%~sdp0"" && %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs" && "%temp%\getadmin.vbs" && exit /B )

REM Search for pythonw3 command, ie Python3 & WxPython are both installed
WHERE pythonw3.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 (

        color 1E
        start "" pythonw3.exe .\sppas\bin\preinstallgui.py
        exit

) else (

    REM Search for python3 command, ie Python3 is installed but not WxPython
    WHERE python3.exe >nul 2>nul
    if %ERRORLEVEL% EQU 0 (

        color 1E
        start "" python3.exe .\sppas\bin\preinstall.py --wxpython
        if %ERRORLEVEL% EQU 0 (
            start "" python3.exe .\sppas\bin\preinstallgui.py
            exit

        ) else (
            color 04
            echo The setup failed to install wxpython automatically.
            echo See http://www.sppas.org/installation.html to do it manually.
        )

    ) else (
            echo Python version 3 is not an internal command of your operating system.
            echo Install it first, preferably from the Windows Store.
        REM Search for python command, ie Python is installed.
        WHERE python.exe >nul 2>nul
        if %ERRORLEVEL% EQU 0 (
            python.exe .\sppas\bin\checkpy.py
            if %ERRORLEVEL% EQU 0 (
                start "" python.exe .\sppas\bin\preinstall.py --wxpython
                start "" python.exe .\sppas\bin\preinstallgui.py
                exit
            )
        ) else (
            color 4E
            echo Python version 3 is not an internal command of your operating system.
            echo Install it first, preferably from the Windows Store.
        )
    )
)


REM Close the windows which was opened to get admin rights
timeout /t 10




