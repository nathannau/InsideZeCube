
import adsk.core # pylint: disable=import-error
import adsk.fusion # pylint: disable=import-error
import adsk.cam # pylint: disable=import-error
import traceback

from .GenCmdDestroyHandler import GenCmdDestroyHandler
from .GenCmdInputChangedHandler import GenCmdInputChangedHandler
from .GenCmdExecutePreviewHandler import GenCmdExecutePreviewHandler
from .GenCmdExecuteHandler import GenCmdExecuteHandler

_handlers = []

class GenCmdCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        ui = None
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface

            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Connect to the command destroyed event.
            onDestroy = GenCmdDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # Connect to the input changed event.           
            onInputChanged = GenCmdInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)

            # Connect to the command execute preview event.           
            onExecutePreview = GenCmdExecutePreviewHandler()
            cmd.executePreview.add(onExecutePreview)
            _handlers.append(onExecutePreview)

            # Connect to the command execute event.           
            onExecute = GenCmdExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)


            # Get the CommandInputs collection associated with the command.
            inputs = cmd.commandInputs

            xInput = inputs.addIntegerSpinnerCommandInput('x', 'X', 3, 15, 1, 6)
            yInput = inputs.addIntegerSpinnerCommandInput('y', 'Y', 3, 15, 1, 6)
            zInput = inputs.addIntegerSpinnerCommandInput('z', 'Z', 3, 15, 1, 6) # pylint: disable=unused-variable

            inputs.addValueInput('ballSize', 'Diametre de la balle', 'mm', adsk.core.ValueInput.createByReal(.6))
            inputs.addValueInput('spaceSize', 'Largeur des parrois', 'mm', adsk.core.ValueInput.createByReal(.1))

            grpstart = inputs.addGroupCommandInput('start', 'Début')
            grpstart.children.addIntegerSliderCommandInput('startX', 'X', 1, xInput.value, True)
            grpstart.children.addIntegerSliderCommandInput('startY', 'Y', 1, yInput.value, False)

            grpstart = inputs.addGroupCommandInput('stop', 'Fin')
            grpstart.children.addIntegerSliderCommandInput('stopX', 'X', 1, xInput.value, True)
            grpstart.children.addIntegerSliderCommandInput('stopY', 'Y', 1, yInput.value, False)

            extremityType = inputs.addDropDownCommandInput('extremityType', 'Extrimité', adsk.core.DropDownStyles.TextListDropDownStyle)
            extremityTypeItems = extremityType.listItems
            extremityTypeItems.add('Window', True, '')
            extremityTypeItems.add('Open', False, '')

            inputs.addBoolValueInput('fillHoles', 'Remplir les trous', True, '', True)
            inputs.addIntegerSliderCommandInput('seed', 'Seed', 0, 0xffff, False)

            renderMode = inputs.addDropDownCommandInput('renderMode', 'Render', adsk.core.DropDownStyles.TextListDropDownStyle)
            renderModeItems = renderMode.listItems
            renderModeItems.add('Sketch', False, '')
            renderModeItems.add('Pipe', True, '')
            renderModeItems.add('Square', False, '')

            inputs.addBoolValueInput('display', 'Afficher', True, '', False)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
