import adsk.core # pylint: disable=import-error
import adsk.fusion # pylint: disable=import-error
import adsk.cam # pylint: disable=import-error
import traceback
from .Generator import Generator
from .Builder import Builder
from .BuilderPipe import BuilderPipe
from .BuilderSketch import BuilderSketch

class GenCmdExecuteHandler(adsk.core.CommandEventHandler):
    cache = {}

    def __init__(self):
        super().__init__()

    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)

        # Get the values from the command inputs.
        inputs = eventArgs.command.commandInputs

        xInput = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById('x'))
        yInput = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById('y'))
        zInput = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById('z'))
        bsInput = adsk.core.ValueCommandInput.cast(inputs.itemById('ballSize'))
        ssInput = adsk.core.ValueCommandInput.cast(inputs.itemById('spaceSize'))
        startXInput = adsk.core.IntegerSliderCommandInput.cast(inputs.itemById('startX'))
        startYInput = adsk.core.IntegerSliderCommandInput.cast(inputs.itemById('startY'))
        stopXInput = adsk.core.IntegerSliderCommandInput.cast(inputs.itemById('stopX'))
        stopYInput = adsk.core.IntegerSliderCommandInput.cast(inputs.itemById('stopY'))
        extremityTypeInput = adsk.core.DropDownCommandInput.cast(inputs.itemById('extremityType'))
        peepholeInput = adsk.core.DropDownCommandInput.cast(inputs.itemById('peephole'))
        peepholeSizeInput = adsk.core.ValueCommandInput.cast(inputs.itemById('peepholeSize'))
        fillHolesInput = adsk.core.BoolValueCommandInput.cast(inputs.itemById('fillHoles'))
        seedInput = adsk.core.IntegerSliderCommandInput.cast(inputs.itemById('seed'))
        renderModeInput = adsk.core.DropDownCommandInput.cast(inputs.itemById('renderMode'))


        self.display(xInput.value, yInput.value, zInput.value, bsInput.value, ssInput.value,
            startXInput.valueOne, startXInput.valueTwo, startYInput.valueOne,
            stopXInput.valueOne, stopXInput.valueTwo, stopYInput.valueOne,
            extremityTypeInput.selectedItem.name, 
            peepholeInput.selectedItem.name, peepholeSizeInput.value,
            fillHolesInput.value, seedInput.valueOne, renderModeInput.selectedItem.name)

        eventArgs.isValidResult = True

    def display(self, sizeX:int, sizeY:int, sizeZ:int, sizeBall:float, sizeSpace:float,
        startX1:int, startX2:int, startY:int, stopX1:int, stopX2:int, stopY:int, 
        extremity:str, peephole:str, peepholeSize:float,
        fillHoles:bool, seed:int, mode:str):
        
        key = "%d-%d-%d-%d-%d-%d-%d-%d-%d-%d-%d" % (
            sizeX, sizeY, sizeZ, 
            startX1, startX2, startY, 
            stopX1, stopX2, stopY,
            1 if fillHoles else 0, seed)
        if not key in self.cache:
            gen = Generator(sizeX, sizeY, sizeZ)
            gen = gen.build(startX1, startX2, startY, stopX1, stopX2, stopY, seed)
            if fillHoles: gen.fillHoles()
            self.cache[key] = gen
        else:
            gen:Generator = self.cache[key]

        builder:Builder = None
        if mode == 'Sketch':
            builder = BuilderSketch()
            # buildSketch(gen, sizeBall, sizeSpace)
        elif mode == 'Pipe':
            builder = BuilderPipe()
            # buildPipe(gen, sizeBall, sizeSpace)
        elif mode == 'Square':
            pass

        if builder: 
            builder.build(
                gen, sizeBall, sizeSpace, 
                extremity, peephole, peepholeSize
            )
