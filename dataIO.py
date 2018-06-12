#
# EXAMPLE RUN CODE
#
# import dataIO
# reload(dataIO)
# dataIO.show()

import sys
import os
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from vendor.Qt import QtWidgets, QtCore, __binding__
from utils import skinclusters, controls, channels, sdk, joints, blendshapes, pose, log, app
reload(controls)
reload(skinclusters)
reload(channels)
reload(sdk)
reload(joints)
reload(blendshapes)
reload(pose)
reload(app)


PLATFORM = sys.platform
if 'darwin' in PLATFORM:
    WINTYPE = QtCore.Qt.Tool
else:
    WINTYPE = QtCore.Qt.Window


if __binding__ == 'PySide2':
    from shiboken2 import wrapInstance
if __binding__ == 'PySide':
    from shiboken import wrapInstance


LOG = log.get_logger(__name__)
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils', 'fonts')
JSON_FILTER = ["JSON (*.json)"]
BSHP_FILTER = ["BSHP (*.bshp)"]
IMPORT_STATUS = 'IMPORT'
EXPORT_STATUS = 'EXPORT'
STYLESHEET = '''
* {
    outline: none;
    color: #DDD;
    font-size: 12pt;

    background-position: center center;
    background-repeat: no-repeat;
}

QPushButton {
    width: 57px;
    height: 57px;
    background: #555;
    border: 0px solid #333;
    font-size: 11pt;
    color: white;
}

QPushButton:hover {
    color: white;
    background: #666;
}

QPushButton:checked {
    background-color: rgb(130, 130, 130);
}

QPushButton:disabled {
    color: rgba(255, 255, 255, 50);
}

QPushButton#BrowseButton {
    width: 27px;
    height: 27px;
    border: 0px solid #333;
}

QPushButton#BrowseButton { font-family: "FontAwesome"; }

'''


# Allows converting pointers to Python objects
def maya_main_window():
    main_win_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_win_ptr), QtWidgets.QWidget)


def show():
    global win
    try:
        win.close()
    except: pass
    win = IO_Dialog()
    win.resize(0, 0)
    win.show()


