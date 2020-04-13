# coding: UTF-8
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

    config.po.py
    ~~~~~~~~~~~

"""

import os
import sys
import re
from subprocess import Popen, PIPE
from pip._vendor.distlib.compat import raw_input

# ----------------------------------------------------------------------------


class Installer:
    """
    Classe définissant les différentes méthodes qu'utiliseront l'installer général
    """
    exploit_syst = "all"
    python_version = ""
    wxpython = False
    julius = False

    def __init__(self):
        """Par défaut, notre name prend la valeur de l'os de l'utilisateur"""
        self.set_python_version()

    # ---------------------------------------------------------------------------

    def set_python_version(self):
        p = Popen("python3 --version".split(), stdout=PIPE, stderr=PIPE)
        p.wait()
        line = p.communicate()

        if re.match("Python 3", line[0].decode()) is not None:
            self.python_version = "Python3"
        else:
            self.python_version = "Python2"

    # ---------------------------------------------------------------------------

    def get_wxpython(self):
        return self.wxpython

    # ---------------------------------------------------------------------------

    def get_python_version(self):
        return self.python_version

    # ---------------------------------------------------------------------------

    def get_julius(self):
        return self.julius

    # ---------------------------------------------------------------------------

    def verify_wx(self):
        """blaaaaaaaaaaa"""
        p = Popen("pip show WxPython".split(), stdout=PIPE)
        p.wait()
        line = p.communicate()
        # print(line[0].decode())

        if line[0].decode() == "":
            self.wxpython = False
            choice = ""
            while choice != "o" or choice != "O":
                choice = raw_input("Vous n'avez pas WxPython voulez vous l'installer o/n : ")
                if choice == "o" or choice == "O":
                    print("L'installation de WxPython va commencer")
                    self.install_wxpython()
                    break
                elif choice == "n" or choice == "N":
                    print("Vous ne voulez pas installer WxPython")
                    break

        else:
            self.wxpython = True
            print("WxPython est déjà installé sur votre machine")

    # ---------------------------------------------------------------------------

    def install_wxpython(self):
        """blaaaaaaaaaaa"""
        print("Installation wxpython classe mère")

    # ---------------------------------------------------------------------------

    def verify_julius(self):
        """blaaaaaaaaaaa"""
        p = Popen("julius --version".split(), shell=True, stdout=PIPE, stderr=PIPE)
        p.wait()
        line = p.stderr.read().decode()
        # print(line)

        if "not found" not in line:
            self.julius = False
            choice = ""
            while str(choice) != "o" or str(choice) != "O":
                choice = raw_input("Vous n'avez pas Julius voulez vous l'installer o/n : ")
                if choice == "o" or choice == "O":
                    print("L'installation de Julius va commencer")
                    self.install_julius()
                    break
                elif choice == "n" or choice == "N":
                    print("Vous ne voulez pas installer Julius")
                    break

        else:
            self.julius = True
            print("Julius est déjà installé sur votre machine")

    # ---------------------------------------------------------------------------

    def install_julius(self):
        """blaaaaaaaaaaa"""
        print("Installation julius classe mère")


class Linux(Installer):
    """
    Classe définissant les différentes méthodes qu'utiliseront l'installer Linux
    """
    exploit_syst = "Linux"
    linux_distributor = ""
    linux_release = ""

    def __init__(self):
        """Par défaut, notre name prend la valeur de l'os de l'utilisateur"""
        self.set_python_version()
        self.set_distributor_release()

    # ---------------------------------------------------------------------------

    def get_os_version(self):
        return self.exploit_syst

    # ---------------------------------------------------------------------------

    def get_os_distributor(self):
        return self.linux_distributor

    # ---------------------------------------------------------------------------

    def get_os_release(self):
        return self.linux_release

    # ---------------------------------------------------------------------------

    def install_wxpython(self):
        if self.get_python_version() == "Python3":
            command = "-f https://extras.wxpython.org/" + "wxPython4" + "/extras/linux/gtk3/" + \
                       self.get_os_distributor() + "-" + self.get_os_release()
            print("Installation de la librairie wxpython")
            p = Popen(['pip',  'install', '-U', ' ', command, ' ', "wxPython"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            p.wait()
            p.communicate()
            print("Installation de la librairie libsdl1.2-dev")
            p1 = Popen("sudo apt-get install libsdl1.2-dev".split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
            p1.wait()
            p1.communicate()
            print("Installation de la librairie sox")
            p2 = Popen("sudo apt-get install -y sox".split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
            p2.wait()
            p2.communicate()
    # ---------------------------------------------------------------------------

    def set_distributor_release(self):
        p = Popen("lsb_release -a".split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        line = p.communicate()
        linux_information = line[0].decode()
        tab2 = dict()
        tab = linux_information.split("\n")
        tab.pop()
        for line_information in tab:
            key_attr = line_information.split(":")
            key_attr[1] = key_attr[1].replace("\t", "")
            tab2[key_attr[0]] = key_attr[1]
        self.linux_distributor = tab2["Distributor ID"].lower()
        self.linux_release = tab2["Release"]

    # ---------------------------------------------------------------------------

    def install_julius(self):
        """blaaaaaaaaaaa"""
        p = Popen("sudo apt install julius".split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
        p.wait()
        p.communicate()
        print("Julius a bien été installé sur votre machine")


class Windows(Installer):
    """
    Classe définissant les différentes méthodes qu'utiliseront l'installer Windows
    """
    exploit_syst = "Windows"

    def get_os_version(self):
        return self.exploit_syst

    # ---------------------------------------------------------------------------

    def install_wxpython(self):
        """blaaaaaaaaaaa"""
        Popen("pip install -U wxPython".split(), shell=True, stdout=PIPE, stderr=PIPE)
        print("WxPython a bien été installé sur votre machine")

    # ---------------------------------------------------------------------------

    def install_julius(self):
        """blaaaaaaaaaaa"""
        print("Installtion julius Windows")


class MacOs(Installer):
    """
    Classe définissant les différentes méthodes qu'utiliseront l'installer MacOs
    """
    exploit_syst = "MacOs"

    def get_os_version(self):
        return self.exploit_syst

    # ---------------------------------------------------------------------------

    def install_wxpython(self):
        """blaaaaaaaaaaa"""
        print("Installtion julius MacOs")

    # ---------------------------------------------------------------------------

    def install_julius(self):
        """blaaaaaaaaaaa"""
        print("Installtion julius MacOs")


if sys.platform == "darwin":
    my_installer = MacOs()
elif sys.platform == "win32":
    my_installer = Windows()
else:
    my_installer = Linux()

print(my_installer.verify_wx())
print(my_installer.verify_julius())

