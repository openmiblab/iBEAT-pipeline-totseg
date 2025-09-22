import os
import logging
import shutil
from pathlib import Path

from tqdm import tqdm
import numpy as np
import dbdicom as db
import vreg
import pydmr
from totalsegmentator.map_to_binary import class_map

from utils import radiomics



def concatenate(build_path):
    measurepath = os.path.join(build_path, 'totseg', 'stage_3_measure')
    for group in ['Controls', 'Patients']:
        folder = os.path.join(measurepath, group) 
        folder = Path(folder)
        dmr_files = list(folder.rglob("*.dmr.zip"))  # change the pattern
        if dmr_files == []:
            continue
        dmr_files = [str(f) for f in dmr_files]
        dmr_file = os.path.join(measurepath, f'{group}_totseg_auto')
        pydmr.concat(dmr_files, dmr_file)

        # Create some derived formats for convenience

        # 1. Long format with additional columns (units, type, description)
        long_format_file = os.path.join(measurepath, f'{group}_totseg_auto_long.csv')
        pydmr.pars_to_long(dmr_file, long_format_file)

        # 2. Wide format
        wide_format_file = os.path.join(measurepath, f'{group}_totseg_auto_wide.csv')
        pydmr.pars_to_wide(dmr_file, wide_format_file)
        


def all_organs(build_path, group, site=None):

    automaskpath = os.path.join(build_path, 'totseg', 'stage_1_segment')
    measurepath = os.path.join(build_path, 'totseg', 'stage_3_measure')
    os.makedirs(measurepath, exist_ok=True)

    if group == 'Controls':
        siteautomaskpath = os.path.join(automaskpath, "Controls")
        sitemeasurepath = os.path.join(measurepath, "Controls")         
    else:
        siteautomaskpath = os.path.join(automaskpath, "Patients", site)
        sitemeasurepath = os.path.join(measurepath, "Patients", site)
    os.makedirs(sitemeasurepath, exist_ok=True)

    all_automasks = db.series(siteautomaskpath)

    for automask in tqdm(all_automasks, desc='Extracting metrics'):

        patient, study, series = automask[1], automask[2][0], automask[3][0]

        # If the results already exist, skip
        dmr_file = os.path.join(sitemeasurepath, f'{patient}_{study}_{series}')
        if os.path.exists(f'{dmr_file}.dmr.zip'):
            continue

        # Get mask volume 
        vol = db.volume(automask)

        # Init results
        dmr = {'data':{}, 'pars':{}}
        
        # Loop over the classes
        for idx, roi in tqdm(class_map[series].items(), 'Looping over organs..'):

            # Binary mask
            mask = (vol.values==idx).astype(np.float32)
            if np.sum(mask) == 0:
                continue

            roi_vol = vreg.volume(mask, vol.affine)
           
            # Get skimage features
            try:
                results = radiomics.volume_features(roi_vol, roi)
            except Exception as e:
                logging.error(f"Patient {patient} {roi} - error computing ski-shapes: {e}")
            else:
                
                dmr['data'] = dmr['data'] | {p: v[1:] for p, v in results.items()}
                dmr['pars'] = dmr['pars'] | {(patient, study, p): v[0] for p, v in results.items()}

            # Get radiomics shape features
            try:
                #roi_vol = roi_vol.resample(1)
                results = radiomics.shape_features(roi_vol, roi)
            except Exception as e:
                logging.error(f"Patient {patient} {roi} - error computing radiomics-shapes: {e}")
            else:
                dmr['data'] = dmr['data'] | {p:v[1:] for p, v in results.items()}
                dmr['pars'] = dmr['pars'] | {(patient, study, p): v[0] for p, v in results.items()}


        # Append parsed biomarkers in the dictionary for convenience
        dmr['columns'] = ['body_part', 'biomarker_category', 'biomarker']
        for p in dmr['data']:
            dmr['data'][p] += p.split('-')

        # Write results to file
        pydmr.write(dmr_file, dmr)


