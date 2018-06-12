import json
import maya.cmds as cmds
import log, app, attributes

LOG = log.get_logger(__name__)


def toggleLRAVisibility():
    """Toggle the visibility of local rotation axes.

    Args:
        None.
    Returns:
        None.
    Raises:
        Logs warning if nothing is selected.
    """
    sel = cmds.ls(sl=1)
    if len(sel) < 1:
        LOG.warning('Nothing is selected.')
        return

    for jnt in sel:
        cmds.toggle(jnt, localAxis=1)


def orientTo():
    """Match specified joint orientation to a target transform.

    Select one source joint and one or more target joints.

    Args:
        None
    Returns:
        None.
    Raises:
        Logs warning if less than 2 objects are selected.
        Logs warning if selections contain non-joint type.
    """
    sel = cmds.ls(sl=1)
    if len(sel) < 2:
        LOG.warning('Please select one source joint and one or more target joints.')
        return

    for jnt in sel:
        if not cmds.objectType(jnt, isType="joint"):
            LOG.warning('Please select joints only.')

    for i in xrange(1, len(sel)):
        # Find unparent children
        children = cmds.listRelatives(sel[i], children=1, type='transform')
        if children and (len(children) > 0):
            # Unparent and get names of the objects(possibly renamed)
            children = cmds.parent(children, w=1)

        oCons = cmds.orientConstraint(sel[0], sel[i])
        cmds.delete(oCons)

        cmds.joint(sel[i], edit=True, zso=1)
        cmds.makeIdentity(sel[i], apply=1, r=True)

        if children and (len(children) > 0):
            cmds.parent(children, sel[i])


def turnOffLRA():
    """
    Turn off LRA for all transform nodes in the scene.

    Returns: NA

    """
    sel = cmds.ls(type='transform')
    for node in sel:
        cmds.setAttr(node + '.dla', 0)


def orientJoint(joints, aimAxis, upAxis, worldUpAxis):
    """Orient joints.

    Adjust joint orientation of selected joints by a certain degree.

    Args:
        joints: List of joints to orient.
        aimAxis: Array(x, y, z) of what axis of joint does aim.
        upAxis: Array(x, y, z) of what axis of joint does up.
        worldUpAxis: World axis used for up direction.
    Returns:
        None.
    Raises:
        Logs warning if axis input is NOT xyz.
        Logs warning if operator input is NOT +-.
    """
    if len(aimAxis) != 3:
        LOG.error('Parameter "aimAxis" must be in format of Array(x, y, z).')
        return
    if len(upAxis) != 3:
        LOG.error('Parameter "upAxis" must be in format of Array(x, y, z).')
        return
    if len(worldUpAxis) != 3:
        LOG.error('Parameter "worldUpAxis" must be in format of Array(x, y, z).')
        return

    for i in xrange(len(joints)):
        # Find unparent children
        children = cmds.listRelatives(joints[i], children=1, pa=1, type='transform')
        if children and (len(children) > 0):
            # Unparent and get names of the objects(possibly renamed)
            children = cmds.parent(children, w=1)

        # Find parent
        parent = cmds.listRelatives(joints[i], pa=1, parent=1)
        if parent:
            parent = parent[0]

        # If joints[i] has a child joint, aim to that
        aimTarget = ''
        if children:
            for child in children:
                if cmds.objectType(child, isType="joint"):
                    aimTarget = child
                    break

        if aimTarget != '':
            aCons = cmds.aimConstraint(aimTarget, joints[i], aim=aimAxis, upVector=upAxis, worldUpVector=worldUpAxis, worldUpType='vector')
            cmds.delete(aCons)

        elif parent:
            # If there is no target, dup orientation of parent
            oCons = cmds.orientConstraint(parent, joints[i])
            cmds.delete(oCons)

        cmds.joint(joints[i], edit=True, zso=1)
        cmds.makeIdentity(joints[i], apply=1, r=True)

        if children and (len(children) > 0):
            cmds.parent(children, joints[i])


