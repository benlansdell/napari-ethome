#From: https://forum.image.sc/t/using-napari-to-annotate-animal-behaviors-events-in-video-data-to-a-csv-file/55971

import csv
import napari
import napari_plot

from functools import partial
from pathlib import Path
from napari.utils.notifications import show_info
from napari_plot._qt.qt_viewer import QtViewer

from ethome import create_dataset, create_metadata
from lib import *

CSV_OUT = Path('test_annotations.csv').expanduser()
if not CSV_OUT.exists():
    CSV_OUT.write_text("file,frame,action\n")

# adjust keybindings to your liking
KEYMAP = {
    'u': 'turn_left',
    'i': 'turn_right',
    'h': 'start_walk',
    'j': 'stop_walk',
}

# this writes the frame, layer source, and action each time you press a key
def on_keypress(key, viewer):
    action = KEYMAP[key]
    frame = viewer.dims.current_step[0]
    layer = viewer.layers.selection.active or viewer.layers[-1]

    show_info(action)  # if you want some visual feedback
    with open(CSV_OUT, 'a') as f:
        csv.writer(f).writerow([layer.source.path, frame, action])

viewer = napari.Viewer()
for key in KEYMAP:
    viewer.bind_key(key, partial(on_keypress, key))

viewer1d = napari_plot.ViewerModel1D()
widget = QtViewer(viewer1d)
viewer.window.add_dock_widget(widget, area="bottom", name="Line Widget")
test_widget = ExampleQWidget(viewer1d)
viewer.window.add_dock_widget(test_widget, area="right", name="Line Widget")

napari.run()