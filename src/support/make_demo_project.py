from ethome import create_metadata 
import json 
from glob import glob 
import os

demo_dir = '/Users/blansdel/projects/napari-ethome/demodata/'
vids = sorted(glob(os.path.join(demo_dir, 'videos/*.avi')))
dlc_files = sorted(glob(os.path.join(demo_dir, 'dlc/*.csv')))
boris_files = sorted(glob(os.path.join(demo_dir, 'boris/*.csv')))
out_file = os.path.join(demo_dir, 'sample_project.json')

# Create metadata
fps = 30
resolution = (1200, 1600)
metadata = create_metadata(dlc_files, labels = boris_files, fps = fps, resolution = resolution, video = vids)

# Save metadata
with open(out_file, 'w') as f:
    json.dump(metadata, f, indent=4)
