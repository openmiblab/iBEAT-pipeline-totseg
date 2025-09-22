import os
import logging

# import stage_0_restore
# import stage_1_segment
# import stage_2_display
import stage_3_measure
import stage_4_edit
# import stage_5_archive


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

    group = 'Controls'
    # stage_0_restore.segmentations(SHAREDPATH, LOCALPATH, group) # wont be necessary when running again
    # stage_0_restore.dixons(SHAREDPATH, LOCALPATH,group)
    # stage_1_segment.segment(LOCALPATH, group, task='total_mr')
    # stage_1_segment.segment(LOCALPATH, group, task='tissue_types_mr') 
    # stage_2_display.mosaic(LOCALPATH, group, task='total_mr')
    # stage_2_display.mosaic(LOCALPATH, group, task='tissue_types_mr')
    # stage_2_display.mosaic(LOCALPATH, group, organs=['pancreas', 'liver'], task='total_mr')
    # stage_5_archive.autosegmentation(LOCALPATH, SHAREDPATH, group)
    # stage_5_archive.displays(LOCALPATH, SHAREDPATH, group)
    

    group = 'Patients'
    sites = ['Bari', 'Bordeaux', 'Exeter', 'Leeds', 'Sheffield', 'Turku']
    for site in ['Sheffield', 'Turku']:

        # stage_0_restore.segmentations(SHAREDPATH, LOCALPATH, group, site)
        # stage_0_restore.dixons(SHAREDPATH, LOCALPATH, group, site)
        # stage_1_segment.segment(LOCALPATH, group, site, task='total_mr')

        # stage_1_segment.segment(LOCALPATH, group, site, task='tissue_types_mr')
        # stage_2_display.mosaic(LOCALPATH, group, site, task='total_mr')

        # stage_2_display.mosaic(LOCALPATH, group, site, task='tissue_types_mr')
        # stage_2_display.mosaic(LOCALPATH, group, site, organs=['pancreas', 'liver'], task='total_mr')

        # stage_3_measure.all_organs(LOCALPATH, group, site)
        # stage_3_measure.concatenate(LOCALPATH)

        stage_4_edit.organ_mask(LOCALPATH, group, site, task='total_mr', organ='liver')
        
        # stage_5_archive.autosegmentation(LOCALPATH, SHAREDPATH, group, site)
        # stage_5_archive.displays(LOCALPATH, SHAREDPATH, group, site)
        
        



if __name__ == '__main__':

    run_totseg()