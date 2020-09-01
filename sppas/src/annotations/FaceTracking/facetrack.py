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

    src.annotations.FaceTracking.facetracking.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Requires the "video" feature of SPPAS.
    Automatic face detection in a video, i.e. face tracking, based on opencv
    HaarCascadeClassifier and DNN.

"""

import numpy as np

from sppas.src.exceptions import NegativeValueError
from sppas.src.exceptions import sppasTypeError
from ..FaceDetection import FaceDetection

# ---------------------------------------------------------------------------


class FaceTracking(object):
    """Search for faces on images of a video.

    :author:       Florian Hocquet, Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2020  Brigitte Bigi

    """

    def __init__(self):
        """Create a new FaceTracker instance."""

        # Not currently used:
        # A reference image to represent the face of each person
        # key=a name or any other identifier, value=sppasImage
        self.__img_known_faces = dict()      # user-defined persons
        self.__img_unknown_faces = dict()    # detected unknown persons

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------

    def set_reference_faces(self, known_faces=tuple()):
        """Set the list of images representing faces of known persons.

        ***** CURRENTLY UNUSED *****

        The given images can be a list with images to represents the faces
        or a dictionary with key=string and value=the image.
        :param known_faces: (list of sppasImage or dict)

        """
        names = list()
        faces = list()
        if isinstance(known_faces, (list, tuple)):
            for i, img in enumerate(known_faces):
                if isinstance(img, np.ndarray) is False:
                    raise sppasTypeError(img, "(sppasImages, numpy.ndarray)")
                names.append("#{:03d}".format(i))
        elif isinstance(known_faces, dict):
            for key in enumerate(known_faces):
                img = known_faces[key]
                if isinstance(img, np.ndarray) is False:
                    raise sppasTypeError(img, "(sppasImages, numpy.ndarray)")
                names.append(str(key))
                faces.append(img)
        else:
            raise sppasTypeError(known_faces, "dict, list, tuple")

        self.__img_known_faces = dict()
        for key, value in zip(names, faces):
            self.__img_unknown_faces[key] = value

    # -----------------------------------------------------------------------
    # Automatic detection of the faces in a video
    # -----------------------------------------------------------------------

    def invalidate(self):
        """Invalidate the list of all automatically added faces."""
        self.__img_unknown_faces = list()

    # -----------------------------------------------------------------------

    def detect_buffer(self, video_buffer):
        """Search for faces in the currently loaded buffer of a video.

        :param video_buffer: (sppasFacesVideoBuffer) The video to be processed
        :return: (list of sppasCoordinates)

        """
        # Determine the coordinates of all the detected faces.
        # They are ranked from the highest score to the lowest one.
        video_buffer.detect_faces_buffer()
        # Detection of landmarks is not enabled because it has to be debugged.

        # Assign a person to each detected face
        self.__track_persons(video_buffer)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __track_persons(self, video_buffer):
        """Compare given faces to the reference ones.

        Assign a face index to each person of the buffer.

        :param video_buffer: (sppasFacesVideoBuffer)

        """
        video_buffer.set_default_detected_persons()
        """
        Next step is, for each image of the video, to compare the already
        known and unknown reference images to the detected faces, then:
            - associate a face index to each recognized person,
            - add un-recognized detected face to the list of unknown person,
            - associate such faces to such new references. 
            
        Algorithm for ONE image at index idx in the buffer:
        
        # Create a list of images with the cropped faces
        cropped_faces = list()
        detected_coords = video_buffer.get_detected_faces(i)
        for face_coords in detected_coords:
            cropped_faces.append(image.icrop(face_coords))
        
        # Associate a face index to the user-defined persons, if recognized.
        person_face = dict()
        for person_id in self.__img_known_faces:
            max_dist = 0.
            max_index = 0
            distances = list()
            for detected_face in cropped_faces:
                d = eval_distance(self.__img_known_faces[person_id], detected_face)
                if d > max_dist:
                    max_dist = d
                    max_index = i
                distances.append(d)
            person_face[person_id] = (max_index, distances)
            
        # Associate a face index to the auto-added persons, if recognized.
        # SAME CODE. replace img_known by img_unknown.
                
        # Check that each face is matching with only one person, not several ones
        # in case of a face is associated to several persons, choose the one 
        # with the best distance
        
        # Browse all faces/persons in video_buffer to save results
        # Add not-found faces to our catalogue of unknown-faces
        # Associate face/person to such un-recognized faces

        """

