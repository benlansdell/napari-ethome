import napari
import napari_plot
import numpy as np
import pandas as pd

from napari.qt.threading import thread_worker
from napari_plot._qt.qt_viewer import QtViewer
from napari.layers import Image, Tracks

from typing import List
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget, QComboBox, QLabel, \
                            QVBoxLayout, QListWidget, QCheckBox
from qtpy import QtWidgets
from qtpy.QtCore import QSize
from qtpy import QtCore
from qtpy.QtCore import QAbstractTableModel
from qtpy import QtWidgets
from qtpy.QtCore import Qt

#This is hacky... but it works better than other solutions
from .backend import FeatureSet, FEATURE_MAKERS, ethomedf
from .widgets import set_plot_data, add_current_frame_line, update_plot, QComboBoxFixedSize, DataFrameModel

class PipelineQWidget(QWidget):

    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        
        global ethomedf 
        self.backend = ethomedf
        self.df = ethomedf.df

        self.image_layers = []
        self.tracking_layers = []
        self.labels_layer = None

        self.viewer.window.qt_viewer.dockLayerList.setVisible(False)
        self.viewer.window.qt_viewer.dockLayerControls.setVisible(False)

        self._setup_widgets()

        self.viewer1d = napari_plot.ViewerModel1D()
        widget = QtViewer(self.viewer1d, parent = self)
        self.viewer.window.add_dock_widget(widget, area="bottom", name="Line Widget")

        self.stats = StatsQWidget(self.viewer, self.df, self)
        self.viewer.window.add_dock_widget(self.stats, area="left", name="Behavior output")

    def select_features(self):
        items = self.feature_list.selectedItems()
        selected = []
        for i in range(len(items)):
            selected.append(str(self.feature_list.selectedItems()[i].text()))

        for k in selected:
            self.backend.add_features(k)
    
    def _setup_widgets(self):
        self.labeling_list = QListWidget()
        self.labeling_list.addItems([k for k in self.backend.label_sets.keys()])
        self.labeling_list.addItems(['(new)'])
        self.labeling_list.setFixedHeight(110)

        self.feature_list = QListWidget()
        self.feature_list.addItems([k for k in self.backend.feature_sets.keys()])
        self.feature_list.setFixedHeight(110)
        self.feature_list.setSelectionMode(
            QtWidgets.QAbstractItemView.MultiSelection
        )
        self.feature_list.itemSelectionChanged.connect(self.select_features)

        self.prediction_list = QListWidget()
        self.prediction_list.setFixedHeight(110)

        for layer in self.viewer.layers:
            if isinstance(layer, Image):
                if layer.name != 'labels':
                    self.image_layers.append(layer)
                else:
                    self.labels_layers = layer
            if isinstance(layer, Tracks):
                self.tracking_layers.append(layer)

        trainBtn = QPushButton('Train', self)
        trainBtn.clicked.connect(self._on_train_click)

        loadModelBtn = QPushButton('Import model', self)
        loadModelBtn.clicked.connect(self._on_import_model_click)

        recBtn = QPushButton('Record labels', self)
        recBtn.clicked.connect(self._on_record_click)

        saveLabelsBtn = QPushButton('Stop labeling', self)
        saveLabelsBtn.clicked.connect(self._on_stoplabels_click)

        refineBtn = QPushButton('Refine labels', self)
        refineBtn.clicked.connect(self._on_refine_click)

        saveModelBtn = QPushButton('Export model', self)
        saveModelBtn.clicked.connect(self._on_export_click)

        ######################
        ## GUI construction ##
        ######################
        vbox = QVBoxLayout(self)
        vbox.addWidget(QLabel("Label sets (select to use in training)"))
        vbox.addWidget(self.labeling_list)
        hbox1 = QHBoxLayout()
        hbox1.addWidget(recBtn)
        hbox1.addWidget(saveLabelsBtn)
        vbox.addLayout(hbox1)
        vbox.addWidget(QLabel("Features to train ML model"))
        vbox.addWidget(self.feature_list)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(trainBtn)
        hbox2.addWidget(loadModelBtn)
        vbox.addLayout(hbox2)
        vbox.addWidget(QLabel("Models"))
        vbox.addWidget(self.prediction_list)
        hbox = QHBoxLayout()
        hbox.addWidget(refineBtn)
        hbox.addWidget(saveModelBtn)
        vbox.addLayout(hbox)
        vbox.addStretch()
        self.setLayout(vbox)

    def _on_label_click(self, idx):

        if self.labels_layers:
            label_data = self.labels_layers.data[idx,:]
            xdata = np.arange(len(label_data))/self.backend.fps
            set_plot_data(self.viewer1d, xdata, label_data)

    def _on_train_click(self):
        pass

    def _on_import_model_click(self):
        pass

    def _on_record_click(self):
        pass

    def _on_stoplabels_click(self):
        pass

    def _on_refine_click(self):
        pass

    def _on_export_click(self):
        pass

    def _on_model_click(self, idx):

        #If we have a labels layer, plot that in the 1d plot
        fn = list(self.df.metadata.details.keys())[0]
        fps = self.df.metadata.details[fn]['fps']

        if self.labels_layers:
            label_data = self.labels_layers.data[idx,:]
            xdata = np.arange(len(label_data))/fps
            set_plot_data(self.viewer1d, xdata, label_data)