def orientTweak(degree, axis, operator):
    """Tweak jointOrient by degree.

    Adjust joint orientation of selected joints by a certain degree.

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
    sel = cmds.ls(sl=1, type='joint')
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

    for jnt in sel:
        cmds.xform(jnt, r=1, os=1, ra=v)
        cmds.joint(jnt, edit=True, zso=1)
        cmds.makeIdentity(jnt, apply=1, r=True)

    sel = cmds.select(sel)


def insertJoints(num):
    """Insert a number of joints between 2 selected joints.

    Takes in an integer as the number of joints to insert.

    Args:
        num: Number of joints to insert.
    Returns:
        List of inserted joints.
    Raises:
        Logs warning if more than 2 objects are selected.
        Logs warning if selection type is NOT joint.
    """
    sel = cmds.ls(sl=1)
    if len(sel) != 2:
        LOG.warning('Please select 2 joints.')
        return

    if not (cmds.objectType(sel[0], isType="joint") and cmds.objectType(sel[1], isType="joint")):
        LOG.warning('Both selections must be joint type.')
        return

    # Swap selection order if child before parent
    checkList = cmds.listRelatives(sel[0], allDescendents=True)
    if not (checkList and (sel[1] in checkList)):
        sel[0], sel[1] = sel[1], sel[0]

    parentPos = cmds.xform(sel[0], q=1, t=1, ws=1)
    childPos = cmds.xform(sel[1], q=1, t=1, ws=1)

    unitX = (childPos[0] - parentPos[0]) / (num + 1)
    unitY = (childPos[1] - parentPos[1]) / (num + 1)
    unitZ = (childPos[2] - parentPos[2]) / (num + 1)
    result = []
    parentJnt = sel[0]
    for i in xrange(num):
        posX = parentPos[0] + (i + 1) * unitX
        posY = parentPos[1] + (i + 1) * unitY
        posZ = parentPos[2] + (i + 1) * unitZ
        jnt = cmds.duplicate(sel[0], po=1)[0]
        result.append(jnt)
        cmds.xform(jnt, t=[posX, posY, posZ], ws=1)
        cmds.parent(jnt, parentJnt)
        cmds.setAttr(jnt + '.jointOrient', 0, 0, 0)
        parentJnt = jnt

    cmds.parent(sel[1], result[-1])


def planarOrient(joints, aimAxis, upAxis):
    """Adjust the joint orientation of three joints to their invisible plane.

    Args:
        joints: List of 3 joints.
        aimAxis: Array(x, y, z) of what axis of joint does aim.
        upAxis: Array(x, y, z) of what axis of joint does up.
        crossVector: World axis used for up direction.
    Returns:
        None.
    Raises:
        Logs warning if the length of joints is not 3.
        Logs warning if joints contain non-joint type.
    """
    if len(joints) != 3:
        LOG.warning('Please select 3 joints.')
        return

    for jnt in joints:
        if not cmds.objectType(jnt, isType="joint"):
            LOG.warning('Please select joints only.')

    jnt1 = cmds.xform(joints[0], ws=1, t=1, q=1)
    jnt2 = cmds.xform(joints[1], ws=1, t=1, q=1)
    jnt3 = cmds.xform(joints[2], ws=1, t=1, q=1)

    vector1 = [jnt2[0] - jnt1[0], jnt2[1] - jnt1[1], jnt2[2] - jnt1[2]]
    vector2 = [jnt3[0] - jnt2[0], jnt3[1] - jnt2[1], jnt3[2] - jnt2[2]]
    crossVector = cross(vector1, vector2)

    orientJoint(joints, aimAxis, upAxis, crossVector)


def cross(a, b):
    """
    Cross product.

    Args:
        a: Vector a.
        b: Vector b.

    Returns: Cross product of a and b.

    """
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]

    return c


def segmentScaleCompensate(joints, mode=None):
    """
    Set the segmentScaleCompensate attr on joints.

    Args:
        joints: A list of joints.
        mode: Boolean.

    Returns: NA

    """
    if not mode:
        mode = False

    for jnt in joints:
        cmds.setAttr(jnt+'.segmentScaleCompensate', mode)


def deleteJoint(joint):
    """
    Removes joint and maintains hierarchy. Use this for optimization of skel.

    Args:
        joint: Target joint to delete.

    Returns: NA

    Raises:
        Logs error if joint doesn't exist.

    """
    if cmds.objExists(joint):
        parent = cmds.listRelatives(joint, p=True)
        children = cmds.listRelatives(joint, c=True, type='joint')
        if children:
            for child in children:
                if parent:
                    cmds.parent(child, parent[0])
                else: # parent to world
                    cmds.parent(child, w=True)
        cmds.delete(joint)
    else:
        LOG.error("%s doesn't exists, skipping..." % joint)


def deleteJointsFromHierarchy(joints):
    """
    Deletes a list of joints and maintains hierarchy.

    Args:
        joints: List of joints to delete from hierarchy.

    Returns: NA

    """
    for j in joints:
        deleteJoint(j)


# ------- data IO ------- #
def exportSkeleton(exportPath, root):
    '''Exports skeleton data to a json file.
    Args:
        exportPath: The file path where a json file is saved.
        root: The root joint of a skeleton to export.

    Returns:
        True if export succeeds. False if export fails.
    Raises:
        Logs error if unable to export json file.
    '''
    def recursiveGather(jnt):
        infoDict = {}
        children = cmds.listRelatives(jnt, children=1, pa=1, type='joint')
        infoDict['p'] = cmds.joint(jnt, q=1, position=1)
        infoDict['o'] = cmds.joint(jnt, q=1, orientation=1)
        infoDict['roo'] = cmds.joint(jnt, q=1, rotationOrder=1)
        infoDict['s'] = cmds.joint(jnt, q=1, scale=1)
        infoDict['r'] = cmds.getAttr(jnt + '.r')[0]
        infoDict['custom'] = {}
        infoDict['child'] = {}
        # custom attrs
        customAttrList = cmds.listAttr(jnt, ud=1)
        if not customAttrList:
            customAttrList = []
        for attr in customAttrList:
            attributes.gatherDict(jnt, attr)
            infoDict['custom'][attr] = attributes.gatherDict(jnt, attr)
            #cmds.getAttr('{}.{}'.format(jnt, attr))
        if not children:
            return infoDict
        for child_jnt in children:
            infoDict['child'][child_jnt] = recursiveGather(child_jnt)
        return infoDict

    data = {}
    data[root] = recursiveGather(root)
    par = cmds.listRelatives(root, parent=1, pa=1)
    if par:
        par = par[0]
    data['parent'] = par

    with open(exportPath, 'w') as outfile:
        try:
            json.dump(data, outfile, sort_keys=True, indent=4)
            LOG.info('Exported skeleton data to {}.'.format(exportPath))
            return True
        except:
            LOG.error('Unable to export skeleton data to {0}.'.format(exportPath))
            return False


def importSkeleton(importPath):
    '''
    Args:
        importPath: The file path where a json file is loaded.

    Returns:
        True if export succeeds. False if export fails.

    Raises:
        Logs error if unable to load json file.
    '''
    with open(importPath) as infile:
        try:
            # data = json.load(infile)
            data = app.json_load_byteified(infile)
        except:
            LOG.error('Unable to load skeleton data from {0}.'.format(importPath))
            return False

    def recursiveRead(d):
        for jnt in d:
            if jnt == 'parent':
                continue

            sel = cmds.ls(sl=1)
            shortName = jnt.split('|')[-1]
            p = d[jnt]['p']
            o = d[jnt]['o']
            s = d[jnt]['s']
            roo = d[jnt]['roo']
            r = d[jnt]['r']
            if cmds.objExists(jnt):
                cmds.joint(jnt, e=1, p=p, o=o, s=s, roo=roo)
                LOG.info('{} already exists in the scene. Skipped joint creation.'.format(jnt))
            else:
                cmds.joint(n=shortName, p=p, o=o, s=s, roo=roo)
            cmds.setAttr(jnt + '.rx', r[0])
            cmds.setAttr(jnt + '.ry', r[1])
            cmds.setAttr(jnt + '.rz', r[2])
            # custom attrs
            if d[jnt]['custom']:
                for attr in d[jnt]['custom']:
                    attributes.restoreAttr(jnt, attr, d[jnt]['custom'][attr])
            cmds.select(jnt)
            recursiveRead(d[jnt]['child'])
            cmds.select(sel)

    cmds.select(cl=1)
    par = data['parent']
    if (par and cmds.objExists(par)):
        cmds.select(par)

    recursiveRead(data)

    LOG.info('Imported skeleton data from {}.'.format(importPath))
