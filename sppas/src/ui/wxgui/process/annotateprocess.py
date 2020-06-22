# -*- coding: UTF-8 -*-
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

    src.wxgui.process.annotateprocess.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import wx

from sppas.src.annotations.manager import sppasAnnotationsManager

from sppas.src.ui.wxgui.sp_consts import ID_FILES
from sppas.src.ui.wxgui.views.log import ShowLogDialog
from sppas.src.ui.wxgui.views.processprogress import ProcessProgressDialog

# ----------------------------------------------------------------------------


class AnnotateProcess(object):
    """Automatic annotation process, with progress bar.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self, preferences):
        """Constructor.

        :param preferences: (Preferences)

        """
        self.process = sppasAnnotationsManager()
        self.process.set_do_merge(True)
        self.preferences = preferences

    # ------------------------------------------------------------------------

    def IsRunning(self):
        """Return True if the process is running.

        :returns (bool)

        """
        if self.process is None:
            return False
        return True

    # ------------------------------------------------------------------------

    def Run(self, parent, filelist, activeannot, parameters):
        """Execute the automatic annotations.

        :param parent: (wx.Window)
        :param filelist:
        :param activeannot:
        :param parameters:

        """
        message = None

        # Check input files
        if len(filelist) == 0:
           return "Empty selection! Select file(s) to annotate."

        # Fix options
        nbsteps = 0
        for i in range(len(activeannot)):
            if activeannot[i]:
                # if there are languages available and none of them is selected, print an error
                lang = parameters.get_lang(i)
                if len(parameters.get_langlist(i)) > 0 and len(lang) == 0:
                    return "A language must be selected for the " \
                           "annotation \"{:s}\"".format(parameters.get_step_name(i))
                nbsteps += 1
                parameters.activate_step(i)
            else:
                parameters.disable_step(i)

        if nbsteps == 0:
            return "No annotation selected or annotations not properly selected"

        for entry in filelist:
            parameters.add_to_workspace(entry)
        parameters.set_output_extension(self.preferences.GetValue('M_OUTPUT_EXT'), "ANNOT")

        # Create the progress bar then run the annotations
        wx.BeginBusyCursor()
        p = ProcessProgressDialog(parent, self.preferences,
                                  "Automatic annotation processing...")
        self.process.annotate(parameters, p)
        p.close()
        wx.EndBusyCursor()

        # Update the file tree (append new annotated files)
        try:
            evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, ID_FILES)
            evt.SetEventObject(parent)
            wx.PostEvent(parent.GetTopLevelParent(), evt)
            parent.GetTopLevelParent().SetFocus()
            parent.GetTopLevelParent().Raise()
        except Exception as e:
            import logging
            logging.debug("%s" % str(e))
            pass

        # Show report
        try:
            ShowLogDialog(parent, self.preferences, parameters.get_report_filename())
        except:
            message = "Automatic annotation finished.\nSee " + \
                      parameters.get_report_filename() + " for details.\n"

        return message
