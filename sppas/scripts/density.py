#!/usr/bin/env python
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

    scripts.dendity.py
    ~~~~~~~~~~~~~~~~~~

    ... a script to search for phoneme reduction density areas.

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.anndata import sppasRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasLocation

from sppas.src.calculus import sppasKullbackLeibler
from sppas.src.calculus import find_ngrams

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="{:s} -i file [options]"
                              "".format(os.path.basename(PROGRAM)),
                        description="... a script to find phoneme "
                                    "reduction density areas.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file name')

parser.add_argument("-t",
                    metavar="value",
                    default=1,
                    type=int,
                    help='Tier number (default: 1)')

parser.add_argument("-o",
                    metavar="file",
                    help='Output file name')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Extract parameters, load data...

file_output = None
if args.o:
    file_output = args.o
trs_out = sppasTranscription("PhonemesDensity")

n = 3   # n-value of the ngram
w = 7   # window size

parser = sppasRW(args.i)
trs = parser.read()

if args.t <= 0 or args.t > len(trs):
    print('Error: Bad tier number {:d}.\n'.format(args.t))
    sys.exit(1)

tier = trs[args.t-1]
if len(tier) == 0:
    print('Empty tier {:s}.\n'.format(tier.get_name()))
    sys.exit(1)

if tier.get_first_point().get_radius() is None:
    tier.set_radius(0.001)

# ----------------------------------------------------------------------------
# Extract areas in which there is a density of phonemes reductions

# Extract phonemes during 30ms
# ----------------------------
# We create a list of the same size than the tier, with values:
# 0: the phoneme is not during 30ms
# 1: the phoneme is during 30ms

t = trs_out.create_tier('PhonCandidates')
values = list()
nb_reduced_1 = 0
nb_reduced_2 = 0
for ann in tier:
    duration = ann.get_location().get_best().duration()
    # duration here is an instance of sppasDuration()
    if duration == 0.030:
        values.append(2)
        nb_reduced_1 += 1
        t.append(ann.copy())
    elif duration == 0.040:
        values.append(1)
        nb_reduced_2 += 1
        t.append(ann.copy())
    else:
        values.append(0)
if len(values) < 3:
    print('Not enough reduced phonemes {:d}.'.format(len(values)))
print('Among the {:d} phonemes, {:d} are 30ms and {:d} are 40ms.'
      ''.format(len(values), nb_reduced_1, nb_reduced_2))


# Train an ngram model with the list of values
# ---------------------------------------------

data = find_ngrams(values, n)

kl = sppasKullbackLeibler()
eps = 1.0 / (10*float(len(data)))
print("Estimated epsilon = {:f}".format(eps))
kl.set_epsilon(eps)
print("Corrected epsilon = {:f}".format(kl.get_epsilon()))

kl.set_model_from_data(data)

print("The model:")
for k, v in kl.get_model().items():
    print("  --> P({}) = {}".format(k, v))

# Use the model:
# estimate a KL distance between the model and a window on the data
# -----------------------------------------------------------------

# Create a list of all windows (more memory, but faster than a real windowing)
windows = find_ngrams(values, w)

# Estimates the distances between the model and each window
distances = list()
for i, window in enumerate(windows):
    ngram_window = find_ngrams(window, n)
    kl.set_observations(ngram_window)
    dist = kl.eval_kld()
    distances.append(dist)

# Bass-pass filter to adjust distances
ngram_window = find_ngrams(tuple([0]*w),n)
kl.set_observations(ngram_window)
base_dist = kl.eval_kld()
print("Base distance for the bass-pass filter {}: {}".format(ngram_window, base_dist))

for i, d in enumerate(distances):
    if d < base_dist:
        distances[i] = 0.
    else:
        distances[i] = distances[i] - base_dist


# Select the windows corresponding to non-zero areas
# -----------------------------------------------------

inside = False
idx_begin = 0
areas = list()
for i, d in enumerate(distances):
    if d == 0.:
        if inside is True:
            # It's the end of a block of non-zero distances
            inside = False
            areas.append((idx_begin, i-1))
        else:
            # It's the beginning of a block of zero distances
            idx_begin = i
            inside = False
    else:
        inside = True

# the last block was interesting!
if inside is True:
    areas.append((idx_begin, len(distances)-1))

# ----------------------------------------------------------------------------
# From windows to annotations

filtered_tier = trs_out.create_tier('ReductionDensity')
filtered_tier.set_meta('density_estimation_on_tier', tier.get_name())
filtered_tier.set_meta('density_estimation_on_file', args.i)

for t in areas:
    idx_begin = t[0]  # index of the first interesting window
    idx_end = t[1]    # index of the last interesting window

    # Find the index of the first interesting annotation
    window_begin = windows[idx_begin]
    i = 0
    while window_begin[i] == 0 :
        i += 1
    ann_idx_begin = idx_begin + i

    # Find the index of the last interesting annotation
    window_end = windows[idx_end]
    i = w - 1
    while window_end[i] == 0:
        i -= 1
    ann_idx_end = idx_end + i

    # Assign a label to the new annotation
    mean_dist = sum(distances[idx_begin:idx_end+1]) / float(idx_end-idx_begin)
    mean_dist = round(mean_dist, 2)
    if mean_dist == 0:
        print(" ERROR: mean dist equal to 0...")
        continue

    begin = tier[ann_idx_begin].get_lowest_localization().copy()
    end = tier[ann_idx_end].get_highest_localization().copy()
    loc = sppasLocation(sppasInterval(begin, end))
    label = sppasLabel(sppasTag(mean_dist, "float"))

    filtered_tier.create_annotation(loc, label)

if len(filtered_tier) == 0:
    print("No density area found.")

# ----------------------------------------------------------------------------
# Save result

if file_output is None:
    for a in filtered_tier:
        print(a)
else:

    parser.set_filename(file_output)
    parser.write(trs_out)
