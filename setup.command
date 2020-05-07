#!/bin/bash
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              the automatic
#           \__   |__/  |__/  |___| \__             annotation and
#              \  |     |     |   |    \             analysis
#           ___/  |     |     |   | ___/              of speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2020  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File:    setup.command
# Author:  Brigitte Bigi
# Summary: Complete installation: install SPPAS external required programs.
# ---------------------------------------------------------------------------

BLACK='\e[0;30m'
WHITE='\e[1;37m'
LIGHT_GRAY='\e[0;37m'
DARK_GRAY='\e[1;30m'
BLUE='\e[0;34m'
DARK_BLUE='\e[1;34m'
GREEN='\e[0;32m'
LIGHT_GREEN='\e[1;32m'
CYAN='\e[0;36m'
LIGHT_CYAN='\e[1;36m'
RED='\e[0;31m'
LIGHT_RED='\e[1;31m'
PURPLE='\e[0;35m'
LIGHT_PURPLE='\e[1;35m'
BROWN='\e[0;33m'
YELLOW='\e[1;33m'
NC='\e[0m' # No Color


# ===========================================================================
# Fix global variables
# ===========================================================================

# Fix the locale with a generic value!
LANG='C'

# Program infos
PROGRAM_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)


# ===========================================================================
# MAIN
# ===========================================================================
export PYTHONIOENCODING=UTF-8

PYTHON=""
v="0"

echo -n "Search for 'python3' command for Python: "
for cmd in `which -a python3`;
do
    v=$($cmd -c "import sys; print(sys.version_info[0])");
    if [[ "$v" == "3" ]]; then
        PYTHON=$cmd;
        break;
    fi;
done

if [ -z "$PYTHON" ]; then
    echo "not found."
    echo -n "Search for 'python' command for Python 3: "
    for cmd in `which -a python`;
    do
        v=$($cmd -c "import sys; print(sys.version_info[0])");
        if [[ "$v" == "3" ]]; then
            PYTHON=$cmd;
            break;
        fi;
    done
else
    echo "OK";
fi

echo;

if [ -z "$PYTHON" ]; then
    echo "not found.";
    echo "Python version 3 is not an internal command of your operating system.";
    echo "Install it first http://www.python.org.";
    exit -1;
fi

# Get the name of the system
unamestr=`uname | cut -f1 -d'_'`;

echo "Setup starts with: ";
echo "  - Command: '$PYTHON' (version $v)";
echo "  - System:  $unamestr";
echo "  - Display:  $DISPLAY";
echo "  - Location: $PROGRAM_DIR";

if [ -e .deps~ ];  then rm .deps~;  fi

echo "Run the installer program to install wxpython...";
$PYTHON $PROGRAM_DIR/sppas/bin/preinstall.py --wxpython
if [ $? -eq 1 ] ; then

    echo -e "${RED}This setup failed to install wxpython automatically."

    # Install of wxpython failed. Continue with the CLI for other requirements.
    $PYTHON $PROGRAM_DIR/sppas/bin/preinstall.py --nowxpython -a
    if [ $? -eq 1 ] ; then
        echo -e "${RED}This setup failed to install automatically the required packages."
        echo -e "See http://www.sppas.org/installation.html to do it manually.${NC}"
        echo
        exit -1
    fi

else
    # Install of wxpython success. Continue with the GUI for other requirements.
    # TO BE IMPLEMENTED!!!!!!!!
    $PYTHON $PROGRAM_DIR/sppas/bin/preinstall.py --nowxpython -a
    if [ $? -eq 1 ] ; then
        echo -e "${RED}This setup failed to install automatically the required packages."
        echo -e "See http://www.sppas.org/installation.html to do it manually.${NC}"
        echo
        exit -1
    fi
fi


