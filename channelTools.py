#
# EXAMPLE RUN CODE
#
# import channelTools
# reload(channelTools)
# channelTools.show()

import sys, os
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from vendor.Qt import QtGui, QtWidgets, QtCore, __binding__
from utils import log, channels

PLATFORM = sys.platform
if 'darwin' in PLATFORM:
    WINTYPE = QtCore.Qt.Tool
else:
    WINTYPE = QtCore.Qt.Window

LOG = log.get_logger(__name__)

if __binding__ == 'PySide2':
    from shiboken2 import wrapInstance
if __binding__ == 'PySide':
    from shiboken import wrapInstance


STYLESHEET = """
QSlider::groove:horizontal {
border: 1px solid #bbb;
background: white;
height: 10px;
border-radius: 4px;
}

QSlider::sub-page:horizontal {
background: #00b000;
border: 1px solid #777;
height: 10px;
border-radius: 4px;
}

QSlider::add-page:horizontal {
background: #fff;
border: 1px solid #777;
height: 10px;
border-radius: 4px;
}

QSlider::handle:horizontal {
background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #eee, stop:1 #ccc);
border: 1px solid #777;
width: 13px;
margin-top: -2px;
margin-bottom: -2px;
border-radius: 4px;
}

QSlider::handle:horizontal:hover {
background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #fff, stop:1 #ddd);
border: 1px solid #444;
border-radius: 4px;
}

QSlider::sub-page:horizontal:disabled {
background: #bbb;
border-color: #999;
}

QSlider::add-page:horizontal:disabled {
background: #eee;
border-color: #999;
}

QSlider::handle:horizontal:disabled {
background: #eee;
border: 1px solid #aaa;
border-radius: 4px;
}
"""


# Allows converting pointers to Python objects
def maya_main_window():
	main_win_ptr = omui.MQtUtil.mainWindow()
	return wrapInstance(long(main_win_ptr), QtWidgets.QWidget)


def show():
    global win
    try:
        win.close()
    except: pass
    win = channel_Dialog()
    win.resize(430, 276)
    win.show()


