import os
import json
import maya.cmds as cmds
import log

LOG = log.get_logger(__name__)
CONTROLS_DIRECTORY = os.path.join(os.path.dirname(__file__), 'controlShapes')
CTRL_SUFFIX = '_ctrl'


def create(name, parent=None, ctrlType='transform', ctrlShape=None, ctrlAxis=None):
    """
    Create control from node.

    Args:
        name: The name of new control for single creation. List of name strings for multiple control creation.
        parent: The parent node of new control.
        ctrlType: Node type. Set to 'transform' by default.
        ctrlShape: The control shape name.
        ctrlAxis: The normal axis name of the control, such as 'x', or '-z'.

    Returns: String of the newly created control name for single creation, including gimbal controls.
             List of string names of newly created controls for multiple creation, including gimbal controls.
             None if fails to create a control.

    """
    # standardize ctrl name
    if CTRL_SUFFIX in name:
        ctrl = name
    else:
        ctrl = name + CTRL_SUFFIX

    # check parent
    ctrlParent = parent
    ctrl = cmds.createNode(ctrlType, name=ctrl, parent=ctrlParent)

    # Add nurbsCurve shape
    if ctrlShape:
        addControlShape(ctrl, ctrlShape)

    return ctrl


def addControlShape(node, ctrlShape=None):
    """
    Add a specific control shape to a node.

    Args:
        node: Target node.
        ctrlShape: Name string of control shape.

    Returns: Curve name if succeeds. False if fails.

    """
    filepath = os.path.join(CONTROLS_DIRECTORY, ctrlShape + '.json')
    if os.path.exists(filepath):
        fh = open(filepath, 'r')
        curveData = json.load(fh)
        fh.close()
    else:
        LOG.error('Control curve file %s does not exist!' % filepath )
        return False
    return createCurve(curveData, node)


def createCurve(controls, transform=None, cleanAll=False):
    """Create a curve.

    Args:
        controls: A (list of) data dictionary generated from the dump function.
        transform: A transform node to add curveShape to.
        cleanAll: True to delete existing shape before adding new.

    Returns: Curve name.

    """
    if type(controls) is dict:
        controls = [controls]
    for control in controls:
        curve = control['name']
        curveShape = control['shape']

        periodic = control['form'] == 2
        degree = control['degree']
        points = control['cvs']

        if periodic:
            points = points + points[:degree]

        if cmds.objExists(curveShape):
            if cleanAll is True:
                cmds.delete(curveShape)
            curve = cmds.curve(degree=degree, p=points, n="TEMP" + curve, per=periodic, k=control['knots'])
        else:
            curve = cmds.curve(degree=degree, p=points, n=curve, per=periodic, k=control['knots'])
        curveShape = cmds.rename(cmds.listRelatives(curve, shapes=True)[0], curveShape.split('|')[-1])

        if 'parent' in control:
            if cmds.objExists(control['parent']):
                if control['parent'] != cmds.listRelatives(curveShape, parent=True, f=True)[0]:
                    try:
                        cmds.parent(curveShape, control['parent'], relative=True, shape=True)
                        cmds.delete(curve)
                    except:
                        pass

        # parenting
        if (transform and (transform is not cmds.listRelatives(curveShape, p=True, type='transform')[0])):
            try:
                cmds.parent(curveShape, transform, s=1, r=1)
                cmds.delete(curve)
            except:
                pass

        if cmds.objExists(curve):
            cmds.delete(curve, constructionHistory=True)

            cmds.setAttr('{0}.overrideEnabled'.format(curve), control['overrideEnabled'])
            cmds.setAttr('{0}.overrideRGBColors'.format(curve), control['overrideRGBColors'])
            cmds.setAttr('{0}.overrideColorRGB'.format(curve), *control['overrideColorRGB'])
            cmds.setAttr('{0}.overrideColor'.format(curve), control['overrideColor'])

        if cmds.objExists(curveShape):
            cmds.setAttr('{0}.overrideEnabled'.format(curveShape), control['overrideEnabled'])
            cmds.setAttr('{0}.overrideRGBColors'.format(curveShape), control['overrideRGBColors'])
            cmds.setAttr('{0}.overrideColorRGB'.format(curveShape), *control['overrideColorRGB'])
            cmds.setAttr('{0}.overrideColor'.format(curveShape), control['overrideColor'])
    return curve


