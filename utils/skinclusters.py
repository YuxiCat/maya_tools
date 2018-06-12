import os
import re
import json
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import log
from vendor.Qt import QtWidgets, QtCore

LOG = log.get_logger(__name__)
# CONSTANTS
PROXYGRP = 'PROXY_SKIN_INFS'


def create(geom, infs, name=None, proxyJnts=True, nw=2, bm=0, sm=0, mi=4):
    """
    Create a skinCluster for a geo with given influence objects.

    Args:
        geom: Target geo.
        infs: A list of influence objects.
        name: SkinCluster name.
        proxyJnts:
        nw: Normalization mode. 0 - none, 1 - interactive, 2 - post
        bm: Binding method. 0 - Closest distance between a joint and a point of the geometry. 1 - Closest distance between a joint, considering the skeleton hierarchy, and a point of the geometry. 2 - Surface heat map diffusion.
        sm: Skinning method. 0 - classical linear skinning. 1 - dual quaternion (volume preserving), 2 - a weighted blend between the two.
        mi: Maximum number of transforms that can influence a point (have non-zero weight for the point) when the skinCluster is first created or a new influence is added. 

    Returns: Created skinCluster.
    """
    if not name:
        name = geom + '_skinCluster'

    if not cmds.objExists(geom):
        LOG.warning('Could not find mesh: "' + geom + '", skipping...')
        return
    infsDup = []
    for inf in infs:
        if not cmds.objExists(inf) and proxyJnts:
            # create a proxy influence so we can still apply weights
            LOG.warning('Could not find influence: "' + inf + '", creating a proxy...')
            if not cmds.objExists(PROXYGRP):
                cmds.createNode('transform', n=PROXYGRP)
            infShortName = inf.split('|')[-1]
            cmds.select(PROXYGRP)
            infName = cmds.joint(n=infShortName)
            infsDup.append(infName)
        else:
            infsDup.append(inf)
    skin = cmds.skinCluster(infsDup, geom, n=name, tsb=True, lw=False, nw=nw, bm=bm, sm=sm, mi=mi)[0]
    return skin


def removeUnusedInfluences(srcSkin):
    """
    Remove unused influences on a skinCluster.

    Args:
        srcSkin: Target skinCluster.

    Returns: The number of removed influence(s).
    """
    removeCount = 0
    infls = cmds.skinCluster(srcSkin, q=True, inf=True)
    wtinfs = cmds.skinCluster(srcSkin, q=True, wi=True)

    # set skinCluster to HasNoEffect so it won't process after each removal
    nodeState = cmds.getAttr(srcSkin + ".nodeState")
    cmds.setAttr(srcSkin + ".nodeState", 1)
    for infl in infls:
        found = False
        for wtinf in wtinfs:
            if wtinf == infl:
                found = True
                break
        if not found:
            # remove the influence since it has no effect
            cmds.skinCluster(srcSkin, e=True, ri=infl)
            removeCount += 1
    # restore the old node state
    cmds.setAttr(srcSkin + ".nodeState", nodeState)
    return removeCount


def getInfluences(src):
    """
    Given a source (geometry or skincluster) return the influences for it.

    Args:
        src: A geometry or skincluster.

    Returns: A string array of the influence objects (joints and transform). None if no skinCluster is found.
    """
    srcSkin = getSkinCluster(src)
    if cmds.objExists(srcSkin):
        return cmds.skinCluster(srcSkin, q=1, inf=1)
    else:
        return None


def getSkinCluster(src):
    """
    Given a source (geometry or skincluster) return skincluster.

    Args:
        src: A geometry or skincluster.

    Returns: Skincluster node.
    """
    if cmds.nodeType(src) == "skinCluster":
        srcSkin = src
    else:
        srcSkin = mel.eval('findRelatedSkinCluster("' + src + '")')
    return srcSkin


