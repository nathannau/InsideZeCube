#Author-Nathan NAU
#Description-Generateur de InsideZeCude

import os, sys
# sys.path.append(os.path.dirname(os.path.abspath('./pkg')))
sys.path.append(os.path.dirname(__file__))
# sys.path.append(os.path.abspath('.'))
# sys.path.append(os.path.abspath('./my_pkg'))

import adsk.core # pylint: disable=import-error
import adsk.fusion # pylint: disable=import-error
import adsk.cam # pylint: disable=import-error
import traceback
import time

# import pkg
import importlib
from importlib import reload, invalidate_caches
pkg = importlib.import_module('pkg')
importlib.invalidate_caches()
pkg = importlib.reload(pkg)



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

        onCommandCreated = pkg.MyCommandCreatedHandler()
        btn.commandCreated.add(onCommandCreated)
        # _handlers.append(onCommandCreated)


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

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


