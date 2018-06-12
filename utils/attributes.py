import json
import maya.cmds as cmds
import log

LOG = log.get_logger(__name__)


def gatherDict(node, attr):
    """
    Pair with restoreAttr()
    Creates a dictionary containing information necessary to recreating the attr.

    Example:
        from rigging.utils import attribute
        # get a dict of info to recreate or rebuild attr Lf_arm.softIk
        lfArmSoftIkAttrDict = attribute.gatherDict('Lf_arm', 'softIk')
    Args:
        node (str): The node to gather info from.
        attr (str): The attribute to gather info from.

    Returns: Dictionary of attribute info.
    """
    nodeAttr = '%s.%s' % (node, attr)
    attrType = cmds.getAttr(nodeAttr, type=True)
    # attrType = cmds.attributeQuery(attr, node=node, at=True)
    keyable = cmds.getAttr(nodeAttr, k=1)
    info = {}
    info['k'] = keyable
    # message
    if 'message' in attrType:
        info['d'] = cmds.listConnections(nodeAttr, d=True, s=False, p=1, scn=1)
        info['s'] = cmds.listConnections(nodeAttr, s=True, d=False, p=1, scn=1)
        info['at'] = attrType
        if not info['d']:
            info['d'] = []
        if not info['s']:
            info['s'] = []
    # string
    elif 'string' in attrType:
    # elif isinstance(cmds.getAttr(nodeAttr), basestring):
        info['dt'] = 'string'
        value = cmds.getAttr(nodeAttr)
        if not value:
            value = ''
        info['string'] = value
    # double
    elif 'double' in attrType:
        if cmds.attributeQuery(attr, node=node, maxExists=True):
            info['max'] = cmds.attributeQuery(attr, node=node, maximum=True)[0]
        if cmds.attributeQuery(attr, node=node, minExists=True):
            info['min'] = cmds.attributeQuery(attr, node=node, minimum=True)[0]
        info['at'] = attrType
        info['dv'] = cmds.getAttr(nodeAttr)
    # bool
    elif 'bool' in attrType:
        info['at'] = attrType
        info['dv'] = cmds.getAttr(nodeAttr)
    # enum
    elif 'enum' in attrType:
        info['at'] = attrType
        info['en'] = cmds.attributeQuery(attr, node=node, listEnum=True)[0]
        info['dv'] = cmds.getAttr(nodeAttr)
    # long
    elif 'long' in attrType:
        if cmds.attributeQuery(attr, node=node, maxExists=True):
            info['max'] = cmds.attributeQuery(attr, node=node, maximum=True)[0]
        if cmds.attributeQuery(attr, node=node, minExists=True):
            info['min'] = cmds.attributeQuery(attr, node=node, minimum=True)[0]
        info['at'] = attrType
        info['dv'] = cmds.getAttr(nodeAttr)
    else:
        info = {}
        LOG.error('{} invalid value'.format(nodeAttr))
    # TODO compound attrs
    # double3

    return info


def restoreAttr(node, attr, info):
    """
    Pair with gatherDict()
    Build / Rebuild attribute from a dict that has info about that attr.

    Example:
        from rigging.utils import attribute
        # rebuilds the attr softIk on Lf_arm using info from the dict lfArmSoftIkAttrDict
        # the dict comes from using attribute.gatherDict()
        attribute.restoreAttr('Lf_arm', 'softIk', 'lfArmSoftIkAttrDict')
    Args:
        node (str): The node to restore attribute info.
        attr (str): The attribute to restore.
        info (dict): The dictionary that carries attribute info.

    Returns: True if succeeds. False if fails.
    """
    nodeAttr = '%s.%s' % (node, attr)
    if cmds.attributeQuery(attr, node=node, ex=True):
        cmds.deleteAttr(nodeAttr)

    if not info:
        LOG.error('{} missing attribute information'.format(nodeAttr))
        return False

    if (('dt' in info.keys()) and (info['dt'] == 'string')):
        cmds.addAttr(node, ln=attr, dt='string')
        cmds.setAttr(nodeAttr, info['string'], type='string')
    elif info['at'] == 'message':
        cmds.addAttr(node, ln=attr, attributeType='message')
        for destination in info['d']:
            if not cmds.objExists(destination.split('.')[0]):
                LOG.error('Failed to restore message connection {} to {}'.format(nodeAttr, destination))
                continue
            cmds.connectAttr(nodeAttr, destination)
        for source in info['s']:
            if not cmds.objExists(source.split('.')[0]):
                LOG.error('Failed to restore message connection {} to {}'.format(source, nodeAttr))
                continue
            cmds.connectAttr(source, nodeAttr)
    else:
        cmds.addAttr(node, ln=attr, **info)
    # TODO compound attrs
    # double3
    return True