def exportSkinWeight(exportPath, meshes, namespace=False):
    """
    Export skinWeights of a list of meshes to a json file.

    Args:
        exportPath: The file path where a json file is saved.
        meshes: A list of mesh nodes.
        namespace: True to export with namespace. False to export without namespace.

    Returns: True if export succeeds. False if export fails.
    """
    data = {}
    if not meshes:
        LOG.error('Meshes input {0} is not valid.'.format(meshes))
        return False

    for mesh in meshes:
        skinCluster = getSkinCluster(mesh)
        if not skinCluster:
            LOG.warning('Mesh {} has no skinCluster, skipping... '.format(mesh))
            continue
        skinNorm = cmds.getAttr('%s.normalizeWeights' % skinCluster)

        # get the MFnSkinCluster for clusterName
        selList = om.MSelectionList()
        selList.add(skinCluster)
        clusterNode = om.MObject()
        selList.getDependNode(0, clusterNode)
        skinFn = oma.MFnSkinCluster(clusterNode)

        # get the MDagPath for all influence
        infDags = om.MDagPathArray()
        skinFn.influenceObjects(infDags)

        # {
        #     "mesh_name": {
        #         "weights": {
        #             "vert id": {
        #                 "influence id": weight,
        #                 "influence id": weight
        #             }
        #         },
        #         "infs": [inf1, inf2, inf3, inf4, ...],
        #         "skinCluster": skinCluster_name
        #     }
        # }

        infIds = {}
        infs = []
        unique = True
        for i in xrange(infDags.length()):
            infPath = infDags[i].partialPathName()
            if '|' in infPath:
                LOG.warning('Influence of {}: "{}" is not have a unique name.'.format(mesh, infDags[i].fullPathName()))
                unique = False
            infId = int(skinFn.indexForInfluenceObject(infDags[i]))
            infIds[infId] = i
            infs.append(infPath)
        if not unique:
            LOG.warning('{} skincluster export is skipped. Please make sure all influence names are unique'.format(mesh))
            continue

        # get the MPlug for the weightList and weights attributes
        wlPlug = skinFn.findPlug('weightList')
        wPlug = skinFn.findPlug('weights')
        wlAttr = wlPlug.attribute()
        wAttr = wPlug.attribute()
        wInfIds = om.MIntArray()

        # progressBar visualization
        total = wlPlug.numElements()
        progressBar = QtWidgets.QProgressBar()
        progressBar.setMinimumSize(QtCore.QSize(450, 40))
        progressBar.setMinimum(1)
        progressBar.setMaximum(total)
        progressBar.setWindowTitle('Exporting skincluster: {}'.format(mesh))
        progressBar.show()
        completed = 0

        weights = {}
        for vId in xrange(wlPlug.numElements()):
            vWeights = {}
            # tell the weights attribute which vertex id it represents
            wPlug.selectAncestorLogicalIndex(vId, wlAttr)

            # get the indice of all non-zero weights for this vert
            wPlug.getExistingArrayAttributeIndices(wInfIds)

            # create a copy of the current wPlug
            infPlug = om.MPlug(wPlug)

            completed += 1
            progressBar.setValue(completed)
            for infId in wInfIds:
                # tell the infPlug it represents the current influence id
                infPlug.selectAncestorLogicalIndex(infId, wAttr)

                # add this influence and its weight to this verts weights
                try:
                    vWeights[infIds[infId]] = infPlug.asDouble()
                except KeyError:
                    # assumes a removed influence
                    pass
            weights[vId] = vWeights

        if namespace:
            meshName = mesh
        else:
            meshName = mesh.split(':')[-1]

        data[meshName] = {'weights': weights, 'infs': infs, 'skinCluster': skinCluster, 'nw': skinNorm}

    with open(exportPath, 'w') as outfile:
        try:
            if data:
                json.dump(data, outfile, sort_keys=True, indent=4)
                LOG.info('Exported skin weights for mesh {0}.'.format(meshes))
                return True
            else:
                LOG.info('No valid skinCluster is found for mesh {0}.'.format(meshes))
                return False
        except:
            LOG.error('Unable to export skinWeight data to {0}.'.format(exportPath))
            return False