def exportShapesToJson(node, filepath=None):
    """
    Export control shape to json.

    Args:
        nodes: One of a list of nodes to export.
        filepath: Absolute filepath to export to.

    Returns: NA

    """
    projPath = cmds.workspace(q=True, rd=True)
    if not filepath:
        filepath = projPath

    file_path = os.path.join(filepath, '%s.json' %node)
    curveData = dump(node)

    fh = open(file_path, 'w')
    json.dump(curveData, fh, indent=4)
    fh.close()

    LOG.info('Exported Control Curves to: %s' % file_path )


def importShapesFromJson(filepath, transform=None):
    """
    Import control shape to node.

    Args:
        filepath: The absolute filepath to a json file.
        transform: Target node.

    Returns: Filepath if succeeds. None if fails.

    """
    if os.path.exists(filepath):

        fh = open(filepath, 'r')
        curveData = json.load(fh)
        fh.close()

        # make sure it's a list - some control json files are dicts in a list some are just dicts
        # this deals with that issue
        if type(curveData) != list:
            curveData = [curveData]

        # if the transform already has shapes delete them and create new ones
        if transform:
            shapes = cmds.listRelatives(transform, s=True)
            if shapes:
                for s in shapes:
                    cmds.delete(s)
                    # create_curve(curveData)
        for dataBlock in curveData:
            createCurve(dataBlock, transform)

        LOG.debug('Imported Control Curves from: %s' % filepath)
        return filepath
    else:
        LOG.error('Control curve file %s does not exist!' % filepath)
        return None


def dump(node=None):
    """
    Get a data dictionary representing all the given curves.

    Args:
        node: curve.

    Returns: A json serializable list of dictionaries containing the data required to recreate the curves.

    """
    cmds.delete(node, constructionHistory=True)
    shapes = cmds.listRelatives(node, s=True, f=1)
    if not shapes:
        return False
    endData = []
    for shp in shapes:
        if cmds.nodeType(shp) == 'nurbsCurve':
            shapeData = {
                'name': node,
                'shape': shp,
                'cvs': cmds.getAttr('{0}.cv[*]'.format(shp)),
                'degree': cmds.getAttr('{0}.degree'.format(shp)),
                'form': cmds.getAttr('{0}.form'.format(shp)),
                'xform': cmds.xform(node, q=True, ws=True, matrix=True),
                'knots': getKnots(shp),
                'pivot': cmds.xform(node, q=True, rp=True),

                'overrideEnabled': cmds.getAttr('{0}.overrideEnabled'.format(shp)),
                'overrideRGBColors': cmds.getAttr('{0}.overrideRGBColors'.format(shp)),
                'overrideColorRGB': cmds.getAttr('{0}.overrideColorRGB'.format(shp))[0],
                'overrideColor': cmds.getAttr('{0}.overrideColor'.format(shp)),
            }
            shapeData['parent'] = cmds.ls(node, l=True)[0]
            endData.append(shapeData)

    return endData


def getKnots(curve):
    """
    Gets the list of knots of a curve so it can be recreated.

    Args:
        curve: Curve to query.

    Returns: A list of knot values that can be passed into the curve creation command.

    """
    if not 'nurbsCurve' in cmds.nodeType(curve):
        curve = getShape(curve)
    info = cmds.createNode('curveInfo')
    cmds.connectAttr('{0}.worldSpace'.format(curve), '{0}.inputCurve'.format(info))
    knots = cmds.getAttr('{0}.knots[*]'.format(info))
    cmds.delete(info)
    return knots


def getShape(node, intermediate=False):
    """
    Get the shape node of a transform.
    This is useful if you don't want to have to check if a node is a shape node
    or transform.  You can pass in a shape node or transform and the function
    will return the shape node.

    Args:
        node: The name of the node.
        intermediate: True to get the intermediate shape.

    Returns: The name of the shape node.

    """
    returnShapes = []
    if cmds.nodeType(node) == 'transform' or 'joint':
        shapes = cmds.listRelatives(node, shapes=True, path=True)
        if not shapes:
            shapes = []
        for shape in shapes:
            is_intermediate = cmds.getAttr('%s.intermediateObject' % shape)
            if intermediate and is_intermediate and cmds.listConnections(shape, source=False):
                returnShapes.append(shape)
                # return shape
            elif not intermediate and not is_intermediate:
                returnShapes.append(shape)
                # return shape
        return returnShapes
        if shapes:
            return shapes[0]
    elif cmds.nodeType(node) in ['mesh', 'nurbsCurve', 'nurbsSurface']:
        is_intermediate = cmds.getAttr('%s.intermediateObject' % node)
        if is_intermediate and not intermediate:
            node = cmds.listRelatives(node, parent=True, path=True)[0]
            return getShape(node)
        else:
            return node
    return None


