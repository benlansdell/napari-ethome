"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
from typing import TYPE_CHECKING

from magicgui import magic_factory
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget, QComboBox, QLabel

from magicgui import magicgui
import datetime
from napari_plot._qt.qt_viewer import QtViewer
import napari_plot

import napari
from typing import List
from napari.layers import Image, Tracks

class PipelineQWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.image_layers = []
        self.tracking_layers = []
        cbox = QComboBox()
        for layer in self.viewer.layers:
            if isinstance(layer, Image):
                self.image_layers.append(layer)
                cbox.addItem(layer.name)
            if isinstance(layer, Tracks):
                self.tracking_layers.append(layer)
        cbox.activated.connect(self._on_click)

        self.setLayout(QHBoxLayout())
        label = QLabel("Select a video")
        self.layout().addWidget(label)
        self.layout().addWidget(cbox)

        self.viewer1d = napari_plot.ViewerModel1D()
        widget = QtViewer(self.viewer1d)
        self.viewer.window.add_dock_widget(widget, area="bottom", name="Line Widget")

    def _on_click(self, idx):
        self.viewer.layers.selection.active = self.image_layers[idx]
        for l in self.image_layers:
            l.visible = False
        self.image_layers[idx].visible = True

        for l in self.tracking_layers:
            l.visible = False
        self.tracking_layers[idx].visible = True

def my_fancy_choices_function(gui) -> List[str]:
    return ["otsu", "opening"]

@magicgui(layer_name={"choices": my_fancy_choices_function})
def example_magic_widget(layer_name: str, viewer: napari.Viewer):
    # the current layer_name choice to get the viewer.
    selected_layer = viewer.layers[layer_name]
    # go nuts with your layer.