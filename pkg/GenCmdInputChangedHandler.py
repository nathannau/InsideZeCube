import adsk.core # pylint: disable=import-error
import adsk.fusion # pylint: disable=import-error
import adsk.cam # pylint: disable=import-error
import traceback

class GenCmdInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        ui = None
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)

            inputs = eventArgs.inputs
            cmdInput = eventArgs.input

            if cmdInput.id == 'x':
                xInput = adsk.core.IntegerSpinnerCommandInput.cast(cmdInput)
                startXInput = adsk.core.IntegerSliderCommandInput.cast(inputs.itemById('startX'))
                stopXInput = adsk.core.IntegerSliderCommandInput.cast(inputs.itemById('stopX'))
                startXInput.maximumValue = xInput.value
                stopXInput.maximumValue = xInput.value
                if startXInput.valueOne > xInput.value - 1:
                    startXInput.valueOne = xInput.value - 1
                if stopXInput.valueOne > xInput.value - 1:
                    stopXInput.valueOne = xInput.value - 1
                if startXInput.valueTwo > xInput.value:
                    startXInput.valueTwo = xInput.value
                if stopXInput.valueTwo > xInput.value:
                    stopXInput.valueTwo = xInput.value
            elif cmdInput.id == 'y':
                yInput = adsk.core.IntegerSpinnerCommandInput.cast(cmdInput)
                startYInput = adsk.core.IntegerSliderCommandInput.cast(inputs.itemById('startY'))
                stopYInput = adsk.core.IntegerSliderCommandInput.cast(inputs.itemById('stopY'))
                startYInput.maximumValue = yInput.value
                stopYInput.maximumValue = yInput.value
                if startYInput.valueOne > yInput.value:
                    startYInput.valueOne = yInput.value
                if stopYInput.valueOne > yInput.value:
                    stopYInput.valueOne = yInput.value

          
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
