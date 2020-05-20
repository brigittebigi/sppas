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

    wxgui.views.filedialogs.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import os
import wx

from sppas.src.config import paths
import sppas.src.anndata.aio
import sppas.src.audiodata.aio

from sppas.src.ui.wxgui.cutils.dialogutils import create_wildcard, extend_path
from .msgdialogs import ShowYesNoQuestion

# ----------------------------------------------------------------------------
# Open
# ----------------------------------------------------------------------------


def OpenAnnotationFiles(multiple=True):
    """Return a list of annotation file names."""

    wildcard = create_wildcard("All files", sppas.src.anndata.aio.extensionsul)
    wildcard += '|' + create_wildcard("SPPAS", sppas.src.anndata.aio.ext_sppas)
    wildcard += '|' + create_wildcard("Praat", sppas.src.anndata.aio.ext_praat)
    wildcard += '|' + create_wildcard("ELAN",  sppas.src.anndata.aio.ext_elan)
    wildcard += '|' + create_wildcard("Transcriber", sppas.src.anndata.aio.ext_transcriber)
    wildcard += '|' + create_wildcard("Phonedit", sppas.src.anndata.aio.ext_phonedit)
    wildcard += '|' + create_wildcard("ASCII", sppas.src.anndata.aio.ext_ascii)

    files = list()
    if multiple is True:
        dlg = wx.FileDialog(None, 
                            "Select annotation file(s)", 
                            os.getcwd(), 
                            "", 
                            wildcard, 
                            wx.FD_OPEN | wx.MULTIPLE | wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            files = dlg.GetPaths()

    else:
        dlg = wx.FileDialog(None, 
                            "Select annotation file", 
                            paths.samples, 
                            "", 
                            wildcard, 
                            wx.FD_OPEN | wx.FD_CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            files.append(dlg.GetPath())

    dlg.Destroy()

    if multiple is False:
        return files[0]
    return files

# ----------------------------------------------------------------------------


def OpenSoundFiles():
    """Return a list of sound file names."""

    wildcard = create_wildcard("Sound files", sppas.src.audiodata.aio.extensionsul)
    wildcard += '|' + create_wildcard("All files", ['*', '*.*'])

    files = list()
    dlg = wx.FileDialog(None, 
                        "Select sound file(s)", 
                        paths.samples, 
                        "", 
                        wildcard, 
                        wx.FD_OPEN | wx.MULTIPLE | wx.FD_CHANGE_DIR)
    if dlg.ShowModal() == wx.ID_OK:
        files = dlg.GetPaths()

    dlg.Destroy()

    return files

# ----------------------------------------------------------------------------


def OpenAnyFiles():
    """ Return a list of file names."""
    
    wildcard = create_wildcard("All files", ['*', '*.*'])

    files = []
    dlg = wx.FileDialog(None, 
                        "Select file(s)", 
                        paths.samples, 
                        "", 
                        wildcard, 
                        wx.FD_OPEN | wx.MULTIPLE | wx.FD_CHANGE_DIR)
    if dlg.ShowModal() == wx.ID_OK:
        files = dlg.GetPaths()

    dlg.Destroy()
    return files

# ----------------------------------------------------------------------------


def OpenSpecificFiles(name, extensions):
    """Return a list of file names with specific extensions."""
    
    wildcard = create_wildcard(name, extensions)

    afile = ""
    dlg = wx.FileDialog(None, 
                        "Select a file", 
                        os.getcwd(), 
                        "", 
                        wildcard, 
                        wx.FD_OPEN | wx.FD_CHANGE_DIR)
    if dlg.ShowModal() == wx.ID_OK:
        afile = dlg.GetPath()

    dlg.Destroy()
    return afile

# ----------------------------------------------------------------------------
# Save
# ----------------------------------------------------------------------------


def SaveAsAnnotationFile(default_dir=None, default_file=None):
    """Return an annotation file name."""

    if default_dir is None:
        default_dir = os.path.dirname(paths.sppas)

    if default_file is None:
        default_file = "newfile.xra"

    save_file = None

    wildcard = create_wildcard("All files", sppas.src.anndata.aio.extensions_out)
    wildcard += '|'+create_wildcard("SPPAS", sppas.src.anndata.aio.ext_sppas)
    wildcard += '|'+create_wildcard("Praat", sppas.src.anndata.aio.ext_praat)
    wildcard += '|'+create_wildcard("ELAN",  sppas.src.anndata.aio.ext_elan)
    wildcard += '|'+create_wildcard("Phonedit", sppas.src.anndata.aio.ext_phonedit)
    wildcard += '|'+create_wildcard("ASCII", sppas.src.anndata.aio.ext_ascii)
    wildcard += '|'+create_wildcard("AnnotationPro", sppas.src.anndata.aio.ext_annotationpro)
    wildcard += '|'+create_wildcard("Subtitles", sppas.src.anndata.aio.ext_subtitles)

    dlg = wx.FileDialog(
        None, message="Choose a file name...",
        defaultDir=default_dir,
        defaultFile=default_file,
        wildcard=wildcard,
        style=wx.FD_SAVE | wx.FD_CHANGE_DIR )

    if dlg.ShowModal() == wx.ID_OK:
        save_file = dlg.GetPath()

    dlg.Destroy()

    return save_file

# ----------------------------------------------------------------------------


def SaveAsAudioFile(default_dir=None, default_file=None):
    """ Return an audio file name."""

    if default_dir is None:
        default_dir = os.path.dirname(paths.sppas)

    if default_file is None:
        default_file = "newfile.wav"

    save_file = None

    wildcard = create_wildcard("All files", sppas.src.audiodata.aio.extensions)
    wildcard += '|' + create_wildcard("Wave", sppas.src.audiodata.aio.ext_wav)
    wildcard += '|' + create_wildcard("SunAu",  sppas.src.audiodata.aio.ext_sunau)

    dlg = wx.FileDialog(
        None,
        message="Choose a file name...",
        defaultDir=default_dir,
        defaultFile=default_file,
        wildcard=wildcard,
        style=wx.FD_SAVE | wx.FD_CHANGE_DIR )

    if dlg.ShowModal() == wx.ID_OK:
        save_file = dlg.GetPath()

    dlg.Destroy()

    return save_file

# ----------------------------------------------------------------------------


def SaveAsImageFile(preferences, image):
    """Save the current image as a PNG picture."""

    extension_map = {"png": wx.BITMAP_TYPE_PNG}
    extensions = extension_map.keys()
    wildcard = create_wildcard("Image files", extensions)

    dialog = wx.FileDialog(None, message="Export to Image",
                           wildcard=wildcard, style=wx.FD_SAVE)

    saved = False
    if dialog.ShowModal() == wx.ID_OK:
        path, extension = extend_path(dialog.GetPath(), extensions, "png")
        overwrite_question = "File '{:s}' exists. Overwrite?".format(path)

        if not os.path.exists(path) or ShowYesNoQuestion(dialog, preferences, overwrite_question) == wx.YES:
            image.SaveFile(path, extension_map[extension])
            saved = True

    dialog.Destroy()
    return saved

# ----------------------------------------------------------------------------


def SaveAsAnyFile(default_dir=None, default_file=None):
    """Select a filename to be saved."""

    if default_dir is None:
        default_dir = os.path.dirname(paths.sppas)

    if default_file is None:
        default_file = "newfile.txt"

    save_file = None
    wildcard = create_wildcard("All files", ['*', '*.*'])
    dlg = wx.FileDialog(
        None,
        message="Choose a file name...",
        defaultDir=default_dir,
        defaultFile=default_file,
        wildcard=wildcard,
        style=wx.FD_SAVE | wx.FD_CHANGE_DIR )

    if dlg.ShowModal() == wx.ID_OK:
        save_file = dlg.GetPath()

    dlg.Destroy()

    return save_file
