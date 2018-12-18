#
# EXAMPLE RUN CODE
#
# import copyKeyframe
# reload(copyKeyframe)
# copyKeyframe.show()

import os
import sys
import maya.cmds as cmds
from Qt import QtWidgets, QtCore, QtGui


PLATFORM = sys.platform
WIN_NAME = 'Copy Keyframes'
if 'darwin' in PLATFORM:
    WINTYPE = QtCore.Qt.Tool
else:
    WINTYPE = QtCore.Qt.Window


def show():
    global win
    try:
        win.close()
    except: pass
    win = copy_Dialog()
    win.resize(400, 220)
    win.show()


class copy_Dialog(QtWidgets.QDialog):
    def __init__(self):
        super(copy_Dialog, self).__init__()

        self.setupUi()
        self.initialize()

        # setup main window
        self.setWindowTitle(WIN_NAME)
        self.setWindowFlags(self.windowFlags() |
                              QtCore.Qt.WindowMaximizeButtonHint |
                              QtCore.Qt.WindowMinimizeButtonHint |
                              QtCore.Qt.WindowCloseButtonHint |
                              QtCore.Qt.Window |
                              # QtCore.Qt.WindowStaysOnTopHint |
                              QtCore.Qt.Tool |
                              WINTYPE)
        # icon = QtGui.QIcon(LEAP_ICON)
        # self.setWindowIcon(icon)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setupSlots()

    def initialize(self):
        self.main_ui['checkbox']['axis_x'].setChecked(True)
        self.main_ui['checkbox']['axis_y'].setChecked(True)
        self.main_ui['checkbox']['axis_z'].setChecked(True)
        self.main_ui['checkbox']['attr_t'].setChecked(True)
        self.main_ui['checkbox']['attr_r'].setChecked(True)
        self.main_ui['checkbox']['attr_s'].setChecked(True)

    # ------- setup ------- #
    def setupUi(self):
        self.setObjectName("kmatExporter")

        mainLayout = QtWidgets.QVBoxLayout(self)
        fLayout_items = QtWidgets.QFormLayout()
        hLayout_btn = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(fLayout_items)
        mainLayout.addLayout(hLayout_btn)

        hLayout_axis = QtWidgets.QHBoxLayout()
        cb_ax = QtWidgets.QCheckBox('x')
        cb_ay = QtWidgets.QCheckBox('y')
        cb_az = QtWidgets.QCheckBox('z')
        hLayout_axis.addWidget(cb_ax)
        hLayout_axis.addWidget(cb_ay)
        hLayout_axis.addWidget(cb_az)
        hLayout_axis.setStretch(0, 1)
        hLayout_axis.setStretch(1, 1)
        hLayout_axis.setStretch(2, 1)

        hLayout_attr = QtWidgets.QHBoxLayout()
        cb_t = QtWidgets.QCheckBox('translate')
        cb_r = QtWidgets.QCheckBox('rotate')
        cb_s = QtWidgets.QCheckBox('scale')
        hLayout_attr.addWidget(cb_t)
        hLayout_attr.addWidget(cb_r)
        hLayout_attr.addWidget(cb_s)
        hLayout_attr.setStretch(0, 1)
        hLayout_attr.setStretch(1, 1)
        hLayout_attr.setStretch(2, 1)

        row = 0

        fLayout_items.insertRow(row, 'Axis:', hLayout_axis)
        row += 1
        fLayout_items.insertRow(row, 'Attribute:', hLayout_attr)
        row += 1
        cb_alpha = QtWidgets.QCheckBox('Alpha')
        fLayout_items.insertRow(row, 'Custom Attr:', cb_alpha)
        row += 1
        line_src = QtWidgets.QLineEdit()
        line_src.setValidator(QtGui.QIntValidator())
        fLayout_items.insertRow(row, 'Source Frame:', line_src)
        row += 1
        line_trg = QtWidgets.QLineEdit()
        fLayout_items.insertRow(row, 'Target Frame:', line_trg)
        rx = QtCore.QRegExp("([0-9]+,)*[0-9]+")
        line_trg.setValidator(QtGui.QRegExpValidator(rx))
        row += 1
        label_trg = QtWidgets.QLabel('Use comma to separate multiple target frames.\nExample: 21,50,95')
        fLayout_items.insertRow(row, '', label_trg)
        row += 1

        btn_apply = QtWidgets.QPushButton("Apply")
        hLayout_btn.addWidget(btn_apply)

        self.main_ui = {
            'buttons': {
                'apply': btn_apply
            },
            'checkbox': {
                'axis_x': cb_ax,
                'axis_y': cb_ay,
                'axis_z': cb_az,
                'attr_t': cb_t,
                'attr_r': cb_r,
                'attr_s': cb_s,
                'attr_alpha': cb_alpha
            },
            'keys': {
                'src': line_src,
                'trg': line_trg
            }
        }

    def setupSlots(self):
        self.main_ui['buttons']['apply'].released.connect(self.hitApply)

    def hitApply(self):
        attrStatus = self.checkStatus()
        src_string = self.main_ui['keys']['src'].text()
        src = int(src_string)
        trg_string = self.main_ui['keys']['trg'].text()
        sel = cmds.ls(sl=1)
        if not sel:
            cmds.confirmDialog(title='ERROR:', message="Please select target object in scene.", button=['OK'], defaultButton='OK')
        for trg in trg_string.split(','):
            if trg:
                trg = int(trg)
                run(src, trg, attrStatus, sel)

    def checkStatus(self):
        attrStatus = list()
        if self.main_ui['checkbox']['axis_x'].isChecked():
            if self.main_ui['checkbox']['attr_t'].isChecked():
                attrStatus.append("translateX")
            else:
                attrStatus.append("")
            if self.main_ui['checkbox']['attr_r'].isChecked():
                attrStatus.append("rotateX")
            else:
                attrStatus.append("")
            if self.main_ui['checkbox']['attr_s'].isChecked():
                attrStatus.append("scaleX")
            else:
                attrStatus.append("")
        else:
            attrStatus.extend(("", "", ""))
        if self.main_ui['checkbox']['axis_y'].isChecked():
            if self.main_ui['checkbox']['attr_t'].isChecked():
                attrStatus.append("translateY")
            else:
                attrStatus.append("")
            if self.main_ui['checkbox']['attr_r'].isChecked():
                attrStatus.append("rotateY")
            else:
                attrStatus.append("")
            if self.main_ui['checkbox']['attr_s'].isChecked():
                attrStatus.append("scaleY")
            else:
                attrStatus.append("")
        else:
            attrStatus.extend(("", "", ""))
        if self.main_ui['checkbox']['axis_z'].isChecked():
            if self.main_ui['checkbox']['attr_t'].isChecked():
                attrStatus.append("translateZ")
            else:
                attrStatus.append("")
            if self.main_ui['checkbox']['attr_r'].isChecked():
                attrStatus.append("rotateZ")
            else:
                attrStatus.append("")
            if self.main_ui['checkbox']['attr_s'].isChecked():
                attrStatus.append("scaleZ")
            else:
                attrStatus.append("")
        else:
            attrStatus.extend(("", "", ""))
        if self.main_ui['checkbox']['attr_alpha'].isChecked():
            attrStatus.append("Alpha")
        return attrStatus

    def messageBox(self, msg):
        msgBox = QtWidgets.QMessageBox(self)
        msgBox.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        msgBox.setText(msg)
        return msgBox.exec_()


def isValidPath(filepath):
    if os.path.isfile(filepath):
        return True
    dirName = os.path.dirname(filepath)
    if os.path.isdir(dirName):
        return True
    return False


def run(src, trg, attrStatus, sel):
    for obj in sel:
        cmds.select(cl=1)
        cmds.select(obj)
        for attr in attrStatus:
            if not attr:
                continue
            if cmds.attributeQuery(attr, node=obj, exists=True):
                anim = cmds.listConnections(obj + '.' + attr, d=False, s=True)[0]
                copyKeyframe(anim, attr, src, trg)


def copyKeyframe(anim, at, src, trg):
    v = cmds.getAttr(anim + '.output', t=src)
    cmds.setKeyframe(t=(trg, trg), at=at, v=v)
