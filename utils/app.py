import os
import json
import maya.cmds as cmds
import maya.mel as mel
from vendor.Qt import QtGui
from utils import log

LOG = log.get_logger(__name__)

FILETYPE = {'mb': 'mayaBinary', 'ma': 'mayaAscii', 'obj': 'OBJexport', 'abc': 'alembic', 'atom': 'atom', 'fbx': 'FBX', 'fbxexportpreset': 'FBX export preset'}
PLUGTYPE = {'so': 'linux', 'mll': 'win', 'bundle': 'mac', 'py': 'python'}


def findPlugins(plugin=None):
    """Find all plugins in the paths set in Maya's plugin path.
    Args:
        plugin (str): Name of a plugin to query if it exists
    Returns:
        If plugin=None it returns a list of plugins available,
        If a plugin name is given then it returns a bool if the plugin exists or not.
    """
    availablePlugins = list()
    pluginPaths = os.environ['MAYA_PLUG_IN_PATH'].split(':')

    for pPath in pluginPaths:
        if os.path.isdir(pPath):
            for root, subdirs, files in os.walk(pPath):
                if files:
                    for fileName in files:
                        ext = fileName.split('.')[-1]
                        if ext in PLUGTYPE:
                            availablePlugins.append(fileName)

    availablePlugins = list(set(availablePlugins))

    if plugin:
        for pluginName in availablePlugins:
            if pluginName.startswith(plugin):
                return True
    elif availablePlugins:
        return availablePlugins
    else:
        return False


def loadPlugin(plugin):
    """Load a Maya plugin.
    Args:
        plugin (str): The name of the plugin you want to load

    Returns:
        If plugin loads, True. If not, False.

    """
    if not cmds.pluginInfo(plugin, q=True, loaded=True) and findPlugins(plugin):
        cmds.loadPlugin(plugin, quiet=True)
        return True
    else:
        return False


def toggleViewport(force=None):
    """Toggle Maya's viewport off and back on again.
    This can be useful when running certain gpu intense operations
    Args:
        force: Explicitly set the state of the viewport
    Returns:
        None
    """
    if not cmds.about(batch=True):

        state = True
        if force is None:
            state = mel.eval("paneLayout -q -manage $gMainPane")
        elif force:
            state = not force

        if state:
            mel.eval("paneLayout -e -manage false $gMainPane")
        else:
            mel.eval("paneLayout -e -manage true $gMainPane")

    else:
        LOG.info("BATCH")


def isValidPath(filepath):
    """Check filepath is a valid dir / file.
    Args:
        filepath: Absolute file path to check.
    Returns:
        True if valid. False if not valid.
    """
    if os.path.isfile(filepath):
        return True
    dirName = os.path.dirname(filepath)
    if os.path.isdir(dirName):
        return True
    return False


def getSceneFile():
    """Get the current Maya scene's path and name.
    Args:
        None
    Returns:
        A tuple of the scene path, and the scene name.
    """
    sceneFilepath = cmds.file(q=True, sceneName=True)
    sceneName = cmds.file(q=True, sceneName=True, shortName=True)
    sceneDir = sceneFilepath.replace(sceneName, '')

    return(sceneDir, sceneName)


def importScene(filepath=None, namespace=None, parent=None, operation=0):
    """Import a Maya file.
    Args:
        filepath (str): Absolute path to a file
        namespace (str): Import file under this namespace string
        parent (str): Object to parent file objects under
        operation (int): 0 for import and 1 for reference file.
    Returns:
        The nodes that live in world that are imported.
    Raises:
        RuntimeError: Not a valid file.
    """
    # Check if file path is provided
    if not filepath:
        # Launch browser
        return mel.eval('projectViewer Import;')
    else:
        if type(filepath) == list:
            filepath = filepath[0]
        if verifyFilePath(filepath):
            # Reference scene
            if operation == 1:
                if namespace:
                    try:
                        newNodes = cmds.file(filepath, r=True, op="v=0", pr=True, namespace=namespace, mergeNamespacesOnClash=True, rnn=True)
                    except:
                        LOG.info('unable to reference file: {0}'.format(filepath))
                else:
                    try:
                        newNodes = cmds.file(filepath, r=True, op="v=0", pr=True, rnn=True)
                    except:
                        LOG.info('unable to reference file: {0}'.format(filepath))
            # Import scene
            elif operation == 0:
                if namespace:
                    try:
                        newNodes = cmds.file(filepath, i=True, op="v=0", pr=True, namespace=namespace, mergeNamespacesOnClash=True, rnn=True)
                    except:
                        LOG.info('unable to open file: {0}'.format(filepath))
                else:
                    try:
                        newNodes = cmds.file(filepath, i=True, op="v=0", pr=True, rnn=True)
                    except:
                        LOG.info('unable to open file: {0}'.format(filepath))
            else:
                LOG.info('invalid file operation input: {0}'.format(operation))

            newTransforms = cmds.ls(newNodes, type="transform")

            # Get the new nodes that are top nodes (parented to world)
            topNodes = list()
            for node in newTransforms:
                if not cmds.listRelatives(node, p=True):
                    topNodes.append(node)

            # Parent them
            if parent and topNodes:
                topNodes = cmds.parent(topNodes, parent)

            return topNodes

        else:
            raise RuntimeError('Invalid filepath, skipping')


