#
# EXAMPLE RUN CODE
#
# import jointTools
# reload(jointTools)
# jointTools.show()

import sys, os
import maya.cmds as cmds
from vendor.Qt import QtGui, QtWidgets, QtCore
from utils import joints as jo
reload(jo)

PLATFORM = sys.platform
if 'darwin' in PLATFORM:
    WINTYPE = QtCore.Qt.Tool
else:
    WINTYPE = QtCore.Qt.Window


def show():
    global win
    try:
        win.close()
    except: pass
    win = joint_Dialog()
    win.resize(274, 423)
    win.show()


class joint_Dialog(QtWidgets.QDialog):
    def __init__(self):
        super(joint_Dialog, self).__init__()

        self.setupUi()
        self.initialize()
        self.setDefault()
        self.setupSlots()
        self.setWindowTitle("Joint Factory")
        self.setWindowFlags(self.windowFlags() |
                      QtCore.Qt.WindowMaximizeButtonHint |
                      QtCore.Qt.WindowMinimizeButtonHint |
                      QtCore.Qt.WindowCloseButtonHint |
                      QtCore.Qt.Window |
                      QtCore.Qt.WindowStaysOnTopHint |
                      WINTYPE)

    # ------- setup ------- #
    def setupUi(self):
        self.setObjectName("jointFactory")

        mainLayout= QtWidgets.QVBoxLayout(self)

        # buttons
        pb_toggle = QtWidgets.QPushButton("Toggle Local Axes Visibility")
        pb_orientJoints = QtWidgets.QPushButton("Orient Joints")
        pb_planarOrientJoints = QtWidgets.QPushButton("Planar Orient Joints for 3")
        pb_minusX = QtWidgets.QPushButton("-")
        pb_plusX = QtWidgets.QPushButton("+")
        pb_minusY = QtWidgets.QPushButton("-")
        pb_plusY = QtWidgets.QPushButton("+")
        pb_minusZ = QtWidgets.QPushButton("-")
        pb_plusZ = QtWidgets.QPushButton("+")
        pb_insertJoints = QtWidgets.QPushButton("Apply")
        pb_copyJointOrient = QtWidgets.QPushButton("Copy Joint Orientation")
        pb_turnOffLRA = QtWidgets.QPushButton("Turn Off All LRA")

        pb_minusX.setMaximumSize(QtCore.QSize(30, 16777215))
        pb_plusX.setMaximumSize(QtCore.QSize(30, 16777215))
        pb_minusY.setMaximumSize(QtCore.QSize(30, 16777215))
        pb_plusY.setMaximumSize(QtCore.QSize(30, 16777215))
        pb_minusZ.setMaximumSize(QtCore.QSize(30, 16777215))
        pb_plusZ.setMaximumSize(QtCore.QSize(30, 16777215))

        # radio buttons
        rb_worldUpAxisX = QtWidgets.QRadioButton("x")
        rb_worldUpAxisY = QtWidgets.QRadioButton("y")
        rb_worldUpAxisZ = QtWidgets.QRadioButton("z")
        rb_aimAxisX = QtWidgets.QRadioButton("x")
        rb_aimAxisY = QtWidgets.QRadioButton("y")
        rb_aimAxisZ = QtWidgets.QRadioButton("z")
        rb_upAxisX = QtWidgets.QRadioButton("x")
        rb_upAxisY = QtWidgets.QRadioButton("y")
        rb_upAxisZ = QtWidgets.QRadioButton("z")

        rbg_worldUpAxis = QtWidgets.QButtonGroup(self)
        rbg_worldUpAxis.addButton(rb_worldUpAxisX)
        rbg_worldUpAxis.addButton(rb_worldUpAxisY)
        rbg_worldUpAxis.addButton(rb_worldUpAxisZ)
        rbg_aimAxis = QtWidgets.QButtonGroup(self)
        rbg_aimAxis.addButton(rb_aimAxisX)
        rbg_aimAxis.addButton(rb_aimAxisY)
        rbg_aimAxis.addButton(rb_aimAxisZ)
        rbg_upAxis = QtWidgets.QButtonGroup(self)
        rbg_upAxis.addButton(rb_upAxisX)
        rbg_upAxis.addButton(rb_upAxisY)
        rbg_upAxis.addButton(rb_upAxisZ)

        hLayout_worldUpAxis = QtWidgets.QHBoxLayout()
        hLayout_worldUpAxis.addWidget(rb_worldUpAxisX)
        hLayout_worldUpAxis.addWidget(rb_worldUpAxisY)
        hLayout_worldUpAxis.addWidget(rb_worldUpAxisZ)
        hLayout_aimAxis = QtWidgets.QHBoxLayout()
        hLayout_aimAxis.addWidget(rb_aimAxisX)
        hLayout_aimAxis.addWidget(rb_aimAxisY)
        hLayout_aimAxis.addWidget(rb_aimAxisZ)
        hLayout_upAxis = QtWidgets.QHBoxLayout()
        hLayout_upAxis.addWidget(rb_upAxisX)
        hLayout_upAxis.addWidget(rb_upAxisY)
        hLayout_upAxis.addWidget(rb_upAxisZ)

        # checkbox
        cb_orientChildren = QtWidgets.QCheckBox("Orient children")
        cb_orient2World = QtWidgets.QCheckBox("Orient Joint to World")

        cb_orientChildren.setLayoutDirection(QtCore.Qt.LeftToRight)
        cb_orient2World.setLayoutDirection(QtCore.Qt.LeftToRight)

        # combo box
        combo_upAxis = QtWidgets.QComboBox()
        combo_upAxis.addItem("+")
        combo_upAxis.addItem("-")
        combo_aimAxis = QtWidgets.QComboBox()
        combo_aimAxis.addItem("+")
        combo_aimAxis.addItem("-")
        combo_worldUpAxis = QtWidgets.QComboBox()
        combo_worldUpAxis.addItem("+")
        combo_worldUpAxis.addItem("-")

        # labels
        label_upAxis = QtWidgets.QLabel("Up Axis")
        label_worldUpAxis = QtWidgets.QLabel("World Up Axis:")
        label_aimAxis = QtWidgets.QLabel("Aim Axis:")
        label_x = QtWidgets.QLabel("x")
        label_y = QtWidgets.QLabel("y")
        label_z = QtWidgets.QLabel("z")
        label_insertJoints = QtWidgets.QLabel("Insert Joints:")
        label_upAxis.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        label_worldUpAxis.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        label_aimAxis.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)

        # line edits
        le_x = QtWidgets.QLineEdit()
        le_y = QtWidgets.QLineEdit()
        le_z = QtWidgets.QLineEdit()
        le_insertJoints = QtWidgets.QLineEdit()

        spacerStart = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        spacerEnd = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        gLayout_orient = QtWidgets.QGridLayout()
        gLayout_orient.setContentsMargins(-1, -1, 0, -1)
        gLayout_orient.addLayout(hLayout_worldUpAxis, 4, 2, 1, 1)
        gLayout_orient.addLayout(hLayout_aimAxis, 2, 2, 1, 1)
        gLayout_orient.addWidget(cb_orientChildren, 0, 2, 1, 1)
        gLayout_orient.addWidget(combo_upAxis, 3, 3, 1, 1)
        gLayout_orient.addItem(spacerStart, 2, 0, 1, 1)
        gLayout_orient.addItem(spacerEnd, 2, 4, 1, 1)
        gLayout_orient.addWidget(cb_orient2World, 1, 2, 1, 1)
        gLayout_orient.addWidget(label_upAxis, 3, 1, 1, 1)
        gLayout_orient.addWidget(combo_worldUpAxis, 4, 3, 1, 1)
        gLayout_orient.addWidget(combo_aimAxis, 2, 3, 1, 1)
        gLayout_orient.addWidget(label_worldUpAxis, 4, 1, 1, 1)
        gLayout_orient.addWidget(label_aimAxis, 2, 1, 1, 1)
        gLayout_orient.addLayout(hLayout_upAxis, 3, 2, 1, 1)

        spacerEnd = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        spacerStart = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        gLayout_tweak = QtWidgets.QGridLayout()
        gLayout_tweak.addWidget(label_x, 0, 1, 1, 1)
        gLayout_tweak.addWidget(le_z, 2, 2, 1, 1)
        gLayout_tweak.addWidget(le_y, 1, 2, 1, 1)
        gLayout_tweak.addWidget(label_y, 1, 1, 1, 1)
        gLayout_tweak.addWidget(le_x, 0, 2, 1, 1)
        gLayout_tweak.addWidget(label_z, 2, 1, 1, 1)
        gLayout_tweak.addItem(spacerEnd, 0, 6, 1, 1)
        gLayout_tweak.addItem(spacerStart, 0, 0, 1, 1)
        gLayout_tweak.addWidget(pb_minusX, 0, 3, 1, 1)
        gLayout_tweak.addWidget(pb_plusX, 0, 4, 1, 1)
        gLayout_tweak.addWidget(pb_minusY, 1, 3, 1, 1)
        gLayout_tweak.addWidget(pb_plusY, 1, 4, 1, 1)
        gLayout_tweak.addWidget(pb_minusZ, 2, 3, 1, 1)
        gLayout_tweak.addWidget(pb_plusZ, 2, 4, 1, 1)

        line_1 = QtWidgets.QFrame()
        line_1.setFrameShape(QtWidgets.QFrame.HLine)
        line_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        line_2 = QtWidgets.QFrame()
        line_2.setFrameShape(QtWidgets.QFrame.HLine)
        line_2.setFrameShadow(QtWidgets.QFrame.Sunken)

        spacerStart = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        spacerEnd = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        hLayout_insert = QtWidgets.QHBoxLayout()
        hLayout_insert.setContentsMargins(0, -1, 0, -1)
        hLayout_insert.addItem(spacerStart)
        hLayout_insert.addWidget(label_insertJoints)
        hLayout_insert.addWidget(le_insertJoints)
        hLayout_insert.addWidget(pb_insertJoints)
        hLayout_insert.addItem(spacerEnd)

        mainLayout.addWidget(pb_toggle)
        mainLayout.addLayout(gLayout_orient)
        mainLayout.addWidget(pb_orientJoints)
        mainLayout.addWidget(pb_planarOrientJoints)
        mainLayout.addWidget(line_1)
        mainLayout.addLayout(gLayout_tweak)
        mainLayout.addWidget(line_2)
        mainLayout.addLayout(hLayout_insert)
        mainLayout.addWidget(pb_copyJointOrient)
        mainLayout.addWidget(pb_turnOffLRA)
        mainLayout.setStretch(0, 1)

        self.data = {
            'buttons': {
                'toggle': pb_toggle,
                'orientJoints': pb_orientJoints,
                'planarOrientJoints': pb_planarOrientJoints,
                'minusX': pb_minusX,
                'plusX': pb_plusX,
                'minusY': pb_minusY,
                'plusY': pb_plusY,
                'minusZ': pb_minusZ,
                'plusZ': pb_plusZ,
                'insertJoints': pb_insertJoints,
                'copyJointOrient': pb_copyJointOrient,
                'turnOffLRA': pb_turnOffLRA
            },
            'radio': {
                'worldUpAxisX': rb_worldUpAxisX,
                'worldUpAxisY': rb_worldUpAxisY,
                'worldUpAxisZ': rb_worldUpAxisZ,
                'aimAxisX': rb_aimAxisX,
                'aimAxisY': rb_aimAxisY,
                'aimAxisZ': rb_aimAxisZ,
                'upAxisX': rb_upAxisX,
                'upAxisY': rb_upAxisY,
                'upAxisZ': rb_upAxisZ
            },
            'rbg': {
                'worldUpAxis': rbg_worldUpAxis,
                'aimAxis': rbg_aimAxis,
                'upAxis': rbg_upAxis
            },
            'checkbox': {
                'orientChildren': cb_orientChildren,
                'orient2World': cb_orient2World
            },
            'combo': {
                'upAxis': combo_upAxis,
                'aimAxis': combo_aimAxis,
                'worldUpAxis': combo_worldUpAxis
            },
            'lineedit': {
                'x': le_x,
                'y': le_y,
                'z': le_z,
                'insertJoints': le_insertJoints
            }
        }

    def initialize(self):
        # add validators
        self.data['lineedit']['x'].setValidator(QtGui.QDoubleValidator(0, 180, 2))
        self.data['lineedit']['y'].setValidator(QtGui.QDoubleValidator(0, 180, 2))
        self.data['lineedit']['z'].setValidator(QtGui.QDoubleValidator(0, 180, 2))

        self.data['lineedit']['insertJoints'].setValidator(QtGui.QIntValidator(1, 100))

        # set button id in buttongroups
        self.data['rbg']['aimAxis'].setId(self.data['radio']['aimAxisX'], 1)
        self.data['rbg']['aimAxis'].setId(self.data['radio']['aimAxisY'], 2)
        self.data['rbg']['aimAxis'].setId(self.data['radio']['aimAxisZ'], 3)
        self.data['rbg']['upAxis'].setId(self.data['radio']['upAxisX'], 4)
        self.data['rbg']['upAxis'].setId(self.data['radio']['upAxisY'], 5)
        self.data['rbg']['upAxis'].setId(self.data['radio']['upAxisZ'], 6)
        self.data['rbg']['worldUpAxis'].setId(self.data['radio']['worldUpAxisX'], 1)
        self.data['rbg']['worldUpAxis'].setId(self.data['radio']['worldUpAxisY'], 2)
        self.data['rbg']['worldUpAxis'].setId(self.data['radio']['worldUpAxisZ'], 3)

    def setDefault(self):
        # default setting
        self.data['radio']['aimAxisY'].setChecked(True)
        self.data['radio']['upAxisX'].setChecked(True)
        self.data['radio']['worldUpAxisY'].setChecked(True)

        self.data['checkbox']['orientChildren'].setChecked(True)

        self.data['lineedit']['x'].setText('90')
        self.data['lineedit']['y'].setText('90')
        self.data['lineedit']['z'].setText('90')

        self.data['lineedit']['insertJoints'].setText('1')

    def setupSlots(self):
        self.data['buttons']['toggle'].clicked.connect(jo.toggleLRAVisibility)
        self.data['buttons']['orientJoints'].released.connect(self.orientJoints)
        self.data['buttons']['planarOrientJoints'].released.connect(self.planarOrient)
        self.data['buttons']['plusX'].released.connect(self.tweakPlusX)
        self.data['buttons']['minusX'].released.connect(self.tweak_minusX)
        self.data['buttons']['plusY'].released.connect(self.tweakPlusY)
        self.data['buttons']['minusY'].released.connect(self.tweak_minusY)
        self.data['buttons']['plusZ'].released.connect(self.tweakPlusZ)
        self.data['buttons']['minusZ'].released.connect(self.tweak_minusZ)
        self.data['buttons']['insertJoints'].released.connect(self.insertJoints)
        self.data['buttons']['copyJointOrient'].released.connect(jo.orientTo)

        self.data['checkbox']['orient2World'].stateChanged.connect(self.is2World)

        self.data['rbg']['aimAxis'].buttonClicked[int].connect(self.checkAxis)
        self.data['rbg']['upAxis'].buttonClicked[int].connect(self.checkAxis)

        self.data['buttons']['turnOffLRA'].released.connect(jo.turnOffLRA)

    # ------- functions ------- #
    def is2World(self):
        """
        Enable / disable radio buttons according to user selection.
        """
        if self.data['checkbox']['orient2World'].isChecked():
            # disable / hide
            for key in self.data['radio']:
                self.data['radio'][key].setEnabled(0)
        else:
            # enable / show
            for key in self.data['radio']:
                self.data['radio'][key].setEnabled(1)

    def checkAxis(self, id):
        """
        Make sure aimAxis and upAxis are different.
        Args:
            id: Id of the active radio button.
        Returns:
            None.
        """
        aimId = self.data['rbg']['aimAxis'].checkedId()
        upId = self.data['rbg']['upAxis'].checkedId()
        
        if (upId - aimId) != 3:
            return
        if id <= 3:
            newId = (id + 1) % 3 + 4
            newBtn = self.data['rbg']['upAxis'].button(newId)
            newBtn.setChecked(True)
        elif id > 3:
            newId = id % 3 + 1
            newBtn = self.data['rbg']['aimAxis'].button(newId)
            newBtn.setChecked(True)

    def orientJoints(self):
        """
        Call back function, collecting user input for orienting joints.
        """
        isChildren = self.data['checkbox']['orientChildren'].isChecked()
        isToWorld = self.data['checkbox']['orient2World'].isChecked()

        if isToWorld:
            cmds.joint(edit=1, oj='none', ch=isChildren, zso=1)
            return

        aimAxis = self.getAxisVector(self.data['rbg']['aimAxis'], self.data['combo']['aimAxis'])
        upAxis = self.getAxisVector(self.data['rbg']['upAxis'], self.data['combo']['upAxis'])
        worldUpAxis = self.getAxisVector(self.data['rbg']['worldUpAxis'], self.data['combo']['worldUpAxis'])

        sel = cmds.ls(sl=1, l=1, type='joint')
        for jnt in sel:
            children = []
            if isChildren:
                children = cmds.listRelatives(jnt, allDescendents=1, pa=1, type='joint')
                if not children:
                    children = []
                children.reverse()
            joints = [jnt] + children
            jo.orientJoint(joints, aimAxis, upAxis, worldUpAxis)

    def tweakPlusX(self):
        v = self.data['lineedit']['x'].text()
        jo.orientTweak(float(v), 'x', '+')

    def tweak_minusX(self):
        v = self.data['lineedit']['x'].text()
        jo.orientTweak(float(v), 'x', '-')

    def tweakPlusY(self):
        v = self.data['lineedit']['y'].text()
        jo.orientTweak(float(v), 'y', '+')

    def tweak_minusY(self):
        v = self.data['lineedit']['y'].text()
        jo.orientTweak(float(v), 'y', '-')

    def tweakPlusZ(self):
        v = self.data['lineedit']['z'].text()
        jo.orientTweak(float(v), 'z', '+')

    def tweak_minusZ(self):
        v = self.data['lineedit']['z'].text()
        jo.orientTweak(float(v), 'z', '-')

    def insertJoints(self):
        v = self.data['lineedit']['insertJoints'].text()
        jo.insertJoints(int(v))

    def planarOrient(self):
        """
        Call back function, orienting joints in their plane.
        """
        joints = cmds.ls(sl=1, l=1, type='joint')
        aimAxis = self.getAxisVector(self.data['rbg']['aimAxis'], self.data['combo']['aimAxis'])
        upAxis = self.getAxisVector(self.data['rbg']['upAxis'], self.data['combo']['upAxis'])

        jo.planarOrient(joints, aimAxis, upAxis)

    def getAxisVector(self, rbg, combo):
        """
        Convert UI input to a vector3.
        """
        factor = combo.currentIndex()
        if factor == 0:
            factor = 1
        elif factor == 1:
            factor = -1
        checkedBtn = rbg.checkedButton()
        axis = checkedBtn.text()
        if axis == 'x':
            return [1 * factor, 0, 0]
        elif axis == 'y':
            return [0, 1 * factor, 0]
        elif axis == 'z':
            return [0, 0, 1 * factor]