class IO_Dialog(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(IO_Dialog, self).__init__(parent)

        self.setupUi()
        # self.initialize()
        self.setupSlots()
        self.setWindowTitle("dataIO")
        self.setWindowFlags(QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setStyleSheet(STYLESHEET)
        self.nameFilter = JSON_FILTER
        # app.addFonts(FONT_PATH)

    # ------- setup ------- #
    def setupUi(self):
        self.setObjectName("dataIO")

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        pb_import = QtWidgets.QPushButton("Import")  # u'\uf093'
        pb_export = QtWidgets.QPushButton("Export")  # u'\uf0c7'
        hLayout1 = QtWidgets.QHBoxLayout()
        hLayout1.addWidget(pb_import)
        hLayout1.addWidget(pb_export)

        pb_skin = QtWidgets.QPushButton(u'SKIN')
        pb_ctrl = QtWidgets.QPushButton(u'CTRL')
        pb_channel = QtWidgets.QPushButton(u'CH')
        pb_sdk = QtWidgets.QPushButton(u'SDK')
        pb_skeleton = QtWidgets.QPushButton(u'SKEL')
        pb_blendshape = QtWidgets.QPushButton(u'BSHP')
        pb_pose = QtWidgets.QPushButton(u'POSE')
        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.addWidget(pb_skin)
        btnLayout.addWidget(pb_ctrl)
        btnLayout.addWidget(pb_channel)
        btnLayout.addWidget(pb_sdk)
        btnLayout.addWidget(pb_skeleton)
        btnLayout.addWidget(pb_blendshape)
        btnLayout.addWidget(pb_pose)

        le_filepath = QtWidgets.QLineEdit()
        pb_browse = QtWidgets.QPushButton(u'\uf07b')
        le_filepath.setText(cmds.workspace(q=1, rd=1) + 'skin.json')
        hLayout2 = QtWidgets.QHBoxLayout()
        hLayout2.addWidget(le_filepath)
        hLayout2.addWidget(pb_browse)

        pb_apply = QtWidgets.QPushButton(u'APPLY')
        vLayout = QtWidgets.QVBoxLayout()
        vLayout.addWidget(pb_apply)

        mainLayout.addLayout(hLayout1)
        mainLayout.addLayout(btnLayout)
        mainLayout.addLayout(hLayout2)
        mainLayout.addLayout(vLayout)

        w_skin = QtWidgets.QWidget()
        w_ctrl = QtWidgets.QWidget()
        w_channel = QtWidgets.QWidget()
        w_sdk = QtWidgets.QWidget()
        w_skeleton = QtWidgets.QWidget()
        w_blendshape = QtWidgets.QWidget()
        w_pose = QtWidgets.QWidget()
        mainLayout.addWidget(w_skin)
        mainLayout.addWidget(w_ctrl)
        mainLayout.addWidget(w_channel)
        mainLayout.addWidget(w_sdk)
        mainLayout.addWidget(w_skeleton)
        mainLayout.addWidget(w_blendshape)
        mainLayout.addWidget(w_pose)

        # set checkable
        pb_skin.setCheckable(1)
        pb_ctrl.setCheckable(1)
        pb_channel.setCheckable(1)
        pb_sdk.setCheckable(1)
        pb_skeleton.setCheckable(1)
        pb_blendshape.setCheckable(1)
        pb_pose.setCheckable(1)

        pb_import.setCheckable(1)
        pb_export.setCheckable(1)

        # set visible
        w_skin.hide()
        w_ctrl.hide()
        w_channel.hide()
        w_sdk.hide()
        w_skeleton.hide()
        w_pose.hide()

        # name all the important widgets
        names = {
            # Buttons
            "SkinButton": pb_skin,
            "CtrlButton": pb_ctrl,
            "ChannelButton": pb_channel,
            "SDKButton": pb_sdk,
            "SkeletonButton": pb_skeleton,
            "BlendshapeButton": pb_blendshape,
            "PoseButton": pb_pose,
            "ImportButton": pb_import,
            "ExportButton": pb_export,
            "BrowseButton": pb_browse,
            "ApplyButton": pb_apply,

            # LineEdits
            "FilePath": le_filepath,
        }

        for name, w in names.items():
            w.setObjectName(name)

        self.data = {
            'buttons': {
                'import': pb_import,
                'export': pb_export,
                'browse': pb_browse,
                'apply': pb_apply
            },
            'options': {
                'skin': pb_skin,
                'ctrl': pb_ctrl,
                'channel': pb_channel,
                'sdk': pb_sdk,
                'skeleton': pb_skeleton,
                'shp': pb_blendshape,
                'pose': pb_pose
            },
            'lineedits': {
                'browse': le_filepath
            },
            'widgets': {
                'skin': w_skin,
                'ctrl': w_ctrl,
                'channel': w_channel,
                'sdk': w_sdk,
                'skeleton': w_skeleton,
                'shp': w_blendshape,
                'pose': w_pose
            }
        }

    def setupSlots(self):
        self.data['buttons']['import'].clicked.connect(self.connectImport)
        self.data['buttons']['export'].clicked.connect(self.connectExport)

        self.data['options']['skin'].clicked.connect(self.connectSkin)
        self.data['options']['ctrl'].clicked.connect(self.connectCtrl)
        self.data['options']['channel'].clicked.connect(self.connectChannel)
        self.data['options']['sdk'].clicked.connect(self.connectSDK)
        self.data['options']['skeleton'].clicked.connect(self.connectSkeleton)
        self.data['options']['shp'].clicked.connect(self.connectBlendshape)
        self.data['options']['pose'].clicked.connect(self.connectPose)

        # init connections
        self.data['buttons']['export'].setChecked(1)
        self.data['options']['skin'].setChecked(1)
        self.connectExport()
        self.updateApplyConnection()

    def updateApplyConnection(self):
        # disconnect
        try:
            self.data['buttons']['apply'].clicked.disconnect()
        except Exception:
            pass
        btnName = self.getOperationButton()
        status = self.getImportExportStatus()
        if status == IMPORT_STATUS:
            if btnName == 'skin':
                self.data['buttons']['apply'].clicked.connect(self.importSkinweight)
            elif btnName == 'ctrl':
                self.data['buttons']['apply'].clicked.connect(self.importCtrl)
            elif btnName == 'channel':
                self.data['buttons']['apply'].clicked.connect(self.importChannel)
            elif btnName == 'sdk':
                self.data['buttons']['apply'].clicked.connect(self.importSDK)
            elif btnName == 'skeleton':
                self.data['buttons']['apply'].clicked.connect(self.importSkeleton)
            elif btnName == 'shp':
                self.data['buttons']['apply'].clicked.connect(self.importBlendshape)
            elif btnName == 'pose':
                self.data['buttons']['apply'].clicked.connect(self.importPose)
            else:
                LOG.error('WAT! It exploded from IMTERNAL!')
        elif status == EXPORT_STATUS:
            if btnName == 'skin':
                self.data['buttons']['apply'].clicked.connect(self.exportSkinweight)
            elif btnName == 'ctrl':
                self.data['buttons']['apply'].clicked.connect(self.exportCtrl)
            elif btnName == 'channel':
                self.data['buttons']['apply'].clicked.connect(self.exportChannel)
            elif btnName == 'sdk':
                self.data['buttons']['apply'].clicked.connect(self.exportSDK)
            elif btnName == 'skeleton':
                self.data['buttons']['apply'].clicked.connect(self.exportSkeleton)
            elif btnName == 'shp':
                self.data['buttons']['apply'].clicked.connect(self.exportBlendshape)
            elif btnName == 'pose':
                self.data['buttons']['apply'].clicked.connect(self.exportPose)
            else:
                LOG.error('WAT! It exploded from EXTERNAL!')

    def connectImport(self):
        self.data['buttons']['import'].setChecked(1)
        self.data['buttons']['export'].setChecked(0)
        try:
            self.data['buttons']['browse'].clicked.disconnect()
        except Exception:
            pass
        self.data['buttons']['browse'].clicked.connect(self.importBrowse)
        self.updateApplyConnection()

    def connectExport(self):
        self.data['buttons']['import'].setChecked(0)
        self.data['buttons']['export'].setChecked(1)
        try:
            self.data['buttons']['browse'].clicked.disconnect()
        except Exception:
            pass
        self.data['buttons']['browse'].clicked.connect(self.exportBrowse)
        self.updateApplyConnection()

    def importBrowse(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        dlg.setDirectory(cmds.workspace(q=1, rd=1))
        dlg.setNameFilters(self.nameFilter)
        dlg.exec_()
        filepath = dlg.selectedFiles()[0]
        if self.nameFilter == JSON_FILTER:
            ext = '.json'
        elif self.nameFilter == BSHP_FILTER:
            ext = '.bshp'
        if not filepath.endswith(ext):
            filepath += ext
        self.data['lineedits']['browse'].setText(filepath)

    def exportBrowse(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setDirectory(cmds.workspace(q=1, rd=1))
        dlg.setNameFilters(self.nameFilter)
        dlg.exec_()
        filepath = dlg.selectedFiles()[0]
        if self.nameFilter == JSON_FILTER:
            ext = '.json'
        elif self.nameFilter == BSHP_FILTER:
            ext = '.bshp'
        if not filepath.endswith(ext):
            filepath += ext
        self.data['lineedits']['browse'].setText(filepath)

    def getImportExportStatus(self):
        if self.data['buttons']['import'].isChecked():
            return IMPORT_STATUS
        elif self.data['buttons']['export'].isChecked():
            return EXPORT_STATUS
        else:
            return None

    def getOperationButton(self):
        for name, button in self.data['options'].items():
            if button.isChecked():
                return name

    def connectSkin(self):
        self.reconnectBtn('skin')
        self.updateApplyConnection()

    def connectCtrl(self):
        self.reconnectBtn('ctrl')
        self.updateApplyConnection()

    def connectChannel(self):
        self.reconnectBtn('channel')
        self.updateApplyConnection()

    def connectSDK(self):
        self.reconnectBtn('sdk')
        self.updateApplyConnection()

    def connectSkeleton(self):
        self.reconnectBtn('skeleton')
        self.updateApplyConnection()

    def connectBlendshape(self):
        self.reconnectBtn('shp')
        self.updateApplyConnection()

    def connectPose(self):
        self.reconnectBtn('pose')
        self.updateApplyConnection()

    def reconnectBtn(self, btnName):
        if not self.data['options'][btnName].isChecked():
            self.data['options'][btnName].setChecked(1)
            return
        # clear checked btns
        lastBtn = ''
        for k, v in self.data['options'].items():
            if (k != btnName) and v.isChecked():
                v.setChecked(0)
                lastBtn = k
        # # show / hide widget area
        # for k, v in self.data['widgets'].items():
        #     if (k != btnName):
        #         v.hide()
        #     else:
        #         v.show()

        # update lineedit
        currentPath = self.data['lineedits']['browse'].text()
        if btnName == 'shp':
            ext = '.' + btnName
            self.nameFilter = BSHP_FILTER
        else:
            ext = '.json'
            self.nameFilter = JSON_FILTER
        fileName = currentPath.split('.')[0]
        if fileName.endswith(lastBtn):
            self.data['lineedits']['browse'].setText(fileName.replace(lastBtn, btnName) + ext)

        self.resize(self.sizeHint().width(), self.sizeHint().height())

    def importSkinweight(self):
        '''
        Import skin weights for selected meshes.
        '''
        sel = cmds.ls(sl=1, tr=1)
        meshes = cmds.filterExpand(sel, sm=12)
        if not meshes:
            meshes = []
        filepath = self.data['lineedits']['browse'].text()
        if not os.path.exists(filepath):
            LOG.error('Filepath does not exist. {0}'.format(filepath))
            return
        skinclusters.importSkinWeight(filepath, meshes)

    def importCtrl(self):
        '''
        Import control shapes for ALL control curves from data.
        '''
        filepath = self.data['lineedits']['browse'].text()
        if not os.path.exists(filepath):
            LOG.error('Filepath does not exist. {0}'.format(filepath))
            return
        controls.importControlCurves(filepath)

    def importChannel(self):
        '''
        Import channel status for ALL objects from data.
        Overwrite current status.
        '''
        filepath = self.data['lineedits']['browse'].text()
        if not os.path.exists(filepath):
            LOG.error('Filepath does not exist. {0}'.format(filepath))
            return
        channels.importChannelTags(filepath)

    def importSDK(self):
        '''
        Import set driven keys from json data.
        Overwrite current keys if existing.
        '''
        filepath = self.data['lineedits']['browse'].text()
        if not os.path.exists(filepath):
            LOG.error('Filepath does not exist. {0}'.format(filepath))
            return
        sdk.importSDK(filepath)

    def importSkeleton(self):
        '''
        Import joint skeleton from json data.
        Modify existing joints if already existing in the scene.
        '''
        filepath = self.data['lineedits']['browse'].text()
        if not os.path.exists(filepath):
            LOG.error('Filepath does not exist. {0}'.format(filepath))
            return
        joints.importSkeleton(filepath)

    def importBlendshape(self):
        '''
        Import blendShape from shp data.
        '''
        sel = cmds.ls(sl=1, tr=1)
        if not sel:
            LOG.error('Selection cannot be empty. Please select a mesh to export blendShape node.')
            return
        meshes = cmds.filterExpand(sel, sm=12)
        if not meshes:
            LOG.error('Selection must contain a mesh. Please select a mesh to export blendShape node.')
            return
        elif len(meshes) > 1:
            LOG.error('More than 1 mesh is selected. Please select only one mesh to export blendShape node.')
            return

        meshNode = meshes[0]
        history = cmds.listHistory(meshNode)
        bShp = cmds.ls(meshNode, history, type='blendShape')
        if not bShp:
            LOG.error('No blendShape node found on {}'.format(meshNode))
            return
        elif len(bShp) > 1:
            LOG.error(
                'More than 1 blendShape node is found on {}. Please make sure selected mesh has 1 blendShape node.'.format(
                    meshNode))
            return
        bShp = bShp[0]

        filepath = self.data['lineedits']['browse'].text()
        if not os.path.exists(filepath):
            LOG.error('Filepath does not exist. {0}'.format(filepath))
            return
        blendshapes.importBlendShapes(filepath, bShp)

    def importPose(self):
        '''
        Import pose from json data.
        '''
        filepath = self.data['lineedits']['browse'].text()
        if not os.path.exists(filepath):
            LOG.error('Filepath does not exist. {0}'.format(filepath))
            return
        pose.importPose(filepath)

    def exportSkinweight(self):
        '''
        Export skin weights for selected meshes.
        Select meshes.
        '''
        sel = cmds.ls(sl=1, tr=1)
        meshes = cmds.filterExpand(sel, sm=12)
        if not meshes:
            LOG.error('Selection cannot be empty. Please select meshes to export skinweights.')
            return
        filepath = self.data['lineedits']['browse'].text()
        if not app.isValidPath(filepath):
            LOG.error('Filepath is not valid. {0}'.format(filepath))
            return
        skinclusters.exportSkinWeight(filepath, meshes)

    def exportCtrl(self):
        '''
        Export control shapes for selected control curves.
        Select control curves.
        '''
        sel = cmds.ls(sl=1, tr=1)
        if not sel:
            LOG.error('Selection cannot be empty. Please select control curves to export shapes.')
            return
        filepath = self.data['lineedits']['browse'].text()
        if not app.isValidPath(filepath):
            LOG.error('Filepath is not valid. {0}'.format(filepath))
            return
        # control.importExportControlCurves(filepath, export=True)
        controls.exportControlCurves(filepath)

    def exportChannel(self):
        '''
        Export channel status for selected objects.
        Select any nodes.
        '''
        sel = cmds.ls(sl=1, tr=1)
        if not sel:
            LOG.error('Selection cannot be empty. Please select objects to export channel status.')
            return
        filepath = self.data['lineedits']['browse'].text()
        if not app.isValidPath(filepath):
            LOG.error('Filepath is not valid. {0}'.format(filepath))
            return
        channels.exportChannelTags(filepath)

    def exportSDK(self):
        '''
        Export setDrivenKey data.
        '''
        filepath = self.data['lineedits']['browse'].text()
        if not app.isValidPath(filepath):
            LOG.error('Filepath is not valid. {0}'.format(filepath))
            return
        sdk.exportSDK(filepath)

    def exportSkeleton(self):
        '''
        Export skeleton data.
        Select root joint.
        '''
        sel = cmds.ls(sl=1, type='joint')
        if not sel:
            LOG.error('Selection cannot be empty. Please select root joint to export skeleton data.')
            return
        filepath = self.data['lineedits']['browse'].text()
        if not app.isValidPath(filepath):
            LOG.error('Filepath is not valid. {0}'.format(filepath))
            return
        joints.exportSkeleton(filepath, sel[0])

    def exportBlendshape(self):
        '''
        Export blendshape data.
        Select mesh with blendShape node.
        '''
        sel = cmds.ls(sl=1, tr=1)
        if not sel:
            LOG.error('Selection cannot be empty. Please select a mesh to export blendShape node.')
            return
        meshes = cmds.filterExpand(sel, sm=12)
        if not meshes:
            LOG.error('Selection must contain a mesh. Please select a mesh to export blendShape node.')
            return
        elif len(meshes) > 1:
            LOG.error('More than 1 mesh is selected. Please select only one mesh to export blendShape node.')
            return

        meshNode = meshes[0]
        history = cmds.listHistory(meshNode)
        bShp = cmds.ls(meshNode, history, type='blendShape')
        if not bShp:
            LOG.error('No blendShape node found on {}'.format(meshNode))
            return
        elif len(bShp) > 1:
            LOG.error('More than 1 blendShape node is found on {}. Please make sure selected mesh has 1 blendShape node.'.format(meshNode))
            return
        bShp = bShp[0]
        filepath = self.data['lineedits']['browse'].text()
        if not app.isValidPath(filepath):
            LOG.error('Filepath is not valid. {0}'.format(filepath))
            return
        # if self.data['checkbox']['targets'].isChecked():
        #     exportTarget = 1
        # else:
        #     exportTarget = 0
        blendshapes.exportBlendShapes(filepath, bShp, exportTarget=0)

    def exportPose(self):
        '''
        Export pose data.
        Select controls curves.
        '''
        sel = cmds.ls(sl=1, tr=1)
        if not sel:
            LOG.error('Selection cannot be empty. Please select control curves to export a pose.')
            return
        filepath = self.data['lineedits']['browse'].text()
        if not app.isValidPath(filepath):
            LOG.error('Filepath is not valid. {0}'.format(filepath))
            return
        pose.exportPose(filepath, sel)


