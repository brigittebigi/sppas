# -*- coding : UTF-8 -*-
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

    src.videodata.facetracking.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from imutils.video import FileVideoStream
import numpy as np
import imutils
import time
import cv2
import os

from sppas.src.config import sppasPathSettings
from sppas.src.imagedata.facedetection import faceDetection


# ---------------------------------------------------------------------------


class faceTracking(object):
    """Class to detect faces.

    :author:       Florian Hocquet
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self, video):
        """Create a new faceTracking instance.

        :param video: (video) The video to process.

        """
        self.__facedetection = faceDetection()
        self.__proto = None
        self.__model = None
        self.__init_files()
        self.__coordinates = list()
        self.video_process(video)
        self.clean_parasite(self.nb_detection())
        # for l in self.__coordinates:
        #     print("Detection")
        #     for c in l:
        #         print(c.__str__())

    # -----------------------------------------------------------------------

    def __init_files(self):
        """Initialise files for detection."""
        try:
            self.__proto = os.path.join(sppasPathSettings().resources, "video", "deploy.prototxt.txt")
            self.__model = os.path.join(sppasPathSettings().resources, "video",
                                        "res10_300x300_ssd_iter_140000.caffemodel")
            raise OSError
        except OSError:
            return "File does not exist"

    # -----------------------------------------------------------------------

    def video_process(self, video):
        """Returns all the faces coordinates in a list"""
        print("[INFO] loading model...")
        net = cv2.dnn.readNetFromCaffe(self.__proto, self.__model)

        print("[INFO] starting video stream...")
        vs = FileVideoStream(video).start()
        time.sleep(2.0)
        while True:
            frame = vs.read()
            if frame is None:
                break

            frame = imutils.resize(frame, width=400)

            self.__coordinates.append(self.__facedetection.detect_faces(frame, net))

            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

        cv2.destroyAllWindows()
        vs.stop()

    # -----------------------------------------------------------------------

    def get_coordinates(self):
        """Returns list with coordinates of faces for each frame."""
        return self.__coordinates

    # -----------------------------------------------------------------------

    def nb_detection(self):
        detections = dict()
        for f in self.__coordinates:
            if len(f) not in detections.keys():
                detections[len(f)] = 1
            else:
                detections[len(f)] += 1
        nb_person = 0
        nb_detections = 0
        for keys, attr in detections.items():
            if detections[keys] > nb_detections:
                nb_detections = detections[keys]
                nb_person = keys
        return nb_person

    # -----------------------------------------------------------------------

    def clean_parasite(self, nb_person):
        parasites = list()
        for f in self.__coordinates:
            if len(f) > nb_person:
                parasites.append(f)
        if len(parasites) / len(self.__coordinates) < 0.0005:
            for p in parasites:
                index = self.__coordinates.index(p)
                self.__coordinates[index].pop()
            parasites.clear()