class channel_Dialog(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(channel_Dialog, self).__init__(parent)

        self.setupUi()
        self.initialize()
        self.setupSlots()
        self.setWindowTitle("Channel Factory")
        self.setWindowFlags(QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    # ------- setup ------- #
    def setupUi(self):
        self.setObjectName("channelFactory")

        mainLayout = QtWidgets.QVBoxLayout(self)
        self.treeWidget = QtWidgets.QTreeWidget()
        mainLayout.addWidget(self.treeWidget)
        self.pb_tag = QtWidgets.QPushButton("Tag")
        mainLayout.addWidget(self.pb_tag)
        self.pb_applyTag = QtWidgets.QPushButton("Apply Tag")
        mainLayout.addWidget(self.pb_applyTag)
        self.treeWidget.headerItem().setText(0, "Channel Name")
        self.treeWidget.headerItem().setText(1, "Keyable")
        self.treeWidget.headerItem().setText(2, "Unlocked")
        self.treeWidget.headerItem().setText(3, "Visible")

    def initialize(self):
        ## Set Columns Width to match content:
        for column in range(self.treeWidget.columnCount()):
            self.treeWidget.setColumnWidth(column, 100)
            # self.treeWidget.resizeColumnToContents( column )

        self.sliderRange = 25
        self.treeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # monitor selection
        self.scriptJobID = cmds.scriptJob(event=["SelectionChanged", self.selectInScene], killWithScene=1)
        # update current selection
        self.selectInScene()

    def setupSlots(self):
        self.pb_tag.clicked.connect(self.attrTag)
        self.pb_applyTag.clicked.connect(self.applyTag)

    def attrTag(self):
        """
        Tag the node by adding and setting "attrTag" attr with channel status.
        """
        sel = cmds.ls(sl=1, l=1)
        for node in sel:
            channels.attrTag(node)

    def applyTag(self):
        """
        Apply channel status according to attribute "attrTag".
        """
        sel = cmds.ls(sl=1, l=1)
        for node in sel:
            channels.applyTag(node)
        cmds.select(cl=1)
        cmds.select(sel)

    def snapToEnd(self, sliderId):
        """
        Call back function. Triggered when a slider is clicked.
        """
        row = int(sliderId.split('|')[0]) # row: 0 - 9
        col = int(sliderId.split('|')[1]) # col: 1 2 3
        item = self.treeWidget.topLevelItem(row)
        slider = self.treeWidget.itemWidget(item, col)
        # snap to end
        if slider.value() > self.sliderRange / 2:
            slider.setValue(self.sliderRange)
            boolResult = 1
        else:
            slider.setValue(0)
            boolResult = 0
        # get attr name
        if row > 9: # custom attr
            attrName = item.text(0)
        else:
            attrName = channels.CHANNELNAMES[row]
        # set selection status according to UI update
        sel = cmds.ls(sl=1, l=1)
        for node in sel:
            channels.setAttrStatus(node, attrName, col, boolResult)
        # check keyable vs visible and update the value for visible slider
        if col == 1:
            visibleSlider = self.treeWidget.itemWidget(item, col + 2)
            if (boolResult and (visibleSlider.value() > 0)):
                visibleSlider.setValue(0)
        # multiple attr selection
        selectedItems = self.treeWidget.selectedItems()
        attrNames = list()
        for selectedItem in selectedItems:
            attrNames.append(selectedItem.text(0))

        for item in selectedItems:
            if item.text(0) not in attrNames:
                self.treeWidget.clearSelection()
                continue
            slider = self.treeWidget.itemWidget(item, col)
            if boolResult:
                slider.setValue(self.sliderRange)
            else:
                slider.setValue(0)
            # check keyable vs visible and update the value for visible slider
            if col == 1:
                visibleSlider = self.treeWidget.itemWidget(item, col + 2)
                if (boolResult and (visibleSlider.value() > 0)):
                    visibleSlider.setValue(0)
            for node in sel:
                channels.setAttrStatus(node, item.text(0), col, boolResult)

    def selectInScene(self):
        """
        Call back function. Triggered when selction changed.
        """
        sel = cmds.ls(sl=1, l=1, type='transform')
        rows = self.treeWidget.topLevelItemCount()
        cols = self.treeWidget.columnCount()

        for i in range(0, rows):
            self.treeWidget.takeTopLevelItem(0)

        if not sel:
            return

        customAttrList = cmds.listAttr(sel[-1], ud=1)
        attrList = list()
        attrList = channels.CHANNELNAMES
        if customAttrList:
            attrList = channels.CHANNELNAMES + customAttrList
        self.mapperSlider = QtCore.QSignalMapper()
        i = 0
        for attr in attrList:
            if attr == 'attrTag':
                continue

            sliderIdA = str(i) + '|'
            item = QtWidgets.QTreeWidgetItem(self.treeWidget)
            ## Column 0
            item.setText(0, attr)
            for col in range(1, cols):
                sliderId = sliderIdA + str(col)
                ## Column 1, 2, 3
                slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.treeWidget)
                self.treeWidget.setItemWidget(item, col, slider)
                slider.setMaximumWidth(self.sliderRange)
                slider.setMaximum(self.sliderRange)
                slider.setPageStep(self.sliderRange)
                slider.setStyleSheet(STYLESHEET)

                self.mapperSlider.setMapping(slider, sliderId)
                slider.sliderReleased.connect(self.mapperSlider.map)
            i += 1
        self.mapperSlider.mapped['QString'].connect(self.snapToEnd)

        self.readCurrentStatus(sel[-1])

    def readCurrentStatus(self, sel):
        """
        Load channel status of sel node.
        """
        rows = self.treeWidget.topLevelItemCount()

        root = self.treeWidget.invisibleRootItem()
        for i in range(rows):
            item = root.child(i)
            attrName = item.text(0)

            # keyable unlocked visible
            keyableSlider = self.treeWidget.itemWidget(item, 1)
            unlockSlider = self.treeWidget.itemWidget(item, 2)
            visibleSlider = self.treeWidget.itemWidget(item, 3)

            keyable = cmds.getAttr('{}.{}'.format(sel, attrName), k=1)
            if keyable:
                keyableSlider.setValue(self.sliderRange)
            else:
                keyableSlider.setValue(0)

            unlock = cmds.getAttr('{}.{}'.format(sel, attrName), l=1)
            if unlock:
                unlockSlider.setValue(0)
            else:
                unlockSlider.setValue(self.sliderRange)

            visible = cmds.getAttr('{}.{}'.format(sel, attrName), cb=1)
            if visible:
                visibleSlider.setValue(self.sliderRange)
            else:
                visibleSlider.setValue(0)

    def closeEvent(self, e):
        cmds.scriptJob(kill=self.scriptJobID, force=1)
        # cmds.scriptJob(exists=self.scriptJobID)
        e.accept()
