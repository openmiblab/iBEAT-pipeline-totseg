import os

import dbdicom as db
import vreg
from totalsegmentator.map_to_binary import class_map

from utils import render

DIXONS = os.path.join(os.getcwd(), 'build', 'dixon', 'stage_2_data')
SEGMENTATIONS = os.path.join(os.getcwd(), 'build', 'totseg', 'stage_1_segment')


def display_surface():
    patient = '5128_007'
    study = 'Baseline'
    classes = {
    #    "tissue_types_mr": ["torso_fat"], 
        "total_mr": ["kidney_left", "kidney_right", "liver","pancreas"],
    }
    opacity = [1, 1, 1, 1]
    masks = []
    for task in classes:
        series = [SEGMENTATIONS, patient, study, task]
        vol = db.volume(series)
        label_map = {v: k for k, v in class_map[task].items()}
        masks += [(vol.values == label_map[s]) for s in classes[task]]
    render.surface_with_clipping(masks, vol.spacing, above_opacity=0.2, n_iter=60, relaxation=0.2, opacity=opacity)


if __name__=='__main__':
    display_surface()
