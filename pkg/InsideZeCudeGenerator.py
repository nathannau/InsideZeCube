# #Author-Nathan Nau
# #Description-

# import adsk.core # pylint: disable=import-error
# import adsk.fusion # pylint: disable=import-error
# import adsk.cam # pylint: disable=import-error
# import traceback
# import random
# import math
# import time

# _handlers = []
# cmdDefName = 'cmdInputsSample_'+str(round(time.time()))

# def run(context):
#     global app, ui

#     ui = None
#     try:
#         app = adsk.core.Application.get()
#         ui  = app.userInterface
#         # ui.messageBox('Hello script')

#         # product = app.activeProduct
#         # design = adsk.fusion.Design.cast(product)
#         # comp = design.activeComponent
#         # baseSketch = comp.sketches.add(comp.xYConstructionPlane)

#         # btn = ui.commandDefinitions.addButtonDefinition('IZCGId'+str(round(time.time())), 'IZCGName', 'ToolTip', './/')

#         # ssap = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
#         # btnc = ssap.controls.addCommand(btn)
#         # btnc.isPromotedByDefault = True
#         # btnc.isPromoted = True
#         # tb = ui.toolbars
#         # atp = ui.allToolbarPanels
#         # att = ui.allToolbarTabs
#         # print("* * * toolbars * * *")
#         # for i in tb:
#         #     print('\t' + i.id)
#         # print("* * * allToolbarPanels * * *")
#         # for i in atp:
#         #     print('\t' + i.id)
#         # print("* * * allToolbarTabs * * *")
#         # for i in att:
#         #     print('\t' + i.id)


#         # ui.messageBox('Oki')
#         # adsk.autoTerminate(True)
#         # return
#         cmdDef = ui.commandDefinitions.itemById(cmdDefName)
#         if not cmdDef:
#             cmdDef = ui.commandDefinitions.addButtonDefinition(cmdDefName, 'Command Inputs Sample', 'Sample to demonstrate various command inputs.')


#         # Connect to the command created event.
#         onCommandCreated = MyCommandCreatedHandler()
#         cmdDef.commandCreated.add(onCommandCreated)
#         _handlers.append(onCommandCreated)

#         # Execute the command definition.
#         cmdDef.execute()

#         # Prevent this module from being terminated when the script returns, because we are waiting for event handlers to fire.
#         adsk.autoTerminate(False)

#     except:
#         if ui:
#             ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