def removeControl(controlTransform):
    """
    Removes any exisiting control curve shapes under the controlTransform

    Args:
        controlTransform: Transform node whose curve shapes are to be removed.
    Returns:
        None.
    Raises:
        Logs error if controlTransform does not exist.

    """
    if cmds.objExists(controlTransform):
        curveShapes = cmds.listRelatives(controlTransform, pa=1, shapes=True, type='nurbsCurve')
        if curveShapes:
            cmds.delete(curveShapes)
            LOG.info('Deleted %s' % curveShapes)
            return True
        else:
            return
    else:
        LOG.error('%s does not exist' % controlTransform)
        return


def duplicateShapes(source, target):
    """
    Copy shapes from one transform node to another.

    Args:
        source: Source of shapes.
        target: Target for shapes.
    Returns:
        None.
    Raises:
        Logs warning if source / target is not transform / joint.

    """
    if not (cmds.objectType(source, isType='joint') or cmds.objectType(source, isType='transform')):
        LOG.warning('Source object needs to be tranform type.')
        return
    elif not (cmds.objectType(target, isType='joint') or cmds.objectType(target, isType='transform')):
        LOG.warning('Target object needs to be tranform type.')
        return

    dup = cmds.duplicate(source, n='ctrlTmp', rc=True)[0]
    controlTempShapes = cmds.listRelatives(dup, s=True)
    for i in range(len(controlTempShapes)):
        cmds.parent(controlTempShapes[i], target, r=True, s=True)
        cmds.select(cl=True)
        if i == 0:
            cmds.rename(controlTempShapes[i], '%sShape' % target)
        if i > 0:
            cmds.rename(controlTempShapes[i], '%sShape%s' % (target, str(i)))
    cmds.delete(dup)


def colorControl(node, index):
    """
    Drawing overrides selected controls.

    Args:
        node: Transform node or nurbsCurve.
        index: Color index.
    Returns:
        None.
    Raises:
        None.

    """
    if cmds.objectType(node, isType='nurbsCurve'):
        cmds.setAttr("{0}.overrideEnabled".format(node), True)
        cmds.setAttr("{0}.overrideColor".format(node), index)

    elif cmds.objectType(node, isType='transform') or cmds.objectType(node, isType='joint'):
        shapeList = getShape(node)
        for shape in shapeList:
            cmds.setAttr("{0}.overrideEnabled".format(shape), True)
            cmds.setAttr("{0}.overrideColor".format(shape), index)


def colorOutliner(node, index):
    """
    Drawing outliner overrides selected controls.

    Args:
        node: Transform node or nurbsCurve.
        index: Color index.
    Returns:
        None.
    Raises:
        None.

    """
    rgb = cmds.colorIndex(index, q=True)
    r, g, b = rgb[0], rgb[1], rgb[2]
    if cmds.objectType(node, isType='nurbsCurve'):
        cmds.setAttr(node + '.useOutlinerColor', 1)
        cmds.setAttr(node + '.outlinerColor', r, g, b)
    elif cmds.objectType(node, isType='transform') or cmds.objectType(node, isType='joint'):
        cmds.setAttr(node + '.useOutlinerColor', 1)
        cmds.setAttr(node + '.outlinerColor', r, g, b)


def makeDefault(node):
    """
    Drawing overrides selected controls to default.

    Args:
        node: Transform node or nurbsCurve.
    Returns:
        None.
    Raises:
        None.

    """
    if cmds.objectType(node, isType='nurbsCurve'):
        cmds.setAttr("{0}.overrideEnabled".format(node), False)
        cmds.setAttr(node + '.overrideDisplayType', 0)

    elif cmds.objectType(node, isType='transform') or cmds.objectType(node, isType='joint'):
        # mc.setAttr("{0}.overrideEnabled".format(node), False)
        shapeList = getShape(node)
        for shape in shapeList:
            cmds.setAttr("{0}.overrideEnabled".format(shape), False)
            cmds.setAttr(shape + '.overrideDisplayType', 0)


