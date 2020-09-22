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
        return cropped_faces, detected_coords

    # -----------------------------------------------------------------------

    def __track_persons(self, video_buffer):
        """Associate a person to each of the detected faces.

        :param video_buffer: (sppasFacesVideoBuffer)

        """
        iter_image = video_buffer.__iter__()
        prev_image = next(iter_image)
        prev_cropped_img, prev_cropped_coords = self.__get_cropped_faces(video_buffer, prev_image, 0)

        # INSTEAD of the following: compare buffer with known persons
        prev_persons = [(str(x), i) for i, x in enumerate(range(len(prev_cropped_img)))]
        persons = [prev_persons]

        # Compare each set of detected faces to the previous ones
        for i in range(video_buffer.__len__()):
            image = next(iter_image)

            # Create a list of images with the cropped faces
            cropped_img, cropped_coords = self.__get_cropped_faces(video_buffer, image, i)
            cur_persons = [None]*len(cropped_img)

            # Compare current faces to the previous ones
            all_scores = list()  # list of list of scores
            for j, cropped_img in enumerate(cropped_img):
                scores_j = self._scores_img_similarity(
                    cropped_img, prev_cropped_img,
                    cropped_coords[i], prev_cropped_coords
                    )
                all_scores.append(scores_j)

            # Analyse scores to associate a face to a person
            best_face_idx = self._get_best_scores(all_scores)
            for j in range(len(best_face_idx)):
                best_idx = best_face_idx[j]
                cur_persons[j] = ("name", best_idx)

        """
        Next step is, for each image of the video, to compare the already
        known reference images to the detected faces, then:
            - associate a face index to each recognized person,
            - add un-recognized detected face to the list of unknown person,
            - associate such faces to such new references. 
      
        # Check that each face is matching with only one person, not several ones
        # in case of a face is associated to several persons, choose the one 
        # with the best distance
        
        # Browse all faces/persons in video_buffer to save results
        # Add not-found faces to our catalogue of unknown-faces
        # Associate face/person to such un-recognized faces

        """

    # -----------------------------------------------------------------------

    def _scores_img_similarity(self, ref_img, compare_imgs, ref_coords=None, compare_coords=None):
        """Evaluate a score to know how similar images are.

        :param ref_img: (sppasImage)
        :param compare_imgs: (list of sppasImage)
        :param ref_coords: (sppasCoord)
        :param compare_coords: (list of sppasCoord)

        """
        if compare_coords is None:
            compare_coords = [None]*len(compare_imgs)
        if len(compare_imgs) != len(compare_coords):
            raise Exception

        scores = list()
        for hyp_img, hyp_coords in zip(compare_imgs, compare_coords):
            cmp = sppasImageCompare(ref_img, hyp_img, ref_coords, hyp_coords)
            scores.append(cmp.score())

        return scores

    # -----------------------------------------------------------------------

    def _get_best_scores(self, all_scores):
        """Return a list with the index of the best score for each list of scores.

        :param all_scores: (list of list of scores)
        :return: (list) index of the best score or -1 if no score is better than the others

        """
        best = list()
        for scores in all_scores:
            best_index = -1
            second_best = -1
            delta_best = 0.
            if len(scores) == 1:
                if scores[0] > 0.5:
                    best_index = 0

            else:
                # sort the scores: the higher the better
                sorted_scores = list(reversed(sorted(scores)))

                # Evaluate the average delta among 2 consecutive scores
                s_prev = sorted_scores[0]
                sum_delta = 0.
                for i in range(1, len(scores)):
                    s_cur = sorted_scores[i]
                    sum_delta += (s_prev - s_cur)
                    s_prev = s_cur
                avg_delta_score = sum_delta / float(len(scores) - 1)

                # Evaluate the dist between the best and the second best
                best_index = scores.index(sorted_scores[0])
                second_best = scores.index(sorted_scores[1])
                delta_best = sorted_scores[0] - sorted_scores[1]
                if delta_best < avg_delta_score:
                    # the best is not significantly better than the 2nd best
                    delta_best = 0

            best.append((best_index, delta_best, second_best))

        # Search for conflicts, if any.
        # Store conflicts to not modify 'best' on the fly.
        conflicts = list()
        for i in range(len(best)):
            # does this index is somewhere later on in the best?
            for j in range(i+1, len(best)):
                if best[i][0] == best[j][0]:
                    # we have a conflict
                    conflicts.append((i, j))

        # Replace the best by the 2nd best when conflicts
        for (i, j) in conflicts:
            if best[i][1] > best[j][1]:
                best[j] = (best[j][2], 0, -1)
            else:
                best[i] = (best[i][2], 0, -1)

        # Search for conflicts, if any.
        # Store conflicts to not modify 'best' on the fly.
        conflicts = list()
        for i in range(len(best)):
            # does this index is somewhere later on in the best?
            for j in range(i+1, len(best)):
                if best[i][0] == best[j][0]:
                    # we have a conflict
                    conflicts.append((i, j))

        # Cancel the worse candidate of conflicts
        for (i, j) in conflicts:
            if best[i][1] > best[j][1]:
                best[j] = (-1, 0, -1)
            else:
                best[i] = (-1, 0, -1)

        return [b[0] for b in best]

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