class StatsQWidget(QWidget):

    def __init__(self, viewer, df, parent):
        super().__init__()
        self.parent = parent #Parent is the pipeline widget
        self.backend = self.parent.backend #EthomeDF houses all data and project details
        self.viewer = viewer
        self.df = df
        self.selected_video = None
        self.trace_col = None

        ##################
        ## GUI elements ##
        ##################

        #Default info text
        self.text = QLabel(f"Animals: {self.df.pose.animals}\nBody parts: {self.df.pose.body_parts}")
        self.text.setFixedWidth(200)

        #Load project button
        #loadBtn = QPushButton('Load project', self)
        #loadBtn.clicked.connect(self._on_load_click)

        #Save project button
        saveBtn = QPushButton('Save project', self)
        saveBtn.clicked.connect(self._on_save_click)

        #Video selection list
        cbox = QComboBoxFixedSize()
        for layer in self.viewer.layers:
            if isinstance(layer, Image):
                if layer.name != 'labels':
                    cbox.addItem(layer.name)
        cbox.activated.connect(self._on_videos_click)

        checkbox = QCheckBox("Plot tracking", self)
        checkbox.setChecked(True)
        checkbox.toggled.connect(self._on_tracking_click)
        self.show_tracking_box = checkbox
        #synccheckbox = QCheckBox("Sync plots", self)

        #Select any trace
        cbox2 = QComboBoxFixedSize()
        for col in self.backend.df.columns:
            cbox2.addItem(col)
        cbox2.activated.connect(self._on_trace_click)

        #List of behaviors with keymaps
        tablemodel = DataFrameModel(self.backend.behaviors, self, self.viewer)
        tableview = QtWidgets.QTableView()
        tableview.setModel(tablemodel)

        ############################
        ## Start GUI construction ##
        ############################

        vbox = QVBoxLayout(self)
        vbox.addWidget(saveBtn)
        hbox = QHBoxLayout()
        label = QLabel("View video")
        hbox.addWidget(label)
        hbox.addWidget(cbox)
        vbox.addLayout(hbox)
        hbox3 = QHBoxLayout()
        hbox3.addWidget(checkbox)
        #hbox3.addWidget(synccheckbox)
        vbox.addLayout(hbox3)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(QLabel("Plot trace"))
        hbox2.addWidget(cbox2)
        vbox.addLayout(hbox2)
        vbox.addWidget(QLabel("Behaviors"))
        vbox.addWidget(tableview)
        vbox.addStretch()
        vbox.addWidget(QLabel("Information:"))
        vbox.addWidget(self.text)
        self.setLayout(vbox)

    def _on_click(self):
        pass

    def _on_load_click(self):
        pass 

    def _on_save_click(self):
        pass

    def _on_tracking_click(self):
        if self.selected_video is not None:
            self.parent.tracking_layers[self.selected_video].visible = self.show_tracking_box.isChecked()

    def _on_videos_click(self, idx):
        self.selected_video = idx

        #Make the video visible
        self.viewer.layers.selection.active = self.parent.image_layers[idx]
        for l in self.parent.image_layers:
            l.visible = False
        self.parent.image_layers[idx].visible = True

        #Make the tracking visible
        for l in self.parent.tracking_layers:
            l.visible = False
        self.parent.tracking_layers[idx].visible = self.show_tracking_box.isChecked()

        if self.trace_col is None and self.parent.labels_layers:
            trace_data = self.parent.labels_layers.data[idx,:]
            self.trace_col = 'label'
        elif self.trace_col is not None:
            #Get selected file name
            fn = list(self.df.metadata.details.keys())[idx]
            trace_data = self.backend.df.loc[self.backend.df['filename'] == fn, self.trace_col].values
        else:
            trace_data = np.zeros(len(self.parent.image_layers[idx].data))

        xdata = np.arange(len(trace_data))/self.backend.fps
        set_plot_data(self.parent.viewer1d, xdata, trace_data, ylabel = self.trace_col)

        #Show current frame line
        frame_line = add_current_frame_line(self.parent.viewer1d, self.viewer.dims.current_step[0]/self.backend.fps)
        self.viewer.dims.events.current_step.connect(
            lambda event: update_plot(frame_line, event.value, self.backend.fps)
        )

    def _on_trace_click(self, idx):
        self.trace_col = self.backend.df.columns[idx]
        if self.selected_video is not None:
            fn = list(self.df.metadata.details.keys())[self.selected_video]
            trace_data = self.backend.df.loc[self.backend.df['filename'] == fn, self.trace_col].values
            xdata = np.arange(len(trace_data))/self.backend.fps
            set_plot_data(self.parent.viewer1d, xdata, trace_data, ylabel = self.trace_col)