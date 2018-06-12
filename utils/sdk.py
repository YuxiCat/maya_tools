import os, sys
import json
import log
LOG = log.get_logger(__name__)

import maya.cmds as cmds
import maya.mel as mm


def lockUnlockSDKAnimCurves(lock=False):
    try:
        animCurveTypes=("animCurveUL","animCurveUU","animCurveUA","animCurveUT")
        sdkCurves = cmds.ls(type=animCurveTypes)

        if sdkCurves:
            for sdkCurve in sdkCurves:
                cmds.setAttr('%s.keyTimeValue' % sdkCurve, lock=lock)
        return True
    except:
        pass


def lockSetDrivenKeyCurve(sdkCurve):
    if cmds.objExists(sdkCurve):
        cmds.setAttr('%s.keyTimeValue' % sdkCurve, lock=True)
        return True
    else:
        return


def returnSetDrivenKeyData(sdkAnimCurve):
    '''
    Returns setDrivenKey command from input sdkAnimCurve
    returnSetDrivenKeyData('Rt_elbow_jnt_transRot_helper_offsetX')
    '''
    LOG.debug('Working on sdkCurve: %s' % sdkAnimCurve)
    if not cmds.objExists(sdkAnimCurve):
        LOG.debug('sdkCurve does not exist: %s' % sdkAnimCurve)
        return

    # Find driver and driven objects
    driver = cmds.listConnections('%s.input' % sdkAnimCurve, scn=True, source=True, destination=False, plugs=True)
    driven = cmds.listConnections('%s.output' % sdkAnimCurve, source=False, destination=True, plugs=True)

    # Find keyframes and values
    driverKeys = cmds.keyframe(sdkAnimCurve, q=True, floatChange=True)
    drivenKeys = cmds.keyframe(sdkAnimCurve, q=True, valueChange=True)

    # Get animCurve tangent types
    itt = mm.eval("keyTangent -query -itt %s ;" % sdkAnimCurve)
    ott = mm.eval("keyTangent -query -ott %s ;" % sdkAnimCurve)

    # Get animCurve lock status
    unify = mm.eval("keyTangent -query -lock %s ;" % sdkAnimCurve)

    # Get animCurve angle values
    ia = mm.eval("keyTangent -query -ia %s ;" % sdkAnimCurve)
    oa = mm.eval("keyTangent -query -oa %s ;" % sdkAnimCurve)

    # Get animCurve pre/post infinity
    cmds.selectKey(sdkAnimCurve, add=True, k=True, f=(driverKeys[0], driverKeys[0]))
    pri = cmds.setInfinity(q=True, pri=True)[0]

    cmds.selectKey(clear=True)
    cmds.selectKey(sdkAnimCurve, add=True, k=True, f=(driverKeys[-1], driverKeys[-1]))
    poi = cmds.setInfinity(q=True, poi=True)[0]

    # Return sdk data
    sdkDict = {}
    sdkDict['driver'] = driver[0]
    sdkDict['driven'] = driven[0]
    sdkDict['driverKeys'] = driverKeys
    sdkDict['drivenKeys'] = drivenKeys
    sdkDict['itt'] = itt
    sdkDict['ott'] = ott
    sdkDict['pri'] = pri
    sdkDict['poi'] = poi
    sdkDict['lock'] = unify
    sdkDict['ia'] = ia
    sdkDict['oa'] = oa
    return sdkDict


def exportSDK(exportPath):
    animCurves = cmds.ls(type=("animCurveUL", "animCurveUU", "animCurveUA", "animCurveUT"))
    cmds.select(animCurves, r=1)
    if not animCurves:
        LOG.info('No SDK curves in the scene.')
        return

    data = {}
    for i in range(len(animCurves)):
        LOG.debug('sdkCurve: %s' % animCurves[i])
        sdkData = returnSetDrivenKeyData(animCurves[i])
        data[animCurves[i]] = sdkData

    with open(exportPath, 'w') as outfile:
        try:
            json.dump(data, outfile, sort_keys=True, indent=4)
            LOG.info('Exported setDrivenKey data to {}.'.format(exportPath))
            return True
        except:
            LOG.error('Unable to export setDrivenKey data to {0}.'.format(exportPath))
            return False


def importSDK(importPath, lock=False):
    with open(importPath) as infile:
        try:
            data = json.load(infile)
        except:
            LOG.error('Unable to load setDrivenKey data from {0}.'.format(importPath))
            return False

    # iterate through dict keys
    for sdkCurve, sdkDict in data.iteritems():

        driver = sdkDict['driver']
        driven = sdkDict['driven']
        driverKeys = sdkDict['driverKeys']
        drivenKeys = sdkDict['drivenKeys']
        itt = sdkDict['itt']
        ott = sdkDict['ott']
        pri = sdkDict['pri']
        poi = sdkDict['poi']
        unify = sdkDict['lock']
        ia = sdkDict['ia']
        oa = sdkDict['oa']

        if not cmds.objExists(driver):
            LOG.warning('SetDrivenKey: driver object "{}" missing in the scene'.format(driver))
            continue
        if not cmds.objExists(driven):
            LOG.warning('SetDrivenKey: driven object "{}" missing in the scene'.format(driver))
            continue
        if cmds.objExists(sdkCurve):
            cmds.delete(sdkCurve)

        i = 0
        cmds.select(driven)
        for driverKey, drivenKey in zip(driverKeys, drivenKeys):
            # Create setDrivenKeyframes
            cmds.setDrivenKeyframe(driven, cd=driver, dv=driverKey, value=drivenKey)
            LOG.debug('SetDrivenKeyframe:  Driver=%s.%s, Driven=%s.%s' % (driver, driven, driverKey, drivenKey))

            cmds.selectKey(clear=1)
            # Set keyframe tangents
            cmds.selectKey(sdkCurve, add=True, k=True, f=(driverKey, driverKey))
            cmds.keyTangent(itt=itt[i], ott=ott[i])

            # Set fixed angles
            if not unify[i]:
                cmds.keyTangent(lock=0)
            if itt[i] == 'fixed':
                cmds.keyTangent(sdkCurve, e=1, a=1, f=(driverKey, driverKey), ia=ia[i])
            if ott[i] == 'fixed':
                cmds.keyTangent(sdkCurve, e=1, a=1, f=(driverKey, driverKey), oa=oa[i])

            i += 1

        # Set pre/post infinity
        cmds.selectKey(sdkCurve, add=True, k=True, f=(driverKeys[0], driverKeys[0]))
        cmds.setInfinity(pri=pri)

        cmds.selectKey(clear=True)
        cmds.selectKey(sdkCurve, add=True, k=True, f=(driverKeys[-1], driverKeys[-1]))
        cmds.setInfinity(poi=poi)

        # Lock setDrivenKeyframes if specified
        if lock:
            cmds.setAttr('%s.keyTimeValue' % sdkCurve, lock=True)

        cmds.refresh()
    LOG.info('Imported setDrivenKey data from {}.'.format(importPath))