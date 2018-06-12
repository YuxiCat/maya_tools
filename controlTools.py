#
# EXAMPLE RUN CODE
#
# import controlTools
# reload(controlTools)
# controlTools.show()

import sys, os
import maya.cmds as cmds
from vendor.Qt import QtGui, QtWidgets, QtCore
from utils import controls as ctrls
reload(ctrls)


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
    win = control_Dialog()
    win.setFixedSize(320, 350)
    win.show()


class control_Dialog(QtWidgets.QDialog):
    def __init__(self):
        super(control_Dialog, self).__init__()

        self.setupUi()
        self.initialize()
        self.setupSlots()
        self.setDefault()
        self.setWindowTitle("Control Factory")
        self.setWindowFlags(self.windowFlags() |
                      QtCore.Qt.WindowMaximizeButtonHint |
                      QtCore.Qt.WindowMinimizeButtonHint |
                      QtCore.Qt.WindowCloseButtonHint |
                      QtCore.Qt.Window |
                      QtCore.Qt.WindowStaysOnTopHint |
                      WINTYPE)

    # ------- setup ------- #
    def setupUi(self):
        self.setObjectName("controlFactory")

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        # layouts
        mainLayout = QtWidgets.QVBoxLayout(self)
        vLayout_addCurve = QtWidgets.QVBoxLayout()
        hLayout_addCurve = QtWidgets.QHBoxLayout()
        vLayout_copyCurve = QtWidgets.QVBoxLayout()
        hLayout_copyCurve = QtWidgets.QHBoxLayout()
        vLayout_removeCurve = QtWidgets.QVBoxLayout()
        hLayout_removeCurve = QtWidgets.QHBoxLayout()
        vLayout_color = QtWidgets.QVBoxLayout()
        hLayout_color = QtWidgets.QHBoxLayout()
        vLayout_scale = QtWidgets.QVBoxLayout()
        hLayout_scale = QtWidgets.QHBoxLayout()
        vLayout_tweak = QtWidgets.QVBoxLayout()
        hLayout_tweak = QtWidgets.QHBoxLayout()
        vLayout_addGroups = QtWidgets.QVBoxLayout()
        hLayout_addOffsetGroups = QtWidgets.QHBoxLayout()

        vLayout_addCurve.addLayout(hLayout_addCurve)
        vLayout_copyCurve.addLayout(hLayout_copyCurve)
        vLayout_removeCurve.addLayout(hLayout_removeCurve)
        vLayout_color.addLayout(hLayout_color)
        vLayout_scale.addLayout(hLayout_scale)
        vLayout_tweak.addLayout(hLayout_tweak)
        vLayout_addGroups.addLayout(hLayout_addOffsetGroups)

        # buttons
        pb_addCurve = QtWidgets.QPushButton()
        pb_copyCurve = QtWidgets.QPushButton()
        pb_copyShapes = QtWidgets.QPushButton("Copy ControlShapes")
        pb_removeCurve = QtWidgets.QPushButton()
        pb_removeShapes = QtWidgets.QPushButton("Remove ControlShapes")
        pb_color = QtWidgets.QPushButton()
        pb_scale = QtWidgets.QPushButton()
        pb_tweak = QtWidgets.QPushButton()
        pb_addOffsetGroups = QtWidgets.QPushButton()
        pb_addGroups = QtWidgets.QPushButton("Add zero grp")
        pb_N = QtWidgets.QPushButton("N")
        pb_R = QtWidgets.QPushButton("R")
        pb_T = QtWidgets.QPushButton("T")
        pb_default = QtWidgets.QPushButton("X")
        pb_plusX = QtWidgets.QPushButton("+")
        pb_minusX = QtWidgets.QPushButton("-")
        pb_plusY = QtWidgets.QPushButton("+")
        pb_minusY = QtWidgets.QPushButton("-")
        pb_plusZ = QtWidgets.QPushButton("+")
        pb_minusZ = QtWidgets.QPushButton("-")
        pb_scaleDown = QtWidgets.QPushButton("-")
        pb_scaleUp = QtWidgets.QPushButton("+")
        pb_N.setSizePolicy(sizePolicy)
        pb_R.setSizePolicy(sizePolicy)
        pb_T.setSizePolicy(sizePolicy)
        pb_default.setSizePolicy(sizePolicy)

        pb_addCurve.setMaximumSize(QtCore.QSize(25, 25))
        pb_copyCurve.setMaximumSize(QtCore.QSize(25, 25))
        pb_removeCurve.setMaximumSize(QtCore.QSize(25, 25))
        pb_color.setMaximumSize(QtCore.QSize(25, 25))
        pb_scale.setMaximumSize(QtCore.QSize(25, 25))
        pb_tweak.setMaximumSize(QtCore.QSize(25, 25))
        pb_addOffsetGroups.setMaximumSize(QtCore.QSize(25, 25))
        pb_plusX.setMaximumSize(QtCore.QSize(30, 16777215))
        pb_minusX.setMaximumSize(QtCore.QSize(30, 16777215))
        pb_plusY.setMaximumSize(QtCore.QSize(30, 16777215))
        pb_minusY.setMaximumSize(QtCore.QSize(30, 16777215))
        pb_minusZ.setMaximumSize(QtCore.QSize(30, 16777215))
        pb_plusZ.setMaximumSize(QtCore.QSize(30, 16777215))
        pb_scaleDown.setMaximumSize(QtCore.QSize(30, 16777215))
        pb_scaleUp.setMaximumSize(QtCore.QSize(30, 16777215))
        pb_addCurve.setMinimumSize(QtCore.QSize(25, 25))
        pb_copyCurve.setMinimumSize(QtCore.QSize(25, 25))
        pb_removeCurve.setMinimumSize(QtCore.QSize(25, 25))
        pb_color.setMinimumSize(QtCore.QSize(25, 25))
        pb_scale.setMinimumSize(QtCore.QSize(25, 25))
        pb_tweak.setMinimumSize(QtCore.QSize(25, 25))
        pb_addOffsetGroups.setMinimumSize(QtCore.QSize(25, 25))

        # labels
        label_addCurve = QtWidgets.QLabel("Add Control Curve")
        label_addCurve.setFrameShape(QtWidgets.QFrame.NoFrame)
        label_copyCurve = QtWidgets.QLabel("Copy Control Curve")
        label_removeCurve = QtWidgets.QLabel("Remove Control Curve(s)")
        label_color = QtWidgets.QLabel("Color")
        label_scale = QtWidgets.QLabel("Scale")
        label_minScale = QtWidgets.QLabel("Min")
        label_maxScale = QtWidgets.QLabel("Max")
        label_title = QtWidgets.QLabel("Value")
        label_sliderValue = QtWidgets.QLabel("")
        label_rotation = QtWidgets.QLabel("Rotation")
        label_rtX = QtWidgets.QLabel("Rotate X")
        label_rtY = QtWidgets.QLabel("Rotate Y")
        label_rtZ = QtWidgets.QLabel("Rotate Z")
        label_addGroups = QtWidgets.QLabel("Add offset groups")
        label_minScale.setAlignment(QtCore.Qt.AlignCenter)
        label_maxScale.setAlignment(QtCore.Qt.AlignCenter)

        # minimize widgets
        widget_addCurve = QtWidgets.QWidget()
        widget_copy = QtWidgets.QWidget()
        widget_remove = QtWidgets.QWidget()
        widget_color = QtWidgets.QWidget()
        widget_scale = QtWidgets.QWidget()
        widget_tweak = QtWidgets.QWidget()
        widget_addGroups = QtWidgets.QWidget()

        vLayout_addCurve.addWidget(widget_addCurve)
        vLayout_copyCurve.addWidget(widget_copy)
        vLayout_removeCurve.addWidget(widget_remove)
        vLayout_color.addWidget(widget_color)
        vLayout_scale.addWidget(widget_scale)
        vLayout_tweak.addWidget(widget_tweak)
        vLayout_addGroups.addWidget(widget_addGroups)

        # checkbox
        cb_shapeOnly = QtWidgets.QCheckBox("ControlShape Only")
        cb_viewport = QtWidgets.QCheckBox("Viewport")
        cb_outliner = QtWidgets.QCheckBox("Outliner")
        cb_nonUniform = QtWidgets.QCheckBox("Non-uniform")
        cb_x = QtWidgets.QCheckBox("x")
        cb_y = QtWidgets.QCheckBox("y")
        cb_z = QtWidgets.QCheckBox("z")
        cb_zero = QtWidgets.QCheckBox("zero")
        cb_sdk = QtWidgets.QCheckBox("sdk")
        cb_offset = QtWidgets.QCheckBox("offset")
        cb_parent = QtWidgets.QCheckBox("parent")

        # line edits
        le_x = QtWidgets.QLineEdit()
        le_y = QtWidgets.QLineEdit()
        le_z = QtWidgets.QLineEdit()
        le_minScale = QtWidgets.QLineEdit()
        le_maxScale = QtWidgets.QLineEdit()
        le_minScale.setMaximumSize(QtCore.QSize(30, 16777215))
        le_maxScale.setMaximumSize(QtCore.QSize(30, 16777215))

        # slider
        hSlider_scaleFactor = QtWidgets.QSlider()

        # spacers
        spacerStart = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        spacerEnd = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        # add buttons to title layouts
        hLayout_addCurve.addWidget(pb_addCurve)
        hLayout_copyCurve.addWidget(pb_copyCurve)
        hLayout_removeCurve.addWidget(pb_removeCurve)
        hLayout_color.addWidget(pb_color)
        hLayout_scale.addWidget(pb_scale)
        hLayout_tweak.addWidget(pb_tweak)
        hLayout_addOffsetGroups.addWidget(pb_addOffsetGroups)

        # add labels to title layouts
        hLayout_addCurve.addWidget(label_addCurve)
        hLayout_copyCurve.addWidget(label_copyCurve)
        hLayout_removeCurve.addWidget(label_removeCurve)
        hLayout_color.addWidget(label_color)
        hLayout_scale.addWidget(label_scale)
        hLayout_tweak.addWidget(label_rotation)
        hLayout_addOffsetGroups.addWidget(label_addGroups)

        # addCurve layout
        vLayout_inner_addCurve = QtWidgets.QVBoxLayout(widget_addCurve)
        gLayout_addCurve = QtWidgets.QGridLayout()
        vLayout_inner_addCurve.addLayout(gLayout_addCurve)
        vLayout_inner_addCurve.addWidget(cb_shapeOnly)

        # copyCurve layout
        vLayout_copy = QtWidgets.QVBoxLayout(widget_copy)
        vLayout_copy.addWidget(pb_copyShapes)

        # removeCurve layout
        vLayout_remove = QtWidgets.QVBoxLayout(widget_remove)
        vLayout_remove.addWidget(pb_removeShapes)

        # color layout
        vLayout_colorWidget = QtWidgets.QVBoxLayout(widget_color)
        gLayout_color = QtWidgets.QGridLayout()
        gLayout_color.addWidget(pb_N, 0, 0, 1, 1)
        gLayout_color.addWidget(pb_R, 0, 2, 1, 1)
        gLayout_color.addWidget(pb_T, 0, 1, 1, 1)
        gLayout_color.addWidget(pb_default, 0, 3, 1, 1)
        hLayout_colorType = QtWidgets.QHBoxLayout()
        hLayout_colorType.addWidget(cb_viewport)
        hLayout_colorType.addWidget(cb_outliner)
        vLayout_colorWidget.addLayout(hLayout_colorType)
        vLayout_colorWidget.addLayout(gLayout_color)

        # scale layout
        vLayout_scaleWidget = QtWidgets.QVBoxLayout(widget_scale)
        vLayout_nonUniform = QtWidgets.QVBoxLayout()
        vLayout_nonUniform.addWidget(cb_nonUniform)
        hLayout_nonUniform = QtWidgets.QHBoxLayout()
        hLayout_nonUniform.setContentsMargins(30, -1, -1, -1)
        hLayout_nonUniform.addWidget(cb_x)
        hLayout_nonUniform.addWidget(cb_y)
        hLayout_nonUniform.addWidget(cb_z)
        vLayout_nonUniform.addLayout(hLayout_nonUniform)
        hLayout_upDown = QtWidgets.QHBoxLayout()
        vLayout_scaleFactor = QtWidgets.QVBoxLayout()
        hLayout_scaleFactor = QtWidgets.QHBoxLayout()
        vLayout_min = QtWidgets.QVBoxLayout()
        vLayout_min.addWidget(label_minScale)
        vLayout_min.addWidget(le_minScale)
        hLayout_scaleFactor.addLayout(vLayout_min)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        hLayout_scaleFactor.addItem(spacerItem)
        vLayout_sliderValue = QtWidgets.QVBoxLayout()
        vLayout_sliderValue.addWidget(label_title)
        vLayout_sliderValue.addWidget(label_sliderValue)
        hLayout_scaleFactor.addLayout(vLayout_sliderValue)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        hLayout_scaleFactor.addItem(spacerItem)
        vLayout_max = QtWidgets.QVBoxLayout()
        vLayout_max.addWidget(label_maxScale)
        vLayout_max.addWidget(le_maxScale)
        hLayout_scaleFactor.addLayout(vLayout_max)
        vLayout_scaleFactor.addLayout(hLayout_scaleFactor)
        hSlider_scaleFactor.setMinimum(1)
        hSlider_scaleFactor.setOrientation(QtCore.Qt.Horizontal)
        hSlider_scaleFactor.setTickPosition(QtWidgets.QSlider.NoTicks)
        vLayout_scaleFactor.addWidget(hSlider_scaleFactor)
        hLayout_upDown.addLayout(vLayout_scaleFactor)
        vLayout_btn = QtWidgets.QVBoxLayout()
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        vLayout_btn.addItem(spacer)
        hLayout_btn = QtWidgets.QHBoxLayout()
        hLayout_btn.addWidget(pb_scaleDown)
        hLayout_btn.addWidget(pb_scaleUp)
        vLayout_btn.addLayout(hLayout_btn)
        hLayout_upDown.addLayout(vLayout_btn)
        vLayout_scaleWidget.addLayout(vLayout_nonUniform)
        vLayout_scaleWidget.addLayout(hLayout_upDown)

        # tweak layout
        gLayout_tweak = QtWidgets.QGridLayout(widget_tweak)
        gLayout_tweak.addItem(spacerStart, 0, 0, 1, 1)
        gLayout_tweak.addWidget(pb_plusX, 0, 4, 1, 1)
        gLayout_tweak.addWidget(le_x, 0, 2, 1, 1)
        gLayout_tweak.addWidget(pb_minusX, 0, 3, 1, 1)
        gLayout_tweak.addWidget(label_rtX, 0, 1, 1, 1)
        gLayout_tweak.addItem(spacerEnd, 0, 5, 1, 1)
        gLayout_tweak.addWidget(label_rtY, 1, 1, 1, 1)
        gLayout_tweak.addWidget(label_rtZ, 2, 1, 1, 1)
        gLayout_tweak.addWidget(le_y, 1, 2, 1, 1)
        gLayout_tweak.addWidget(le_z, 2, 2, 1, 1)
        gLayout_tweak.addWidget(pb_minusY, 1, 3, 1, 1)
        gLayout_tweak.addWidget(pb_minusZ, 2, 3, 1, 1)
        gLayout_tweak.addWidget(pb_plusY, 1, 4, 1, 1)
        gLayout_tweak.addWidget(pb_plusZ, 2, 4, 1, 1)

        # add groups layout
        vLayout_addOffsetGroups = QtWidgets.QVBoxLayout(widget_addGroups)
        hLayout_addGroups = QtWidgets.QHBoxLayout()
        hLayout_addGroups.addWidget(cb_zero)
        hLayout_addGroups.addWidget(cb_sdk)
        hLayout_addGroups.addWidget(cb_offset)
        hLayout_addGroups.addWidget(cb_parent)
        vLayout_addOffsetGroups.addLayout(hLayout_addGroups)
        vLayout_addOffsetGroups.addWidget(pb_addGroups)

        line_1 = QtWidgets.QFrame()
        line_1.setFrameShape(QtWidgets.QFrame.HLine)
        line_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        line_2 = QtWidgets.QFrame()
        line_2.setFrameShape(QtWidgets.QFrame.HLine)
        line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        line_3 = QtWidgets.QFrame()
        line_3.setFrameShape(QtWidgets.QFrame.HLine)
        line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        line_4 = QtWidgets.QFrame()
        line_4.setFrameShape(QtWidgets.QFrame.HLine)
        line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        line_5 = QtWidgets.QFrame()
        line_5.setFrameShape(QtWidgets.QFrame.HLine)
        line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        line_6 = QtWidgets.QFrame()
        line_6.setFrameShape(QtWidgets.QFrame.HLine)
        line_6.setFrameShadow(QtWidgets.QFrame.Sunken)

        mainLayout.addLayout(vLayout_addCurve)
        mainLayout.addWidget(line_1)
        mainLayout.addLayout(vLayout_copyCurve)
        mainLayout.addWidget(line_2)
        mainLayout.addLayout(vLayout_removeCurve)
        mainLayout.addWidget(line_3)
        mainLayout.addLayout(vLayout_color)
        mainLayout.addWidget(line_4)
        mainLayout.addLayout(vLayout_scale)
        mainLayout.addWidget(line_5)
        mainLayout.addLayout(vLayout_tweak)
        mainLayout.addWidget(line_6)
        mainLayout.addLayout(vLayout_addGroups)

        self.data = {
            'buttons': {
                'addCurve': pb_addCurve,
                'copyCurve': pb_copyCurve,
                'copyShapes': pb_copyShapes,
                'removeCurve': pb_removeCurve,
                'removeShapes': pb_removeShapes,
                'color': pb_color,
                'scale': pb_scale,
                'tweak': pb_tweak,
                'addOffsetGroups': pb_addOffsetGroups,
                'addGroups': pb_addGroups,
                'N': pb_N,
                'R': pb_R,
                'T': pb_T,
                'X': pb_default,
                'plusX': pb_plusX,
                'minusX': pb_minusX,
                'plusY': pb_plusY,
                'minusY': pb_minusY,
                'plusZ': pb_plusZ,
                'minusZ': pb_minusZ,
                'scaleDown': pb_scaleDown,
                'scaleUp': pb_scaleUp
            },
            'layouts': {
                'addCurve': gLayout_addCurve,
                'color': gLayout_color
            },
            'widgets': {
                'addCurve': widget_addCurve,
                'copy': widget_copy,
                'remove': widget_remove,
                'color': widget_color,
                'scale': widget_scale,
                'tweak': widget_tweak,
                'addGroups': widget_addGroups

            },
            'checkbox': {
                'shapeOnly': cb_shapeOnly,
                'viewport': cb_viewport,
                'outliner': cb_outliner,
                'nonUniform': cb_nonUniform,
                'x': cb_x,
                'y': cb_y,
                'z': cb_z,
                'zero': cb_zero,
                'sdk': cb_sdk,
                'offset': cb_offset,
                'parent': cb_parent
            },
            'lineedit': {
                'x': le_x,
                'y': le_y,
                'z': le_z,
                'minScale': le_minScale,
                'maxScale': le_maxScale
            },
            'slider': {
                'scale': hSlider_scaleFactor
            },
            'label': {
                'slider': label_sliderValue
            }
        }

    def initialize(self):
        # add validators
        self.data['lineedit']['x'].setValidator(QtGui.QDoubleValidator(0, 180, 2))
        self.data['lineedit']['y'].setValidator(QtGui.QDoubleValidator(0, 180, 2))
        self.data['lineedit']['z'].setValidator(QtGui.QDoubleValidator(0, 180, 2))

        self.data['lineedit']['minScale'].setValidator(QtGui.QDoubleValidator(1.0, 100, 2))
        self.data['lineedit']['maxScale'].setValidator(QtGui.QDoubleValidator(1.0, 100, 2))

        # add buttons - add control curve
        dirs = os.listdir(ctrls.CONTROLS_DIRECTORY)
        col = 6
        row = 0
        count = 0
        self.mapperAddCurve = QtCore.QSignalMapper()
        for fileName in dirs:
            if fileName.endswith('.json'):
                if count == 6:
                    count = 0
                    row += 1
                btn = QtWidgets.QPushButton()
                btn.setToolTip(fileName)
                iconName = fileName.replace('.json', '.png')
                if iconName in dirs:
                    iconPath = os.path.join(ctrls.CONTROLS_DIRECTORY, iconName)
                    btn.setIcon(QtGui.QIcon(iconPath))
                    btn.setIconSize(QtCore.QSize(30, 30))
                self.data['layouts']['addCurve'].addWidget(btn, row, count)
                count += 1
                self.mapperAddCurve.setMapping(btn, fileName)
                btn.clicked.connect(self.mapperAddCurve.map)
        self.mapperAddCurve.mapped['QString'].connect(self.addCtrlShape)

        # add buttons - color
        self.mapperColor = QtCore.QSignalMapper()
        col = 8
        row = 0
        count = 4
        for i in xrange(1, 32):
            if count == col:
                count = 0
                row += 1
            rgb = cmds.colorIndex(i, q=True)
            r, g, b = rgb[0], rgb[1], rgb[2]
            btn = QtWidgets.QPushButton()
            btn.btnIndex = count
            btn.setAutoFillBackground(True)
            values = "{r}, {g}, {b}, {a}".format(r=r * 255, g=g * 255, b=b * 255, a = 255)
            btn.setStyleSheet("QPushButton { background-color: rgba(" + values + "); }")
            self.data['layouts']['color'].addWidget(btn, row, count)
            count += 1
            self.mapperColor.setMapping(btn, i)
            btn.clicked.connect(self.mapperColor.map)
        self.mapperColor.mapped['int'].connect(self.colorShapes)

    def setDefault(self):
        # default setting
        self.data['checkbox']['shapeOnly'].setChecked(True)
        self.data['checkbox']['viewport'].setChecked(True)

        self.data['checkbox']['nonUniform'].setChecked(False)

        self.data['checkbox']['x'].setEnabled(False)
        self.data['checkbox']['y'].setEnabled(False)
        self.data['checkbox']['z'].setEnabled(False)
        self.data['checkbox']['x'].setChecked(False)
        self.data['checkbox']['y'].setChecked(False)
        self.data['checkbox']['z'].setChecked(False)

        self.data['lineedit']['x'].setText('90')
        self.data['lineedit']['y'].setText('90')
        self.data['lineedit']['z'].setText('90')

        self.data['lineedit']['minScale'].setText('1')
        self.data['lineedit']['maxScale'].setText('2')

        self.data['slider']['scale'].setMinimum(100)
        self.data['slider']['scale'].setMaximum(200)
        self.data['slider']['scale'].setValue(120)

        self.data['checkbox']['zero'].setChecked(True)
        self.data['checkbox']['sdk'].setChecked(False)
        self.data['checkbox']['offset'].setChecked(False)
        self.data['checkbox']['parent'].setChecked(False)

        # fold all tabs
        self.data['buttons']['addCurve'].click()
        self.data['buttons']['copyCurve'].click()
        self.data['buttons']['removeCurve'].click()
        self.data['buttons']['color'].click()
        self.data['buttons']['scale'].click()
        self.data['buttons']['tweak'].click()
        self.data['buttons']['addOffsetGroups'].click()

    def setupSlots(self):
        self.data['buttons']['copyShapes'].clicked.connect(self.copyCtrlShapes)
        self.data['buttons']['removeShapes'].clicked.connect(self.removeCtrlShape)

        self.data['buttons']['scaleDown'].clicked.connect(self.scaleDown)
        self.data['buttons']['scaleUp'].clicked.connect(self.scaleUp)

        self.data['lineedit']['minScale'].textChanged.connect(self.updateScale)
        self.data['lineedit']['maxScale'].textChanged.connect(self.updateScale)

        self.data['buttons']['N'].released.connect(self.makeNormal)
        self.data['buttons']['T'].released.connect(self.makeTemplate)
        self.data['buttons']['R'].released.connect(self.makeReference)
        self.data['buttons']['X'].released.connect(self.makeDefault)

        self.data['checkbox']['nonUniform'].stateChanged.connect(self.uniformCheck)
        self.data['slider']['scale'].valueChanged.connect(self.updateSliderValue)

        self.data['buttons']['plusX'].released.connect(self.tweakPlusX)
        self.data['buttons']['minusX'].released.connect(self.tweak_minusX)
        self.data['buttons']['plusY'].released.connect(self.tweakPlusY)
        self.data['buttons']['minusY'].released.connect(self.tweak_minusY)
        self.data['buttons']['plusZ'].released.connect(self.tweakPlusZ)
        self.data['buttons']['minusZ'].released.connect(self.tweak_minusZ)

        self.data['buttons']['addGroups'].clicked.connect(self.addGroups)

        # resize
        self.data['buttons']['addCurve'].clicked.connect(self.resizeAddCurve)
        self.data['buttons']['copyCurve'].clicked.connect(self.resizeCopyCurve)
        self.data['buttons']['removeCurve'].clicked.connect(self.resizeRemoveCurve)
        self.data['buttons']['color'].clicked.connect(self.resizeColor)
        self.data['buttons']['scale'].clicked.connect(self.resizeScale)
        self.data['buttons']['tweak'].clicked.connect(self.resizeTweak)
        self.data['buttons']['addOffsetGroups'].clicked.connect(self.resizeAddGroups)

    # ------- functions ------- #
    def addCtrlShape(self, fileName):
        sel = cmds.ls(sl=1, r=1)
        curveName = fileName.split('.')[0]
        parentCurveShape = self.data['checkbox']['shapeOnly'].isChecked()
        # shapeOnly not checked, create a new curve node
        if (not sel) or (not parentCurveShape):
            curves = ctrls.create(curveName, ctrlShape=curveName)
            cmds.select(curves)
        else:
            ctrlList = list()
            for ctrl in sel:
                if cmds.objectType(ctrl, isType='transform') or cmds.objectType(ctrl, isType='joint'):
                    ctrls.addControlShape(ctrl, ctrlShape=curveName)
                    ctrlList.append(ctrl)

                elif cmds.objectType(ctrl, isType='nurbsCurve'):
                    p = cmds.listRelatives(ctrl, p=True, type='transform')[0]
                    cmds.delete(ctrl)
                    ctrls.addControlShape(p, ctrlShape=curveName)
                    ctrlList.append(p)
            cmds.select(ctrlList)
        return

    def copyCtrlShapes(self):
        sel = cmds.ls(sl=1, l=1, type='transform')
        if len(sel) < 2:
            return
        source = sel[0]
        for node in sel[1:]:
            ctrls.removeControl(node)
            ctrls.duplicateShapes(source, node)

    def removeCtrlShape(self):
        sel = cmds.ls(sl=1, l=1, type='transform')
        for ctrl in sel:
            ctrls.removeControl(ctrl)

    def uniformCheck(self):
        if self.data['checkbox']['nonUniform'].isChecked():
            self.data['checkbox']['x'].setEnabled(True)
            self.data['checkbox']['y'].setEnabled(True)
            self.data['checkbox']['z'].setEnabled(True)
        else:
            self.data['checkbox']['x'].setEnabled(False)
            self.data['checkbox']['y'].setEnabled(False)
            self.data['checkbox']['z'].setEnabled(False)

    def scaleDown(self):
        sel = cmds.ls(sl=1, l=1)
        value = self.data['slider']['scale'].value() / 100.0
        scaleX, scaleY, scaleZ = 1.0/value, 1.0/value, 1.0/value
        if self.data['checkbox']['nonUniform'].isChecked():
            if not self.data['checkbox']['x'].isChecked():
                scaleX = 1
            if not self.data['checkbox']['y'].isChecked():
                scaleY = 1
            if not self.data['checkbox']['z'].isChecked():
                scaleZ = 1
        for node in sel:
            ctrls.scaleControl(node, [scaleX, scaleY, scaleZ])
        cmds.select(sel)

    def scaleUp(self):
        sel = cmds.ls(sl=1, l=1)
        value = self.data['slider']['scale'].value() / 100.0
        scaleX, scaleY, scaleZ = value, value, value
        if self.data['checkbox']['nonUniform'].isChecked():
            if not self.data['checkbox']['x'].isChecked():
                scaleX = 1
            if not self.data['checkbox']['y'].isChecked():
                scaleY = 1
            if not self.data['checkbox']['z'].isChecked():
                scaleZ = 1
        for node in sel:
            ctrls.scaleControl(node, [scaleX, scaleY, scaleZ])
        cmds.select(sel)

    def updateScale(self):
        minV = self.data['lineedit']['minScale'].text()
        maxV = self.data['lineedit']['maxScale'].text()
        if minV and maxV:
            self.data['slider']['scale'].setMinimum(float(minV) * 100)
            self.data['slider']['scale'].setMaximum(float(maxV) * 100)

    def updateSliderValue(self):
        v = self.data['slider']['scale'].value() / 100.0
        self.data['label']['slider'].setNum(v)

    def makeNormal(self):
        sel = cmds.ls(sl=1, l=1)
        for node in sel:
            if cmds.objectType(node, isType='nurbsCurve'):
                cmds.setAttr(node + '.overrideEnabled', 1)
                cmds.setAttr(node + '.overrideDisplayType', 0)

            elif cmds.objectType(node, isType='transform') or cmds.objectType(node, isType='joint'):
                shapeList = ctrls.getShape(node)
                for shape in shapeList:
                    cmds.setAttr(shape + '.overrideEnabled', 1)
                    cmds.setAttr(shape + '.overrideDisplayType', 0)

    def makeTemplate(self):
        sel = cmds.ls(sl=1, l=1)
        for node in sel:
            if cmds.objectType(node, isType='nurbsCurve'):
                cmds.setAttr(node + '.overrideEnabled', 1)
                cmds.setAttr(node + '.overrideDisplayType', 1)

            elif cmds.objectType(node, isType='transform') or cmds.objectType(node, isType='joint'):
                shapeList = ctrls.getShape(node)
                for shape in shapeList:
                    cmds.setAttr(shape + '.overrideEnabled', 1)
                    cmds.setAttr(shape + '.overrideDisplayType', 1)

    def makeReference(self):
        sel = cmds.ls(sl=1, l=1)
        for node in sel:
            if cmds.objectType(node, isType='nurbsCurve'):
                cmds.setAttr(node + '.overrideEnabled', 1)
                cmds.setAttr(node + '.overrideDisplayType', 2)

            elif cmds.objectType(node, isType='transform') or cmds.objectType(node, isType='joint'):
                shapeList = ctrls.getShape(node)
                for shape in shapeList:
                    cmds.setAttr(shape + '.overrideEnabled', 1)
                    cmds.setAttr(shape + '.overrideDisplayType', 2)

    def makeDefault(self):
        sel = cmds.ls(sl=1, l=1)
        if self.data['checkbox']['viewport'].isChecked():
            for node in sel:
                ctrls.makeDefault(node)
        if self.data['checkbox']['outliner'].isChecked():
            for node in sel:
                cmds.setAttr(node + '.useOutlinerColor', 0)

    def selectColorCtrls(self, colorIndex):
        # TODO - need to add signal: select controls with a certain color
        cmds.select(cl=1)
        sel = []
        shapes = cmds.ls(type='nurbsCurve')
        for shape in shapes:
            if not cmds.getAttr(shape + '.overrideRGBColors'):
                index = cmds.getAttr(shape + '.overrideColor')
                if index == colorIndex:
                    parent = cmds.listRelatives(shape, p=1)[0]
                    sel.append(parent)
        cmds.select(sel)

    def colorShapes(self, index):
        sel = cmds.ls(sl=1, l=1)
        if self.data['checkbox']['viewport'].isChecked():
            for node in sel:
                ctrls.colorControl(node, index)
        if self.data['checkbox']['outliner'].isChecked():
            for node in sel:
                ctrls.colorOutliner(node, index)

    def tweakPlusX(self):
        v = self.data['lineedit']['x'].text()
        ctrls.orientTweak(float(v), 'x', '+')

    def tweak_minusX(self):
        v = self.data['lineedit']['x'].text()
        ctrls.orientTweak(float(v), 'x', '-')

    def tweakPlusY(self):
        v = self.data['lineedit']['y'].text()
        ctrls.orientTweak(float(v), 'y', '+')

    def tweak_minusY(self):
        v = self.data['lineedit']['y'].text()
        ctrls.orientTweak(float(v), 'y', '-')

    def tweakPlusZ(self):
        v = self.data['lineedit']['z'].text()
        ctrls.orientTweak(float(v), 'z', '+')

    def tweak_minusZ(self):
        v = self.data['lineedit']['z'].text()
        ctrls.orientTweak(float(v), 'z', '-')

    def addGroups(self):
        isZero = self.data['checkbox']['zero'].isChecked()
        isSdk = self.data['checkbox']['sdk'].isChecked()
        isOffset = self.data['checkbox']['offset'].isChecked()
        isParent = self.data['checkbox']['parent'].isChecked()

        sel = cmds.ls(sl=1, l=1, type='transform')
        sel.sort(key=lambda x: len(x), reverse=True)
        for node in sel:
            parentNode = cmds.listRelatives(node, p=True, f=True)
            if parentNode and (type(parentNode) is list):
                parentNode = parentNode[0]
            if isZero:
                grp = cmds.group(em=1, n=node.split('|')[-1] + '_zero_grp')
                pCons = cmds.parentConstraint(node, grp, mo=False)
                cmds.delete(pCons)
                if parentNode:
                    parentNode = cmds.parent(grp, parentNode)[0]
                else:
                    parentNode = grp
            if isSdk:
                grp = cmds.group(em=1, n=node.split('|')[-1] + '_sdk_grp')
                pCons = cmds.parentConstraint(node, grp, mo=False)
                cmds.delete(pCons)
                if parentNode:
                    parentNode = cmds.parent(grp, parentNode)[0]
                else:
                    parentNode = grp
            if isOffset:
                grp = cmds.group(em=1, n=node.split('|')[-1] + '_offset_grp')
                pCons = cmds.parentConstraint(node, grp, mo=False)
                cmds.delete(pCons)
                if parentNode:
                    parentNode = cmds.parent(grp, parentNode)[0]
                else:
                    parentNode = grp
            if isParent:
                grp = cmds.group(em=1, n=node.split('|')[-1] + '_parent_grp')
                pCons = cmds.parentConstraint(node, grp, mo=False)
                cmds.delete(pCons)
                if parentNode:
                    parentNode = cmds.parent(grp, parentNode)[0]
                else:
                    parentNode = grp
            if parentNode:
                cmds.parent(node, parentNode)

    def minimizeWidget(self, widget):
        w = self.width()
        h = self.height()
        widgetHeight = widget.minimumSizeHint().height()
        if widget.isHidden():
            widget.show()
            self.setFixedSize(w, h + widgetHeight)
        else:
            widget.hide()
            self.setFixedSize(w, h - widgetHeight)

    def resizeAddCurve(self):
        self.minimizeWidget(self.data['widgets']['addCurve'])

    def resizeCopyCurve(self):
        self.minimizeWidget(self.data['widgets']['copy'])

    def resizeRemoveCurve(self):
        self.minimizeWidget(self.data['widgets']['remove'])

    def resizeColor(self):
        self.minimizeWidget(self.data['widgets']['color'])

    def resizeScale(self):
        self.minimizeWidget(self.data['widgets']['scale'])

    def resizeTweak(self):
        self.minimizeWidget(self.data['widgets']['tweak'])

    def resizeAddGroups(self):
        self.minimizeWidget(self.data['widgets']['addGroups'])
