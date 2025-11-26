import os
import logging

import numpy as np
from tqdm import tqdm
import dbdicom as db
import pyvista as pv

from utils.total_segmentator_class_maps import class_map
from utils import plot, data, sdf
from utils.constants import SITE_IDS







def WIP_movie(build_path, group, site=None,
        kidney=False, all=False, liver_pancreas=False):
    
    datapath = os.path.join(build_path, 'dixon', 'stage_2_data')
    maskpath = os.path.join(build_path, 'totseg', 'stage_1_segment')
    displaypath = os.path.join(build_path, 'totseg', 'stage_2_display')
    os.makedirs(displaypath, exist_ok=True)

    
    if site is None:
        sitedatapath = os.path.join(datapath, group)
        sitemaskpath = os.path.join(maskpath, group)
        sitedisplaypath = os.path.join(displaypath, group)
    else:
        sitedatapath = os.path.join(datapath, site, group)
        sitemaskpath = os.path.join(maskpath, group, site)
        sitedisplaypath = os.path.join(displaypath, group, site)

    # Build output folders
    movies_all = os.path.join(displaypath, sitedisplaypath, 'Movies_all')
    movies_kidneys = os.path.join(displaypath, sitedisplaypath, 'Movies_kidneys')
    movies_liver_pancreas = os.path.join(displaypath, sitedisplaypath, 'Movies_liver_pancreas')
    os.makedirs(movies_all, exist_ok=True)
    os.makedirs(movies_kidneys, exist_ok=True)
    os.makedirs(movies_liver_pancreas, exist_ok=True)

    record = data.dixon_record()

    # Loop over the masks
    for mask in tqdm(db.series(sitemaskpath), 'Displaying masks..'):

        # Get the corresponding outphase series
        patient_id = mask[1]
        study = mask[2][0]
        sequence = data.dixon_series_desc(record, patient_id, study)
        series_op = [sitedatapath, patient_id, study, f'{sequence}_out_phase']

        # Skip if not in the right site
        if patient_id[:4] not in SITE_IDS[site]:
            continue

        # Get arrays
        op_arr = db.volume(series_op).values
        mask_arr = db.volume(mask).values
        rois = {}
        for idx, roi in class_map['total_mr'].items():
            rois[roi] = (mask_arr==idx).astype(np.int16)

        # Build movie (kidneys only)
        if kidney:
            file = os.path.join(movies_kidneys, f'{patient_id}_{study}_{sequence}_kidneys.mp4')
            if not os.path.exists(file):
                rois_k = {k:v for k, v in rois.items() if k in ["kidney_left", "kidney_right"]}
                plot.movie_overlay(op_arr, rois_k, file)

        # Build movie (all ROIS)
        if all:
            file = os.path.join(movies_all, f'{patient_id}_{study}_{sequence}_all.mp4')
            if not os.path.exists(file):
                plot.movie_overlay(op_arr, rois, file)

        if liver_pancreas:
            file = os.path.join(movies_liver_pancreas, f'{patient_id}_{study}_{sequence}_pancreas_liver.mp4')
            if not os.path.exists(file):
                rois_pl = {k:v for k, v in rois.items() if k in ["pancreas", "liver"]}
                plot.movie_overlay(op_arr, rois_pl, file)


def display_3d(maskpath, displaypath, organ, group, site=None):

    os.makedirs(displaypath, exist_ok=True)
    
    if site is None:
        sitemaskpath = os.path.join(maskpath, group)
        imagefile = os.path.join(displaypath, f"{group}_{organ}.png")
    else:
        sitemaskpath = os.path.join(maskpath, group, site)
        imagefile = os.path.join(displaypath, f"{group}_{site}_{organ}.png")
    
    # Plot settings
    aspect_ratio = 16/9
    width = 150
    height = 150

    # Get baseline kidneys
    masks = db.series(sitemaskpath)
    masks = [k for k in masks if k[2][0] in ['Visit1', 'Baseline']]

    # Count nr of mosaics
    n_mosaics = len(masks)
    nrows = int(np.round(np.sqrt((width*n_mosaics)/(aspect_ratio*height))))
    ncols = int(np.ceil(n_mosaics/nrows))

    plotter = pv.Plotter(window_size=(ncols*width, nrows*height), shape=(nrows, ncols), border=False, off_screen=True)
    plotter.background_color = 'white'

    mask_idx = {roi:idx for idx, roi in class_map['total_mr'].items()}
    organ_idx = mask_idx[organ]

    row = 0
    col = 0
    for mask_series in tqdm(masks, desc=f'Processing..'):

        if mask_series[3][0] != 'total_mr':
            continue

        patient = mask_series[1]

        # Set up plotter
        plotter.subplot(row,col)
        plotter.add_text(f"{patient}", font_size=6)
        if col == ncols-1:
            col = 0
            row += 1
        else:
            col += 1

        # Load data
        vol = db.volume(mask_series, verbose=0)
        mask = (vol.values==organ_idx).astype(np.int16)
        # mask, _ = sdf.compress(mask, (64, 64, 64))

        # Plot tile
        orig_vol = pv.wrap(mask.astype(float))
        orig_vol.spacing = vol.spacing
        orig_surface = orig_vol.contour(isosurfaces=[0.5])
        plotter.add_mesh(orig_surface, color='lightblue', opacity=1.0, style='surface')
        plotter.camera_position = 'iso'
        plotter.view_vector((1, 0, 0))  # rotate 180° around vertical axis
    
    plotter.screenshot(imagefile)
    plotter.close()



