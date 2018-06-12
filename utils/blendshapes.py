import os
import maya.cmds as cmds
import maya.mel as mel
import log

LOG = log.get_logger(__name__)


def exportBlendShapes(exportPath, blendShapeNode, exportTarget=0):
    """Export blendshape targets from blendShape node of baseMesh.
    Args:
        exportPath: If exportTarget = 0, absolute file path to export blendShape node to a .shp file.
                    If exportTarget = 1, directory path to export blendshape targets to .shp files named after target names.
        blendShapeNode: BlendShape node to export.
        exportTarget:
    Returns: True if succeeds. False if fails.
    """
    if exportTarget:
        # find the export dir
        if not os.path.isdir(exportPath):
            exportDir = os.path.dirname(exportPath)
        else:
            exportDir = exportPath

        targets = cmds.listAttr('{}.w'.format(blendShapeNode), m=1)
        for i in range(len(targets)):
            path = os.path.join(exportDir, targets[i] + '.shp')
            exCmd = ('blendShape -edit -export "{}" -exportTarget 0 {} {};'.format(path.replace("\\", "/"), i, blendShapeNode))
            mel.eval(exCmd)
            LOG.info('Exported blendShape target "{}" to {}'.format(targets[i]), path)
    else:
        exCmd = ('blendShape -edit -export "{}" {};'.format(exportPath.replace("\\", "/"), blendShapeNode))
        mel.eval(exCmd)
        LOG.info('Exported blendShape node "{}" to {}'.format(blendShapeNode, exportPath))


def importBlendShapes(importPath, blendShapeNode):
    """Import .shp file to blendShape node.
    The base object to which you want to import the shape file must match the topology (same number of vertices) and name used for the shape file you're going to import.

    Args:
        importPath:
        blendShapeNode:

    Returns:
    """
    exCmd = ('blendShape -edit -import "{}" {};'.format(importPath.replace("\\", "/"), blendShapeNode))
    mel.eval(exCmd)


def restoreBlendShapes(baseMesh, parent='BSHP_GRP'):
    """
    Restore blendshape meshes.

    Args:
        baseMesh: The mesh that has blendshape node on.
        parent: The group where restored meshes are parented under.

    Returns:
    """
    history = cmds.listHistory(baseMesh)
    bShp = cmds.ls(baseMesh, history, type='blendShape')
    if not bShp:
        LOG.error('No blendShape node found on {}'.format(baseMesh))
        return False
    bShp = bShp[0]
    attrList = cmds.aliasAttr(bShp, query=True)

    if not cmds.objExists(parent):
        cmds.group(n=parent, em=1)

    for i in xrange(0, len(attrList), 2):
        cmds.setAttr('{}.{}'.format(bShp, attrList[i]), 0)

    for i in xrange(0, len(attrList), 2):
        cmds.setAttr('{}.{}'.format(bShp, attrList[i]), 1)
        dup = cmds.duplicate(baseMesh, n=attrList[i])[0]
        dup = cmds.parent(dup, parent)[0]
        cmds.xform(dup, t=(0, 0, 0), ro=(0, 0, 0))
        cmds.rename(dup, attrList[i])
        cmds.setAttr('{}.{}'.format(bShp, attrList[i]), 0)
