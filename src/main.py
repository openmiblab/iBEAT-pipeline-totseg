import os

import logging
import stage_0_restore
import stage_1_segment
import stage_2_display
import stage_3_measure
import stage_4_archive


LOCALPATH = os.path.join(os.getcwd(), 'build')
SHAREDPATH = os.path.join("G:\\Shared drives", "iBEAt_Build")


# Set up logging
logging.basicConfig(
    filename=os.path.join(LOCALPATH, 'error.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def run_totseg():

    # Define input and outputh paths here

    # group = 'Controls'
    # stage_0_restore.dixons(SHAREDPATH, LOCALPATH,group)
    # stage_1_segment.segment(LOCALPATH, group)
    # stage_2_display.mosaic(LOCALPATH, group)
    # stage_2_display.mosaic(LOCALPATH, group, organs=['pancreas', 'liver'])
    # stage_4_archive.autosegmentation(LOCALPATH, SHAREDPATH, group)
    # stage_4_archive.displays(LOCALPATH, SHAREDPATH, group)

    group = 'Patients'
    sites = ['Bari', 'Bordeaux', 'Exeter', 'Leeds', 'Sheffield', 'Turku']
    for site in sites:
        stage_0_restore.dixons(SHAREDPATH, LOCALPATH, group, site)
        stage_1_segment.segment(LOCALPATH, group, site)
        stage_2_display.mosaic(LOCALPATH, group, site)
        # stage_2_display.mosaic(LOCALPATH, group, site, organs=['pancreas', 'liver'])
        stage_4_archive.autosegmentation(LOCALPATH, SHAREDPATH, group, site)
        stage_4_archive.displays(LOCALPATH, SHAREDPATH, group, site)



if __name__ == '__main__':
    run_totseg()