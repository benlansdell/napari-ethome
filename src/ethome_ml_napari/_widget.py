"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""

import napari
import napari_plot

import numpy as np

from typing import List
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget, QComboBox, QLabel, \
                            QVBoxLayout, QListWidget
from qtpy import QtWidgets
from napari_plot._qt.qt_viewer import QtViewer
from napari.layers import Image, Tracks

def set_plot_data(viewer1d, x, y, xmin = None, xmax = None, ymin = None, ymax = None):
    if xmin is None:
        xmin = np.min(x)-.2
    if xmax is None:
        xmax = np.max(x)+.2
    if ymin is None:
        ymin = np.min(y)-.2
    if ymax is None:
        ymax = np.max(y)+.2

    try:
        viewer1d.layers.remove("feature_line")
    except ValueError:
        pass

    viewer1d.add_line(np.c_[x, y], name="feature_line", color="lightblue")
    #viewer1d.camera.extent = (xmin, xmax, ymin, ymax)
    viewer1d.camera.set_x_range(xmin, xmax)
    viewer1d.camera.set_y_range(ymin, ymax)
    viewer1d.axis.x_label = "frame"
    viewer1d.axis.y_label = "label"
    viewer1d.reset_view()

def update_plot(frame_line, data):
    current_frame = data[0]
    frame_line.data = [current_frame]

def add_current_frame_line(viewer1d, current_frame):
    viewer1d.add_inf_line([current_frame], name="current_frame", color="red")
    return viewer1d.layers[-1]

class QComboBoxFixedSize(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizeAdjustPolicy(2)
    def minimumSizeHint(self):
        return 50

class PipelineQWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.image_layers = []
        self.tracking_layers = []
        self.labels_layer = None

        #Video selection list
        cbox = QComboBoxFixedSize()
        for layer in self.viewer.layers:
            if isinstance(layer, Image):
                if layer.name != 'labels':
                    self.image_layers.append(layer)
                    cbox.addItem(layer.name)
                else:
                    self.labels_layers = layer
            if isinstance(layer, Tracks):
                self.tracking_layers.append(layer)
        cbox.activated.connect(self._on_click)

        #Feature list
        self.feature_list = QListWidget()
        self.feature_list.addItems(['sparrow', 'robin', 'crow', 'raven',
                                  'woopecker', 'hummingbird'])
        self.feature_list.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        clearBtn = QPushButton('Clear', self)
        clearBtn.clicked.connect(self.onClearClicked)

        countBtn = QPushButton('Count', self)
        countBtn.clicked.connect(self.onCountClicked)
        vbox.addWidget(self.feature_list)

        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout()

        label = QLabel("Select a video")
        hbox.addWidget(label)
        hbox.addWidget(cbox)
        vbox.addLayout(hbox)

        vbox.addStretch()
        self.setLayout(vbox)

        self.viewer1d = napari_plot.ViewerModel1D()
        widget = QtViewer(self.viewer1d)
        self.viewer.window.add_dock_widget(widget, area="bottom", name="Line Widget")

        frame_line = add_current_frame_line(self.viewer1d, self.viewer.dims.current_step[0])
        self.viewer.dims.events.current_step.connect(
            lambda event: update_plot(frame_line, event.value)
        )

    def _on_click(self, idx):
        self.viewer.layers.selection.active = self.image_layers[idx]
        for l in self.image_layers:
            l.visible = False
        self.image_layers[idx].visible = True

        for l in self.tracking_layers:
            l.visible = False
        self.tracking_layers[idx].visible = True

        #If we have a labels layer, plot that in the 1d plot
        if self.labels_layers:
            label_data = self.labels_layers.data[idx,:]
            set_plot_data(self.viewer1d, range(len(label_data)), label_data)