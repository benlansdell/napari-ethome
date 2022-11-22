
import numpy as np

from qtpy.QtWidgets import QComboBox
from qtpy import QtWidgets
from qtpy.QtCore import QSize
from qtpy import QtCore
from qtpy.QtCore import QAbstractTableModel
from qtpy import QtWidgets
from qtpy.QtCore import Qt

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

def set_plot_data(viewer1d, x, y, xmin = None, xmax = None, ymin = None, ymax = None, ylabel = 'label'):
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
    viewer1d.camera.set_x_range(xmin, xmax)
    viewer1d.camera.set_y_range(ymin, ymax)
    viewer1d.axis.x_label = "time (s)"
    viewer1d.axis.y_label = ylabel
    viewer1d.reset_view()

def update_plot(frame_line, data, fps = 1):
    current_frame = data[0]/fps
    frame_line.data = [current_frame]

def add_current_frame_line(viewer1d, current_frame):
    viewer1d.add_inf_line([current_frame], name="current_frame", color="red")
    return viewer1d.layers[-1]

class QComboBoxFixedSize(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSizeAdjustPolicy(2)
    def minimumSizeHint(self):
        return QSize(200, 0)

class DataFrameModel(QAbstractTableModel):
    def __init__(self, datain, parent = None, viewer = None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain
        self.viewer = viewer
        self.parent = parent

    def rowCount(self, parent = QtCore.QModelIndex()):
        return len(self.arraydata)

    def columnCount(self, parent = QtCore.QModelIndex()):
        return len(self.arraydata.columns)

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        return self.arraydata.iloc[index.row(),index.column()]

    def setData(self, index, value, role):

        if not index.isValid():
            return False

        if role != QtCore.Qt.EditRole:
            return False

        row = index.row()

        if row < 0 or row >= len(self.arraydata.values):
            return False

        column = index.column()

        if (column < 0) or column >= self.arraydata.columns.size:
            return False

        if column == 0:
            if value in self.arraydata.values[:,column]:
                raise ValueError("Behavior already exists")
            self.parent.backend.update_behaviors()

        #Just grab the first letter of the string
        if column == 1:
            value = value[:1]
            if value in self.arraydata.values[:,column]:
                raise ValueError("Keymap already exists")
            self.parent.backend.update_key_maps()

        #Update the value
        self.arraydata.values[row][column] = value

        #If we chose the last row, add a new row
        if row == len(self.arraydata.values)-1:
            self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
            self.arraydata.loc[len(self.arraydata)] = ["", ""]
            self.endInsertRows()

        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.arraydata.columns[col]
        return None

