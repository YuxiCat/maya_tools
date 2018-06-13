#
# EXAMPLE RUN CODE
#
# import renameTools
# reload(renameTools)
# renameTools.show()

import sys, os
import string
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.mel as mm
from vendor.Qt import QtGui, QtWidgets, QtCore, __binding__
from utils import log

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


# Allows converting pointers to Python objects
def maya_main_window():
    main_win_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_win_ptr), QtWidgets.QWidget)


def show():
    global win
    try:
        win.close()
    except: pass
    win = rename_Dialog()
    win.resize(340, 394)
    win.show()


class rename_Dialog(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(rename_Dialog, self).__init__(parent)

        self.setupUi()
        self.setupSlots()
        self.setWindowTitle("Rename Factory")
        self.setWindowFlags(self.windowFlags() |
                            QtCore.Qt.WindowMaximizeButtonHint |
                            QtCore.Qt.WindowMinimizeButtonHint |
                            QtCore.Qt.WindowCloseButtonHint |
                            QtCore.Qt.Window |
                            QtCore.Qt.WindowStaysOnTopHint |
                            WINTYPE)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def setupUi(self):
        self.setObjectName("renameWindow")

        mainLayout = QtWidgets.QVBoxLayout(self)
        # groupboxes
        groupBox_rename = QtWidgets.QGroupBox("Rename")
        groupBox_replace = QtWidgets.QGroupBox("Replace")
        groupBox_prefix = QtWidgets.QGroupBox("Prefix")
        groupBox_suffix = QtWidgets.QGroupBox("Suffix")
        # lineedits
        lineEdit_rename = QtWidgets.QLineEdit(groupBox_rename)
        lineEdit_search = QtWidgets.QLineEdit(groupBox_replace)
        lineEdit_replace = QtWidgets.QLineEdit(groupBox_replace)
        lineEdit_prefix = QtWidgets.QLineEdit(groupBox_prefix)
        lineEdit_suffix = QtWidgets.QLineEdit(groupBox_suffix)
        # buttons
        btn_rename = QtWidgets.QPushButton("Rename", groupBox_rename)
        btn_apply = QtWidgets.QPushButton("Apply", groupBox_replace)
        btn_prefix = QtWidgets.QPushButton("Prefix", groupBox_prefix)
        btn_suffix = QtWidgets.QPushButton("Suffix", groupBox_suffix)
        # labels
        label_rename = QtWidgets.QLabel("eg: spine_#_jnt", groupBox_rename)
        label_search = QtWidgets.QLabel("Search for:", groupBox_replace)
        label_replace = QtWidgets.QLabel("Replace with:", groupBox_replace)
        # layout for rename section
        vLayout_rename = QtWidgets.QVBoxLayout(groupBox_rename)
        hLayout_rename = QtWidgets.QHBoxLayout()
        hLayout_rename.addWidget(lineEdit_rename)
        hLayout_rename.addWidget(btn_rename)
        vLayout_rename.addLayout(hLayout_rename)
        vLayout_rename.addWidget(label_rename)
        # layout for search / replace section
        gLayout_replace = QtWidgets.QGridLayout(groupBox_replace)
        gLayout_replace.addWidget(label_search, 0, 0, QtCore.Qt.AlignRight)
        gLayout_replace.addWidget(label_replace, 1, 0, QtCore.Qt.AlignRight)
        gLayout_replace.addWidget(lineEdit_search, 0, 1)
        gLayout_replace.addWidget(lineEdit_replace, 1, 1)
        gLayout_replace.addWidget(btn_apply, 1, 2)
        # layout for prefix
        hLayout_prefix = QtWidgets.QHBoxLayout(groupBox_prefix)
        hLayout_prefix.addWidget(lineEdit_prefix)
        hLayout_prefix.addWidget(btn_prefix)
        # layout for suffix
        hLayout_suffix = QtWidgets.QHBoxLayout(groupBox_suffix)
        hLayout_suffix.addWidget(lineEdit_suffix)
        hLayout_suffix.addWidget(btn_suffix)
        # main layout
        mainLayout.addWidget(groupBox_rename)
        mainLayout.addWidget(groupBox_replace)
        mainLayout.addWidget(groupBox_prefix)
        mainLayout.addWidget(groupBox_suffix)

        self.data = {
            'buttons': {
                'rename': btn_rename,
                'apply': btn_apply,
                'prefix': btn_prefix,
                'suffix': btn_suffix
            },
            'lineedit': {
                'rename': lineEdit_rename,
                'search': lineEdit_search,
                'replace': lineEdit_replace,
                'prefix': lineEdit_prefix,
                'suffix': lineEdit_suffix
            }
        }

    def setupSlots(self):
        self.data['buttons']['rename'].clicked.connect(self.setRename)
        self.data['buttons']['apply'].clicked.connect(self.replaceName)
        self.data['buttons']['prefix'].clicked.connect(self.addPrefix)
        self.data['buttons']['suffix'].clicked.connect(self.addSuffix)

    def setRename(self):
        """
        Call back function. To set names in a format of AA_#_BB based on selection order.
        """
        sel = cmds.ls(selection=True, uuid=1)
        newName = self.data['lineedit']['rename'].text()
        if '#' not in newName:
            LOG.error('Input must have one "#".')
            return False
        newName = newName.split('#', 1)
        num = 1
        for uuid in sel:
            obj = cmds.ls(uuid)
            if obj:
                obj = obj[0]
                cmds.rename(obj, newName[0] + str(num) + newName[1])
            else:
                LOG.warning('UUID {} does not exist in scene.'.format(uuid))
            num = num + 1

    def addPrefix(self):
        """
        Call back function. To add prefix to selected nodes.
        """
        prefix = self.data['lineedit']['prefix'].text()
        sel = cmds.ls(selection=True, uuid=1)
        for uuid in sel:
            obj = cmds.ls(uuid)
            if obj:
                obj = obj[0]
                shortName = self.getShortName(obj)
                cmds.rename(obj, prefix + shortName)

    def addSuffix(self):
        """
        Call back function. To add suffix to selected nodes.
        """
        suffix = self.data['lineedit']['suffix'].text()
        sel = cmds.ls(selection=True, uuid=1)
        for uuid in sel:
            obj = cmds.ls(uuid)
            if obj:
                obj = obj[0]
                shortName = self.getShortName(obj)
                cmds.rename(obj, shortName + suffix)

    def replaceName(self):
        """
        Call back function. To replace string A with B for selected nodes.
        """
        search_str = str(self.data['lineedit']['search'].text())
        replace_str = str(self.data['lineedit']['replace'].text())
        mm.eval('searchReplaceNames ' + search_str + ' ' + replace_str + " selected")

    def getShortName(self, obj):
        """
        Get short name for a node.
        Args:
            obj: Target object.
        Return: String of the short name of target object.
        """
        sep = obj.rpartition('|')
        return sep[-1]
