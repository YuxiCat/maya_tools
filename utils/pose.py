import json
import maya.cmds as cmds
from utils import attributes, app, log

LOG = log.get_logger(__name__)


def exportPose(exportPath, nodes):
    '''Exports pose data to a json file.
    Args:
        exportPath: The file path where a json file is saved.
        root: The selected nodes to export.

    Returns: True if export succeeds. False if export fails.
    '''
    data = {}
    for node in nodes:
        infoDict = {}
        infoDict['t'] = cmds.xform(node, q=1, r=1, t=1)
        infoDict['ro'] = cmds.xform(node, q=1, r=1, ro=1)
        infoDict['s'] = cmds.xform(node, q=1, r=1, s=1)
        infoDict['sp'] = cmds.xform(node, q=1, sp=1)
        infoDict['rp'] = cmds.xform(node, q=1, rp=1)
        infoDict['roo'] = cmds.xform(node, q=1, roo=1)
        # custom attrs
        customAttrList = cmds.listAttr(node, ud=1)
        if not customAttrList:
            customAttrList = []
        for attr in customAttrList:
            attributes.gatherDict(node, attr)
            infoDict['custom'][attr] = attributes.gatherDict(node, attr)
        data[node] = infoDict

    with open(exportPath, 'w') as outfile:
        try:
            json.dump(data, outfile, sort_keys=True, indent=4)
            LOG.info('Exported pose data to {}.'.format(exportPath))
            return True
        except:
            LOG.error('Unable to export pose data to {0}.'.format(exportPath))
            return False


def importPose(importPath):
    '''Import pose data from a json file.
    Args:
        importPath: The file path where a json file is loaded.

    Returns: True if export succeeds. False if export fails.
    '''
    with open(importPath) as infile:
        try:
            # data = json.load(infile)
            data = app.json_load_byteified(infile)
        except:
            LOG.error('Unable to load skeleton data from {0}.'.format(importPath))
            return False

    for node in data:
        if not cmds.objExists(node):
            LOG.info('{} does not exist in the scene. Skipped for pose restoring.'.format(node))
            continue
        t = data[node]['t']
        ro = data[node]['ro']
        s = data[node]['s']
        sp = data[node]['sp']
        rp = data[node]['rp']
        roo = data[node]['roo']

        cmds.setAttr(node + '.tx', t[0])
        cmds.setAttr(node + '.ty', t[1])
        cmds.setAttr(node + '.tz', t[2])
        cmds.setAttr(node + '.rx', ro[0])
        cmds.setAttr(node + '.ry', ro[1])
        cmds.setAttr(node + '.rz', ro[2])
        cmds.setAttr(node + '.sx', s[0])
        cmds.setAttr(node + '.sy', s[1])
        cmds.setAttr(node + '.sz', s[2])
        cmds.setAttr(node + '.spx', sp[0])
        cmds.setAttr(node + '.spy', sp[1])
        cmds.setAttr(node + '.spz', sp[2])
        cmds.setAttr(node + '.rpx', rp[0])
        cmds.setAttr(node + '.rpy', rp[1])
        cmds.setAttr(node + '.rpz', rp[2])
        if cmds.attributeQuery('roo', node=node, exists=True):
            cmds.setAttr(node + '.roo', roo)
        # custom attrs
        if 'custom' in data[node].keys():
            for attr in data[node]['custom']:
                attributes.restoreAttr(node, attr, data[node]['custom'][attr])

    LOG.info('Imported pose data from {}.'.format(importPath))
    return True