def openScene(filepath=None):
    """Open a Maya scene.
    Args:
        filepath (str): Absolute file path for file to open
    Returns:
        If the filepath is invalid, open import dialog.
        If the filepath IS valid returns a list of maya nodes from the opened scene
    Raises:
        RuntimeError: Not a valid file path.
    """
    # Check if file path is provided
    if not filepath:
        # Launch browser
        return mel.eval('projectViewer Import;')
    else:
        if type(filepath) == list:
            filepath = filepath[0]
        if verifyFilePath(filepath):
            # Open scene
            newNodes = cmds.file(filepath, o=True, f=True, op="v=0", pr=True, rnn=True)

            return newNodes

        else:
            raise RuntimeError('Invalid filepath, skipping')


def toggleUndo(forceOff=None, undoMode='length', verbose=True):
    """Turn undo on or off in Maya.
    Args:
        forceOff (bool): Explicitly turn off undo
        undoMode (str): Set type of undo 'infinity' or 'length'
        verbose (bool): Toggle log feedback
    Returns:
        None
    """
    # gather some info
    state = cmds.undoInfo(q=True, state=True)
    infinity = cmds.undoInfo(q=True, infinity=True)
    length = None
    if infinity and undoMode != 'length':
        undoMode = 'infinity'
    else:
        length = cmds.undoInfo(q=True, length=True)

    # toggle
    if state > 0 or forceOff:
        # turn off undo
        cmds.undoInfo(state=False)
        if verbose:
            LOG.info('undo stack OFF')
    else:
        # turn on undo
        if undoMode == 'infinity':
            cmds.undoInfo(state=True, infinity=True)
        else:
            cmds.undoInfo(state=True, infinity=False, length=length)
        if verbose:
            LOG.info('undo stack ON: {0} = {1}'.format(undoMode, length))


def openWebPage(url):
    """
    Opens a webpage with the given URL.
    Args:
        url (str): full web address with any http:// and such
    Returns:
        None
    """
    cmds.launch(web=url)


def json_load_byteified(text):
    """
    Wrapper for json.load that convers non bytestrings to bytestrings

    Example:
        from utils import app
        file_directory = '/some/file/dir'
        json_data=open(file_directory).read()
        data = app.json_load_byteified(json_data)

    Args:
        text (str): text from json file
    Returns:
        data from json file that has been converted to bytestrings
    """
    return _byteify(json.load(text, object_hook=_byteify), ignore_dicts=True)


def json_loads_byteified(text):
    """
    Wrapper for json.loads that converts non bytestrings to bytestrings

    Example:
        from utils import app
        file_directory = '/some/file/dir'
        json_data=open(file_directory).read()
        data = app.json_loads_byteified(json_data)

    Args:
        text (str): text from json file
    Returns:
        data from json file that has been converted to bytestrings
    """
    return _byteify(json.loads(text, object_hook=_byteify), ignore_dicts=True)


def _byteify(data, ignore_dicts=False):
    """
    Converts different types of strings into byte strings i.e unicode to a byte string
    Example:
        from utils import app
        ustring = u'test'
        bytestring = app._byteify(ustring)
    Args:
        data (any type): a variable like a string or list or a dict that has non byte strings in it
        ignore_dicts (bool): If True this function will ignore dictionaries
    Returns:
        The same data type that was fed in via the data arg but in byte strings
    """
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data


def addFonts(fontDir):
    """Add fonts to QApplication.

    Args:
        fontDir: Absolute path to fonts folder.

    Returns:
        bool: True if successful, False if not.

    """
    validTypes = ['ttf', 'otf']
    fonts = QtGui.QFontDatabase()
    for font in os.listdir(fontDir):
        fontPath = os.path.join(fontDir, font)
        if os.path.isfile(fontPath):
            if font.split('.')[1] in validTypes:
                fonts.addApplicationFont(fontPath)
                return True
    return False