def scaleControl(node, scaleVector):
    """
    Scale controlCurve by [x, y, z].
    Adjust controlCurve size of node.

    Args:
        node: Transform / joint / nurbsCurve node.
        scaleVector: Scale vector.
        ocp: Object Center Pivot.
    Returns:
        None.
    Raises:
        Logs warning if node does not exist.
        Logs warning if node is not tranform or nurbsCurve type.
        Logs warning if scaleVector is not a list of three.

    """
    if not cmds.objExists(node):
        LOG.warning(node + ' does not exist.')
        return
    elif not (cmds.objectType(node, isType='transform') or
                cmds.objectType(node, isType='joint') or
                cmds.objectType(node, isType='nurbsCurve')):
        LOG.warning('Input node requires transform, joint or nurbsCurve type.')
        return
    elif len(scaleVector) != 3:
        LOG.warning('Input scaleVector requires a list of three.')
        return

    if cmds.objectType(node, isType='nurbsCurve'):
        cmds.select(cl=1)
        cmds.select(node + '.cv[:]')
        cmds.scale(scaleVector[0], scaleVector[1], scaleVector[2], r=1, ocp=0)
        return

    shapeList = getShape(node)
    for shape in shapeList:
        cmds.select(cl=1)
        cmds.select(shape + '.cv[:]')
        cmds.scale(scaleVector[0], scaleVector[1], scaleVector[2], r=1, ocp=0)


def orientTweak(degree, axis, operator):
    """
    Tweak controlCurve orientation by degree.
    Adjust controlCurve orientation of selected transform nodes by a certain degree.

    Args:
        degree: Rotation value.
        axis: Rotation axis.
        operator: + / -
    Returns:
        None.
    Raises:
        Logs warning if nothing is selected.
        Logs warning if axis input is NOT xyz.
        Logs warning if operator input is NOT +-.

    """
    sel = cmds.ls(sl=1, l=True)
    if len(sel) < 1:
        LOG.warning('Nothing is selected.')
        return

    if operator == '+':
        factor = 1
    elif operator == '-':
        factor = -1
    else:
        LOG.warning('Parameter operator is expecting + / - as input.')
        return

    if (axis in 'x') or (axis in 'X'):
        v = [degree * factor, 0, 0]
    elif (axis in 'y') or (axis in 'Y'):
        v = [0, degree * factor, 0]
    elif(axis in 'z') or (axis in 'Z'):
        v = [0, 0, degree * factor]
    else:
        LOG.warning('Parameter axis is expecting x / y / z as input.')
        return

    for node in sel:
        if cmds.objectType(node, isType='transform') or cmds.objectType(node, isType='joint'):
            shapeList = getShape(node)
            for shape in shapeList:
                cmds.select(cl=1)
                cmds.select(shape + '.cv[:]')
                cmds.rotate(v[0], v[1], v[2], r=1, os=1, fo=1)
        elif cmds.objectType(node, isType='nurbsCurve'):
            cmds.select(cl=1)
            cmds.select(node + '.cv[:]')
            cmds.rotate(v[0], v[1], v[2], r=1, os=1, fo=1)

    cmds.select(sel)


# ------- data IO ------- #
def importControlCurves(filename):
    """
    Use to import curve data to single json file.

    Args:
        filename:  Full or relative path to json curve data file.
    Returns:
        bool

    """
    projPath = cmds.workspace(q=True, rd=True)
    file_path = ''

    if '.json' in filename:
        file_path = os.path.join('%s' % projPath, '{0}'.format(filename))
    else:
        file_path = os.path.join('%s' % projPath, '{0}.json'.format(filename))

    if not os.path.exists(filename):
        filename = file_path

    if os.path.exists(file_path):
        try:
            fh = open(file_path, 'r')
            curveData = json.load(fh)
            fh.close()

            for dataBlock in curveData:
                createCurve(dataBlock, None, True)

            LOG.info('Imported Control Curves to: %s' % file_path)
            return file_path
        except:
            LOG.error('Error importing Control Curves from: %s' % file_path)
            raise
    else:
        LOG.error('Control curve file %s does not exist!' % file_path)
        return


def exportControlCurves(filename):
    """
    Use to export curve data to single json file.

    Args:
        filename:  Full or relative path to json curve data file
    Returns:
        bool

    """
    file_path = ""
    projPath = cmds.workspace(q=True, rd=True)

    if '.json' in filename:
        file_path = os.path.join('%s' % projPath, '{0}'.format(filename))
    else:
        file_path = os.path.join('%s' % projPath, '{0}.json'.format(filename))

    if not os.path.exists(filename):
        filename = file_path

    sel = cmds.ls(selection=True)
    if sel:
        try:
            data = []
            for obj in sel:
                curveData = dump(obj)
                data.append(curveData)

            fh = open(file_path, 'w')
            json.dump(data, fh, indent=4)
            fh.close()

            cmds.select(sel)
            LOG.info('Exported Control Curves to: %s' % file_path)
            return file_path
        except:
            LOG.error('Error exporting Control Curves to: %s' % file_path)
            raise
    else:
        LOG.error('No curve controls selected to export!')
        return