def importSkinWeight(importPath, meshes, namespace=False):
    """
    Import skinWeight from a json file, to a list of meshes.
    To a whole mesh, or selected vertices.

    Args:
        filepath: The file path where a json file is loaded.
        meshes: A list of mesh nodes. If [], import all available meshes.
        namespace: True to respect imported namespace data. False to ignore any namespaces.

    Returns: True if import succeeds. False if import fails.
    """

    with open(importPath) as infile:
        try:
            data = json.load(infile)
            LOG.info('Loaded skinWeight data from {0}.'.format(importPath))
        except:
            LOG.error('Unable to load skinWeight data from {0}.'.format(importPath))
            return False

    if not meshes:
        meshes = data.keys()

    for mesh in meshes:
        selectedIndice = []
        selectedVerts = [v.split('.vtx')[-1] for v in cmds.ls(sl=1, fl=1) if (('.vtx' in v) and (mesh in v))]
        for v in selectedVerts:
            id = re.findall('\\d+', v)[0]
            selectedIndice.append(id)

        if namespace:
            if not (mesh in data):
                LOG.warning('Unable to find mesh data for "{0}"'.format(mesh))
                continue
            meshName = mesh
        else:
            shortName = mesh.split(':')[-1]
            meshName = ''
            for m in data.keys():
                if m.split(':')[-1] == shortName:
                    meshName = m
            if not meshName:
                LOG.warning('Unable to find mesh data for "{0}"'.format(shortName))
                continue

        # if mesh is not in current scene, skip
        if not cmds.objExists(meshName):
            continue

        weights = data[meshName]['weights']
        infs = data[meshName]['infs']
        skinClusterName = data[meshName]['skinCluster']
        skinNorm = data[meshName]['nw']

        if cmds.polyEvaluate(mesh, v=1) != len(weights.keys()):
            LOG.warning('Mesh "{0}": Vertex number does not match with the imported skinCluster "{1}"'.format(
                mesh, skinClusterName))

        # progressBar visualization
        total = len(weights.items())
        progressBar = QtWidgets.QProgressBar()
        progressBar.setMinimumSize(QtCore.QSize(450, 40))
        progressBar.setMinimum(1)
        progressBar.setMaximum(total)
        progressBar.setWindowTitle('Importing skincluster: {}'.format(mesh))
        progressBar.show()
        completed = 0

        # vertices selection
        if selectedIndice:
            # get skinCluster
            currentName = getSkinCluster(mesh)
            # check if skinCluster exists
            if not currentName:
                LOG.error('Mesh "{0}": SkinCluster missing selected vertices'.format(mesh))
                return False
            # check the name of skinCluster
            elif currentName != skinClusterName:
                LOG.warning('SkinCluster "{0}": Name does not match with the imported skinCluster "{1}"'.format(currentName, skinClusterName))

            # check the number of influences
            currentInfs = cmds.skinCluster(currentName, q=1, inf=1)
            if len(currentInfs) != len(infs):
                LOG.warning('SkinCluster "{0}": Influence number does not match with the imported skinCluster "{1}"'.format(currentName, skinClusterName))

            # unlock influences used by skincluster
            for inf in infs:
                if not cmds.objExists(inf):
                    LOG.warning('Unable to find influence "{0}"]'.format(inf))
                    continue
                cmds.setAttr('%s.liw' % inf, 0)

            for vertId in selectedIndice:
                if not (vertId in weights):
                    LOG.info('Unable to find weight data for {0}.vtx[{1}]'.format(mesh, vertId))
                    continue
                    # TODO
                    # deal with vertices with missing weight data: missing data for vertId
                    # currently acting awkward
                weightData = weights[vertId]
                wlAttr = '%s.weightList[%s]' % (currentName, vertId)
                completed += 1
                progressBar.setValue(completed)
                for infId, infValue in weightData.items():
                    wAttr = '.weights[%s]' % infId
                    cmds.setAttr(wlAttr + wAttr, infValue)
            return True

        # get skinCluster
        if getSkinCluster(mesh):
            cmds.delete(getSkinCluster(mesh))
        create(mesh, infs, name=skinClusterName, nw=skinNorm)

        # normalize needs turned off for the prune to work
        if skinNorm != 0:
            cmds.setAttr('%s.normalizeWeights' % skinClusterName, 0)
        cmds.skinPercent(skinClusterName, mesh, nrm=False, prw=100)

        # restore normalize setting
        cmds.setAttr('%s.normalizeWeights' % skinClusterName, skinNorm)

        # apply weights
        for vertId, weightData in weights.items():
            wlAttr = '%s.weightList[%s]' % (skinClusterName, vertId)
            completed += 1
            progressBar.setValue(completed)
            for infId, infValue in weightData.items():
                wAttr = '.weights[%s]' % infId
                cmds.setAttr(wlAttr + wAttr, infValue)

    return True