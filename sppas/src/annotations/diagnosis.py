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

    src.annotations.diagnosis.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import codecs
import os

from sppas.src.config import sg
from sppas.src.config import annots
from sppas.src.config import info

import sppas.src.imgdata
from sppas.src.anndata import sppasRW
import sppas.src.audiodata.aio

# ----------------------------------------------------------------------------

anndata_ext = ["."+e for e in sppasRW.extensions_in()]
imgdata_ext = sppas.src.imgdata.extensions
audiodata_ext = sppas.src.audiodata.aio.extensions

# ----------------------------------------------------------------------------


class sppasDiagnosis:
    """Diagnose if files are appropriate.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    A set of methods to check if files are valid for SPPAS automatic
    annotations. Each method returns a status and a message depending on the
    fact that the given file is matching the requirements.

    """

    EXPECTED_CHANNELS = 1
    EXPECTED_FRAME_RATE = 16000
    EXPECTED_SAMPLE_WIDTH = 2

    # ------------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------------

    @staticmethod
    def check_file(filename):
        """Check file of any type: audio or image or annotated file.

        The extension of the filename is used to know the type of the file.

        :param filename: (str) name of the input file to diagnose.
        :returns: tuple with (status identifier, message)

        """
        ext = os.path.splitext(filename)[1]

        if ext.lower() in audiodata_ext:
            return sppasDiagnosis.check_audio_file(filename)

        if ext.lower() in anndata_ext:
            return sppasDiagnosis.check_trs_file(filename)

        if ext.lower() in imgdata_ext:
            return sppasDiagnosis.check_img_file(filename)

        message = info(1006, "annotations") + \
                  (info(1020, "annotations")).format(extension=ext)
        return annots.error, message

    # ------------------------------------------------------------------------

    @staticmethod
    def check_audio_file(filename):
        """Check an audio file.

        Are verified:

            1. the format of the file (error);
            2. the number of channels (error);
            3. the sample width (error or warning);
            4. the framerate (error or warning;
            5. the filename (warning).

        :param filename: (str) name of the input file
        :returns: tuple with (status identifier, message)

        """
        status = annots.ok
        message = ""

        # test file format: can we support it?
        try:
            audio = sppas.src.audiodata.aio.open(filename)
            fm = audio.get_framerate()
            sp = audio.get_sampwidth()*8
            nc = audio.get_nchannels()
            audio.close()
        except UnicodeDecodeError:
            message = info(1004, "annotations") + \
                      (info(1026, "annotations")).format(encoding=sg.__encoding__)
            return annots.error, message
        except Exception as e:
            message = info(1004, "annotations") + str(e)
            return annots.error, message

        if nc > sppasDiagnosis.EXPECTED_CHANNELS:
            status = annots.error
            message += (info(1010, "annotations")).format(number=nc)

        if sp < sppasDiagnosis.EXPECTED_SAMPLE_WIDTH*8:
            status = annots.error
            message += (info(1012, "annotations")).format(sampwidth=sp)

        if fm < sppasDiagnosis.EXPECTED_FRAME_RATE:
            status = annots.error
            message += (info(1014, "annotations")).format(framerate=fm)

        if status != annots.error:
            if sp > sppasDiagnosis.EXPECTED_SAMPLE_WIDTH*8:
                status = annots.warning
                message += (info(1016, "annotations")).format(sampwidth=sp)

            if fm > sppasDiagnosis.EXPECTED_FRAME_RATE:
                status = annots.warning
                message += (info(1018, "annotations")).format(framerate=fm)

        # test US-ASCII chars
        if all(ord(x) < 128 for x in filename) is False:
            status = annots.warning
            message += info(1022, "annotations")

        if " " in filename:
            status = annots.warning
            message += info(1024, "annotations")

        # test whitespace
        if status == annots.error:
            message = info(1004, "annotations") + message
        elif status == annots.warning:
            message = info(1002, "annotations") + message
        else:
            message = info(1000, "annotations")

        return status, message

    # ------------------------------------------------------------------------

    @staticmethod
    def check_trs_file(filename):
        """Check an annotated file.

        Are verified:

            1. the format of the file (error);
            2. the file encoding (error);
            3. the filename (warning).

        :param filename: (string) name of the input file
        :returns: tuple with (status identifier, message)

        """
        status = annots.ok
        message = info(1000, "annotations")

        # test encoding
        try:
            f = codecs.open(filename, "r", sg.__encoding__)
            f.close()
        except UnicodeDecodeError:
            message = info(1004, "annotations") + \
                      (info(1026, "annotations")).format(encoding=sg.__encoding__)
            return annots.error, message
        except Exception as e:
            message = info(1004, "annotations") + str(e)
            return annots.error, message

        # test US_ASCII in filename
        if all(ord(x) < 128 for x in filename) is False:
            message = info(1002, "annotations") + info(1022, "annotations")
            return annots.warning, message

        # test whitespace in filename
        if " " in filename:
            message = info(1002, "annotations") + info(1024, "annotations")
            return annots.warning, message

        return status, message

    # ------------------------------------------------------------------------

    @staticmethod
    def check_img_file(filename):
        """Check an image file.

        Are verified:

            Nothing

        :param filename: (string) name of the input file
        :returns: tuple with (status identifier, message)

        """
        status = annots.ok
        message = info(1000, "annotations")
        return status, message
