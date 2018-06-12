import json, ast
import maya.cmds as cmds
import log

LOG = log.get_logger(__name__)


CHANNELNAMES = ['translateX', 'translateY', 'translateZ',
        'rotateX', 'rotateY', 'rotateZ',
        'scaleX', 'scaleY', 'scaleZ',
        'visibility'
]


def attrTag(node):
    '''Tag the node by adding and setting "attrTag" attr with channel status.
    Args:
        node: Target node name.

    Returns: String value from attribute "attrTag", which can be read as a dictionary.
    '''
    if not cmds.attributeQuery('attrTag', node=node, ex=True):
        cmds.addAttr(node, ln='attrTag', dt='string')
    # list of attrs
    customAttrList = cmds.listAttr(node, ud=1)
    attrList = list()
    attrList = CHANNELNAMES
    if customAttrList:
        attrList = CHANNELNAMES + customAttrList

    attrDict = {}
    for attr in attrList:
        if attr is 'attrTag':
            continue
        keyable = cmds.getAttr('{}.{}'.format(node, attr), k=1)
        unlock = cmds.getAttr('{}.{}'.format(node, attr), l=1)
        visible = cmds.getAttr('{}.{}'.format(node, attr), cb=1)
        attrDict[attr] = [keyable, unlock, visible]

    attrStr = str(attrDict)
    cmds.setAttr('{}.{}'.format(node, 'attrTag'), attrStr, type='string')
    return attrStr


def applyTag(node):
    '''Apply channel status according to attribute "attrTag".
    Args:
        node: Target node name.

    Returns:
    '''
    if not cmds.attributeQuery('attrTag', node=node, ex=True):
        print 'No tags found on %s.' %node
        return False

    attrStr = cmds.getAttr('{}.{}'.format(node, 'attrTag'))
    attrDict = ast.literal_eval(attrStr)

    for attr in attrDict:
        keyable = attrDict[attr][0]
        unlock = attrDict[attr][1]
        visible = attrDict[attr][2]
        setAttrStatus(node, attr, 1, keyable)
        setAttrStatus(node, attr, 2, 1 - unlock)
        setAttrStatus(node, attr, 3, visible)
    return True


def setAttrStatus(node, attrName, col, status):
    '''Set the attribute status.
    Args:
        node: Target node name.
        attrName: Attribute name.
        col: 1 for keyable; 2 for unlock; 3 for channelBox
        status: True or False.

    Returns:
    '''
    if cmds.attributeQuery(attrName, node=node, ex=True):
        # keyable unlocked visible
        if col == 1:
            cmds.setAttr('{}.{}'.format(node, attrName), keyable=status)
        elif col == 2:
            cmds.setAttr('{}.{}'.format(node, attrName), lock=1 - status)
        elif col == 3:
            cmds.setAttr('{}.{}'.format(node, attrName), channelBox=status)


def exportChannelTags(exportPath):
    '''Export the channel tags for selected transform nodes.
    Args:
        exportPath: Absolute path to save a json file.

    Returns:
        bool
    '''
    import json
    sel = cmds.ls(type='transform', l=1, sl=1)
    d = {}
    for node in sel:
        # if cmds.attributeQuery('attrTag', node=node, ex=True):
        attrStr = attrTag(node)
        d[node] = attrStr
    with open(exportPath, 'w') as outfile:
        try:
            json.dump(d, outfile, indent=4)
            LOG.info('Exported channel status data to {0}.'.format(exportPath))
            return True
        except:
            LOG.error('Unable to export channel status data to {0}.'.format(exportPath))
            return False


def importChannelTags(importPath):
    '''Import the channel tags from a json file.
    Args:
        importPath: Absolute path to load a json file.

    Returns:
        bool
    '''
    with open(importPath, "r") as infile:
        try:
            data = json.load(infile)
            LOG.info('Loaded channel data from {0}.'.format(importPath))
        except:
            LOG.error('Unable to load channel data from {0}.'.format(importPath))
            return False

    for node in data:
        if not cmds.objExists(node):
            LOG.info('Skipping channel status for node {}'.format(node))
            continue
        if not cmds.attributeQuery('attrTag', node=node, ex=True):
            cmds.addAttr(node, ln='attrTag', dt='string')
        attrStr = data[node]
        cmds.setAttr('{}.{}'.format(node, 'attrTag'), attrStr, type='string')
        applyTag(node)
    return True
