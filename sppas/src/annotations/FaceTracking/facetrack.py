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

        # A reference image to represent the portrait/face of each already
        # identified person. List of tuple(person_id, sppasImage)
        self.__img_known_persons = list()

        # Store information about the previously analyzed buffer
        # i.e. the detected faces and persons of the last image.
        self.__prev_faces = list()
        self.__prev_persons = list()

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def enable_tracker(self, value=True):
        """Enable or disable the automatic face tracking.

        When disabled, an identifier is associated to each detected face of
        an image, without any guarantee that it corresponds to the same
        person as in the other images. [very fast]

        When enabled, an identifier is associated to each detected face and
        it should match a person. Then, when the same person is detected in
        several images, its identifier is assigned to all its faces. [very
        very very slow]

        :param value: (bool)

        """
        self.__track_ia = bool(value)

    # -----------------------------------------------------------------------

    def invalidate(self):
        """Invalidate the list of all automatically added faces."""
        self.__img_known_persons = list()
        self.__prev_faces = list()
        self.__prev_persons = list()

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

        self.__img_known_persons = list()
        for key, value in zip(names, faces):
            self.__img_known_persons.append((key, value))

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
            self._track_persons(video_buffer)
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
    def __get_cropped_images(image, coords):
        """Return the list of cropped images of the given coords. """
        cropped_faces = list()
        for face_coord in coords:
            cropped_faces.append(image.icrop(face_coord))
        return cropped_faces

    # -----------------------------------------------------------------------

    def _track_persons(self, video_buffer):
        """Associate a person to each of the detected faces.

        :param video_buffer: (sppasFacesVideoBuffer)

        """
        iter_image = video_buffer.__iter__()
        start_i = 0
        
        # No previous image was analyzed. Use the 1st of this buffer.
        if len(self.__prev_faces) == 0:
            self._create_initial_image_data(video_buffer)
            start_i = 1
            next(iter_image)

        # Compare each list of detected faces of the current image to the ones
        # of the previous image to find who are the persons of the current img.
        for i in range(start_i, video_buffer.__len__()):
            print("* Image {}".format(i))
            image = next(iter_image)

            # Create the list of images with the cropped faces of previous img
            print("  - prev image detected len={}".format(len(self.__prev_persons)))
            prev_img = list()
            for p in self.__prev_persons:
                print("      -> prev image person={}".format(p[0]))
                if p is None:
                    prev_img.append(image.inegative())
                for (pid, img) in self.__img_known_persons:
                    if pid == p[0]:
                        prev_img.append(img)
                        break
            assert(len(self.__prev_persons) == len(prev_img))

            # Create a list of images with the cropped faces of current img
            current_faces = video_buffer.get_detected_faces(i)
            current_img = self.__get_cropped_images(image, current_faces)
            print("  - current image detected len={}".format(len(current_img)))

            # Compare current faces to the previous ones
            print("  - compare cur to prev:")
            prev_img_scores = list()    # list of list of scores
            known_img_scores = list()   # list of list of scores
            for j, cropped_img in enumerate(current_img):
                scores1_j = self._scores_img_similarity(cropped_img, prev_img, current_faces[j], self.__prev_faces)
                print("    -> prev {}: {}".format(j, scores1_j))
                prev_img_scores.append(scores1_j)
                scores2_j = self._scores_img_similarity(cropped_img, [img for pid, img in self.__img_known_persons])
                known_img_scores.append(scores2_j)
                print("    -> prev {}: {}".format(j, scores2_j))

            # Analyse scores to associate a face to a person
            # The returned index is one of the person in the previous image
            best_person_idx_prev = self._get_best_scores(prev_img_scores)
            best_person_idx_known = self._get_best_scores(known_img_scores)
            identified = list()
            for j in range(len(current_img)):
                idx = best_person_idx_known[j]
                if idx != -1:
                    identified.append(self.__img_known_persons[idx][0])

            print("  - bests prev: {}".format(best_person_idx_prev))
            print("  - bests known: {}".format(best_person_idx_known))
            current_persons = list()
            for j in range(len(current_img)):
                best_name = None
                idx = best_person_idx_known[j]
                if idx != -1:
                    best_name = self.__img_known_persons[idx][0]
                else:
                    idx = best_person_idx_prev[j]
                    if idx != -1:
                        # this face is identified as a person in the known persons
                        best_name = self.__prev_persons[idx][0]
                        if best_name in identified:
                            best_name = None

                if best_name is None:
                    # Create a new person name and associated image
                    best_name = "X{:03d}".format(len(self.__img_known_persons))
                    self.__img_known_persons.append((best_name, current_img[j]))

                # set to the list of persons
                current_persons.append((best_name, j))
                print("   -> best name={}".format(best_name))

            self.__prev_faces = current_faces
            self.__prev_persons = current_persons
            video_buffer.set_detected_persons(i, current_persons)

    # -----------------------------------------------------------------------
    
    def _create_initial_image_data(self, video_buffer):
        """Fill in the prev members with the 1st image of the buffer."""
        self.invalidate()
        image = video_buffer[0]
        
        # Store the list of coords with the detected faces
        self.__prev_faces = video_buffer.get_detected_faces(0)
        
        # Create an initial list of images with the cropped faces
        prev_img = self.__get_cropped_images(image, self.__prev_faces)
        # Create the list of person names matching the detected faces
        for i in range(len(self.__prev_faces)):
            person_name = "X{:03d}".format(i)
            self.__prev_persons.append((person_name, i))
            self.__img_known_persons.append((person_name, prev_img[i]))

        video_buffer.set_detected_persons(0, self.__prev_persons)

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
        """Search for the index of the best score for each list of scores.

        :param all_scores: (list of list of scores)
        :return: (list) index of the best score of each list or -1

        """
        # Make a list of tuple(best index, delta score, second best index)
        best = list()
        for scores in all_scores:
            best_index = -1     # index of the best score in scores
            second_best = -1    # index of the second best score in scores
            delta_best = 0.     # score difference between best and second best
            if len(scores) == 0:
                pass

            elif len(scores) == 1:
                if scores[0] > 0.2:
                    best_index = 0

            else:
                # sort the scores: the higher the better
                sorted_scores = list(reversed(sorted(scores)))
                if sorted_scores[0] > 0.2:
                    best_index = scores.index(sorted_scores[0])
                if sorted_scores[1] > 0.2:
                    second_best = scores.index(sorted_scores[1])

                # Evaluate the delta between the best and the second best
                delta_best = sorted_scores[0] - sorted_scores[1]

                if len(scores) > 2:
                    # Evaluate the average delta among 2 consecutive scores
                    s_prev = sorted_scores[0]
                    sum_delta = 0.
                    for i in range(1, len(scores)):
                        s_cur = sorted_scores[i]
                        sum_delta += (s_prev - s_cur)
                        s_prev = s_cur
                    avg_delta_score = sum_delta / float(len(scores) - 1)

                    # Assign a delta only if it makes sense
                    if delta_best < avg_delta_score:
                        # the 1st best is not significantly better than the 2nd best
                        delta_best = 0

            best.append((best_index, delta_best, second_best))

        # Search for conflicts, if any.
        # Store conflicts to not modify 'best' list on the fly.
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

        # re-Search for conflicts, if any.
        # Store conflicts to not modify 'best' on the fly.
        conflicts = list()
        for i in range(len(best)):
            # does this index is somewhere later on in the best?
            for j in range(i+1, len(best)):
                if best[i][0] == best[j][0]:
                    # we have again a conflict
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

