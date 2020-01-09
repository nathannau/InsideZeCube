#Author-Nathan NAU
#Description-Generateur de InsideZeCude

import os, sys, glob
selfDir = os.path.dirname(__file__)
if selfDir not in sys.path:
    sys.path.append(selfDir)

import adsk.core # pylint: disable=import-error
import adsk.fusion # pylint: disable=import-error
import adsk.cam # pylint: disable=import-error
import traceback
import time

import pkg


_handlers = []
btnId = 'IZCGId'+str(round(time.time()))

def run(context):
    # global app, ui
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        btn = ui.commandDefinitions.addButtonDefinition(
            btnId, 
            'Inside Ze Cube Generator', 
            '',
            './/Resources//Generator')

        onCommandCreated = pkg.GenCmdCreatedHandler()
        btn.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)


        ssap = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        btnc = ssap.controls.addCommand(btn)
        btnc.isPromotedByDefault = True

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        btn = ui.commandDefinitions.itemById(btnId)
        if btn:
            btn.deleteMe()
        ssap = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        btnc = ssap.controls.itemById(btnId)

        if btnc:
            btnc.deleteMe()

        unloadPkg()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def unloadPkg():
    basePath = os.path.dirname(__file__)+'/'
    for file in glob.glob(basePath+'pkg/**.py', recursive=True):
        file = file[len(basePath):]
        file = (file.replace('.py','') 
                    .replace('\\','/')
                    .replace('/','.')
                    .replace('.__init__', ''))
        if file in sys.modules:
            del sys.modules[file]
