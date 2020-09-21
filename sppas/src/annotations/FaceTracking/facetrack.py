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

import logging
import numpy as np

from sppas.src.exceptions import NegativeValueError
from sppas.src.exceptions import sppasTypeError
from sppas.src.imgdata import sppasCoords
from sppas.src.imgdata import sppasImageCompare
from sppas.src.calculus import slope_intercept
from sppas.src.calculus import linear_fct
from sppas.src.calculus import tansey_linear_regression

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
        self.__track_ia = False

        # Not currently used:
        # A reference image to represent the face of each person
        # key=a name or any other identifier, value=sppasImage
        self.__img_known_faces = dict()

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def invalidate(self):
        """Invalidate the list of all automatically added faces."""
        self.__img_known_faces = list()

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
            self.__img_known_faces[key] = value

    # -----------------------------------------------------------------------
    # Automatic detection of the faces in a video
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
        if self.__track_ia is True:
            self.__track_persons(video_buffer)
        else:
            video_buffer.set_default_detected_persons()

        # Remove un-relevant detected faces and fill-in holes
        video_buffer.remove_isolated()
        video_buffer.remove_rare_persons()
        video_buffer.fill_in_holes()

        # Smooth the trajectory of the coordinates
        # self.__smooth_coords(video_buffer)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    @staticmethod
    def __get_cropped_faces(video_buffer, image, idx):
        """Return the list of cropped face images detected at given index.

        """
        cropped_faces = list()
        detected_coords = video_buffer.get_detected_faces(idx)
        for face_coords in detected_coords:
            cropped_faces.append(image.icrop(face_coords))
        return cropped_faces

    # -----------------------------------------------------------------------

    def __track_persons(self, video_buffer):
        """Associate a person to each of the detected faces.

        :param video_buffer: (sppasFacesVideoBuffer)

        """
        iter_image = video_buffer.__iter__()
        prev_image = next(iter_image)
        prev_cropped = self.__get_cropped_faces(video_buffer, prev_image, 0)
        prev_persons = [str(x) for x in range(len(prev_cropped))]
        persons = [prev_persons]

        for i in range(video_buffer.__len__()):
            image = next(iter_image)

            # Create a list of images with the cropped faces
            cropped = self.__get_cropped_faces(video_buffer, image, i)

            # Compare current faces to the previous ones
            for i, cropped_img in enumerate(cropped):
                scores_i = self.__scores_img_similarity(cropped_img, prev_cropped)
                # person_i = the person with the best score

        """
        Next step is, for each image of the video, to compare the already
        known and unknown reference images to the detected faces, then:
            - associate a face index to each recognized person,
            - add un-recognized detected face to the list of unknown person,
            - associate such faces to such new references. 
            
        
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

    # -----------------------------------------------------------------------

    def __scores_img_similarity(self, ref_img, compare_imgs):
        """Evaluate a score to know how similar images are.

        :param ref_img: (sppasImage)
        :param compare_imgs: (list of sppasImage)

        """
        scores = list()
        for hyp_img in compare_imgs:
            cmp = sppasImageCompare(ref_img, hyp_img)
            print(cmp.compare_areas())
            print(cmp.compare_sizes())
            print(cmp.compare_with_mse())
            print(cmp.score())
            scores.append(cmp.score())

        return scores

    # -----------------------------------------------------------------------

    def __smooth_coords(self, video_buffer):
        """Smooth the trajectory of the detected coordinates of each person.

        :param video_buffer: (sppasFacesVideoBuffer)

        """
        if len(video_buffer) <= 2:
            return

        # For each detected person, smooth the trajectory of the coordinates
        person_coords = video_buffer.coords_by_person()

        for person_id in person_coords:
            coords = person_coords[person_id]
            cache = list()
            cache.append(person_coords[person_id][0])
            cache.append(person_coords[person_id][1])
            for i in range(2, len(video_buffer)):
                if coords[i] is None:
                    continue
                cache.append(person_coords[person_id][i])
                # Predict x of p2
                p1 = (cache[0].y, cache[0].x)
                p3 = (cache[2].y, cache[2].x)
                a, b = slope_intercept(p1, p3)
                x = linear_fct(cache[1].y, a, b)

                # Predict y of p2
                p1 = (cache[0].x, cache[0].y)
                p3 = (cache[2].x, cache[2].y)
                a, b = slope_intercept(p1, p3)
                y = linear_fct(cache[1].x, a, b)

                cache.pop(0)

# ---------------------------------------------------------------------------


class FaceRecognition(object):

    def __init__(self, known_persons):
        """

        :param known_persons: (dict) key=name; value=image

        """
        self.__known_persons = known_persons

    # -----------------------------------------------------------------------

    def identify(self, image):
        """Return who, among the known person, is in the given image."""
        pass

    # -----------------------------------------------------------------------

    def scores_img_similarity(self, image):
        """Evaluate a score to know how similar the known images are.

        :param image: (sppasImage) The image to compare with
        :return: dict key=person_id, value=score

        """
        scores = dict()
        for ref_name in self.__known_persons:
            ref_img = self.__known_persons[ref_name]
            cmp = sppasImageCompare(image, ref_img)
            print("areas: {}".format(cmp.compare_areas()))
            print("sizes: {}".format(cmp.compare_sizes()))
            print("mse:   {}".format(cmp.compare_with_mse()))
            print("kld:   {}".format(cmp.compare_with_kld()))
            print(" -> combined: {}".format(cmp.score()))
            scores[ref_name] = cmp.score()
        return scores

    # -----------------------------------------------------------------------

