"""Display image and 1d plot."""
import napari
import numpy as np
from skimage import data

import napari_plot
from napari_plot._qt.qt_viewer import QtViewer

from qtpy.QtWidgets import QHBoxLayout, QCheckBox, QPushButton, QWidget, QListWidget, QComboBox, QLabel, QVBoxLayout
from qtpy.QtCore import QSize

# create the viewer with an image
viewer = napari.view_image(data.astronaut(), rgb=True)

from qtpy import QtWidgets

class QHSeperationLine(QtWidgets.QFrame):
  '''
  a horizontal seperation line\n
  '''
  def __init__(self):
    super().__init__()
    self.setMinimumWidth(1)
    self.setFixedHeight(20)
    self.setFrameShape(QtWidgets.QFrame.HLine)
    self.setFrameShadow(QtWidgets.QFrame.Sunken)
    self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
    return

class QComboBoxFixedSize(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizeAdjustPolicy(2)
    def minimumSizeHint(self):
        return QSize(200, 0)

class ExampleQWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        cbox = QComboBoxFixedSize()
        cbox.addItem("asdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdf")
        cbox.activated.connect(self._on_click)

        cbox2 = QComboBoxFixedSize()
        cbox2.addItem("trace 1")
        cbox2.activated.connect(self._on_click)


        self.feature_list = QListWidget()
        self.feature_list.addItems(['sparrow', 'robin', 'crow', 'raven',
                                  'woopecker', 'hummingbird'])
        #self.feature_list.setFixedHeight(200)
        self.feature_list.setSelectionMode(
            QtWidgets.QAbstractItemView.MultiSelection
        )

        trainBtn = QPushButton('Train', self)
        trainBtn.clicked.connect(self._on_click)

        vbox = QVBoxLayout(self)
        vbox.addWidget(QHSeperationLine())
        vbox.addWidget(QLabel("Features to train ML model"))
        vbox.addWidget(self.feature_list)

        #Make this dropdown box instead
        self.model_list = QComboBoxFixedSize()
        self.model_list.addItems(['sparrow', 'robin', 'crow', 'raven'])
        vbox.addWidget(QLabel("ML model to train"))
        vbox.addWidget(self.model_list)

        #Make this dropdown box instead
        self.labels_list = QComboBoxFixedSize()
        self.labels_list.addItems(['sparrow', 'robin', 'crow'])
        vbox.addWidget(QLabel("Labels to use for training"))
        vbox.addWidget(self.labels_list)

        vbox.addWidget(trainBtn)

        hbox = QHBoxLayout()

        label = QLabel("View video")
        hbox.addWidget(label)
        hbox.addWidget(cbox)
        vbox.addLayout(hbox)

        checkbox = QCheckBox("Plot tracking", self)
        vbox.addWidget(checkbox)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(QLabel("Plot trace"))
        hbox2.addWidget(cbox2)
        vbox.addLayout(hbox2)
        vbox.addStretch()

        self.setLayout(vbox)

    def _on_click(self):
        print("napari has", len(self.viewer.layers), "layers")

# viewer1d = napari_plot.ViewerModel1D()
# widget = QtViewer(viewer1d)
# viewer.window.add_dock_widget(widget, area="bottom", name="Line Widget")

# # example data
# x = np.arange(0.1, 4, 0.1)
# y1 = np.exp(-1.0 * x)
# y2 = np.exp(-0.5 * x)

# # example variable error bar values
# y1err = 0.1 + 0.1 * np.sqrt(x)
# y2err = 0.1 + 0.1 * np.sqrt(x / 2)


# viewer1d.add_line(np.c_[x, y1], name="Line 1", color="lightblue")
# viewer1d.add_centroids(
#     np.c_[x, y1 - y1err, y1 + y1err], orientation="vertical", color="lightblue", opacity=0.5, name="Line 1 (errors)"
# )
# viewer1d.add_line(np.c_[x, y2], name="Line 2", color="orange")
# viewer1d.add_centroids(
#     np.c_[x, y2 - y2err, y2 + y2err], orientation="vertical", color="orange", opacity=0.5, name="Line 2 (errors)"
# )
# viewer1d.camera.extent = (-0.1, 4.1, 1.0, -0.3)
# viewer1d.axis.x_label = ""
# viewer1d.axis.y_label = ""
# viewer1d.reset_view()

#test_widget = ExampleQWidget(viewer1d)
test_widget = ExampleQWidget(viewer)
viewer.window.add_dock_widget(test_widget, area="right", name="Line Widget")

napari.run()