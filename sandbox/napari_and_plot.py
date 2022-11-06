"""Display image and 1d plot."""
import napari
import numpy as np
from skimage import data

import napari_plot
from napari_plot._qt.qt_viewer import QtViewer

from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget

# create the viewer with an image
viewer = napari.view_image(data.astronaut(), rgb=True)


class ExampleQWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        btn = QPushButton("Click me!")
        btn.clicked.connect(self._on_click)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(btn)

    def _on_click(self):
        print("napari has", len(self.viewer.layers), "layers")
        self.viewer.axis.x_label = "Now I've been clicked!"
        self.viewer.reset_view()


viewer1d = napari_plot.ViewerModel1D()
widget = QtViewer(viewer1d)
viewer.window.add_dock_widget(widget, area="bottom", name="Line Widget")

# example data
x = np.arange(0.1, 4, 0.1)
y1 = np.exp(-1.0 * x)
y2 = np.exp(-0.5 * x)

# example variable error bar values
y1err = 0.1 + 0.1 * np.sqrt(x)
y2err = 0.1 + 0.1 * np.sqrt(x / 2)


viewer1d.add_line(np.c_[x, y1], name="Line 1", color="lightblue")
viewer1d.add_centroids(
    np.c_[x, y1 - y1err, y1 + y1err], orientation="vertical", color="lightblue", opacity=0.5, name="Line 1 (errors)"
)
viewer1d.add_line(np.c_[x, y2], name="Line 2", color="orange")
viewer1d.add_centroids(
    np.c_[x, y2 - y2err, y2 + y2err], orientation="vertical", color="orange", opacity=0.5, name="Line 2 (errors)"
)
viewer1d.camera.extent = (-0.1, 4.1, 1.0, -0.3)
viewer1d.axis.x_label = ""
viewer1d.axis.y_label = ""
viewer1d.reset_view()

test_widget = ExampleQWidget(viewer1d)
viewer.window.add_dock_widget(test_widget, area="right", name="Line Widget")

napari.run()