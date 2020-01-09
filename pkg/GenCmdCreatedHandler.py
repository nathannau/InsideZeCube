import adsk.core # pylint: disable=import-error
import adsk.fusion # pylint: disable=import-error
import adsk.cam # pylint: disable=import-error
import traceback

class GenCmdCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self): # , ui:adsk.core.UserInterface):
        super().__init__()
        # self.ui = ui

    def notify(self, args):
        # sui = self.ui
        ui = None
        try:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            if ui:
                ui.messageBox('OnClick : Hello World 2')

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