def mosaic(datapath, maskpath, displaypath, group, site=None, organs=None, task='total_mr'):

    os.makedirs(displaypath, exist_ok=True)
    
    if site is None:
        sitedatapath = os.path.join(datapath, group)
        sitemaskpath = os.path.join(maskpath, group)
        sitedisplaypath = os.path.join(displaypath, group)
    else:
        sitedatapath = os.path.join(datapath, group, site)
        sitemaskpath = os.path.join(maskpath, group, site)
        sitedisplaypath = os.path.join(displaypath, group, site)

    # Build output folders
    if organs is None:
        sitedisplaypath = os.path.join(sitedisplaypath, f'mosaic_{task}')
    else:
        sitedisplaypath = os.path.join(sitedisplaypath, 'mosaic_' + '_'.join(organs))
    os.makedirs(sitedisplaypath, exist_ok=True)

    record = data.dixon_record()
    all_series = db.series(sitedatapath)

    # Loop over the masks
    for mask in tqdm(db.series(sitemaskpath), 'Displaying masks..'):

        # Skip if not the right task
        if mask[3][0] != task:
            continue

        # Get the outphase series for the mask
        patient_id = mask[1]
        study = mask[2][0]
        sequence = data.dixon_series_desc(record, patient_id, study)
        series_op = [sitedatapath, patient_id, mask[2], (f'{sequence}_out_phase', 0)]

        # Skip if Dixon series is not there
        if series_op not in all_series:
            continue

        # Skip if not in the right site
        if site is not None:
            if patient_id[:4] not in SITE_IDS[site]:
                continue

        # Skip if file already exists
        png_file = os.path.join(sitedisplaypath, f'{patient_id}_{study}_{sequence}.png')
        if os.path.exists(png_file):
             continue

        # Read arrays
        op_arr = db.volume(series_op).values
        mask_arr = db.volume(mask).values
        rois = {}
        for idx, roi in class_map[task].items():
            rois[roi] = (mask_arr==idx).astype(np.int16)

        # Build mosaic
        if organs is None:
            plot.mosaic_overlay(op_arr, rois, png_file)
        else:
            rois_k = {k:v for k, v in rois.items() if k in organs}
            if rois_k == {}:
                raise ValueError(f'No organs {organs} found in {patient_id} {study}.')
            plot.mosaic_overlay(op_arr, rois_k, png_file)


if __name__=='__main__':

    DIXONPATH = r"C:\Users\md1spsx\Documents\Data\iBEAt_Build\dixon\stage_2_data"
    SEGMENTPATH = r"C:\Users\md1spsx\Documents\Data\iBEAt_Build\totseg\stage_1_segment"
    MOSAICPATH = r"C:\Users\md1spsx\Documents\Data\iBEAt_Build\totseg\stage_2_display"
    os.makedirs(MOSAICPATH, exist_ok=True)

    logging.basicConfig(
        filename=os.path.join(MOSAICPATH, 'error.log'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # mosaic(DIXONPATH, SEGMENTPATH, MOSAICPATH, 'Controls', site=None, organs=['pancreas'], task='total_mr')
    # mosaic(DIXONPATH, SEGMENTPATH, MOSAICPATH, 'Patients', site='Bari', organs=['pancreas'], task='total_mr')

    display_3d(SEGMENTPATH, MOSAICPATH, 'pancreas', 'Controls')
    display_3d(SEGMENTPATH, MOSAICPATH, 'pancreas', 'Patients', 'Bari')



