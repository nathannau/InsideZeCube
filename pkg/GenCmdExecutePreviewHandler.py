import adsk.core # pylint: disable=import-error
import adsk.fusion # pylint: disable=import-error
import adsk.cam # pylint: disable=import-error
import traceback
from .Generator import Generator
from .Builder import Builder
from .BuilderSketch import BuilderSketch

class GenCmdExecutePreviewHandler(adsk.core.CommandEventHandler):
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
        fillHolesInput = adsk.core.BoolValueCommandInput.cast(inputs.itemById('fillHoles'))
        seedInput = adsk.core.IntegerSliderCommandInput.cast(inputs.itemById('seed'))
        displayInput = adsk.core.BoolValueCommandInput.cast(inputs.itemById('display'))

        self.display(xInput.value, yInput.value, zInput.value, bsInput.value, ssInput.value,
            startXInput.valueOne, startXInput.valueTwo, startYInput.valueOne,
            stopXInput.valueOne, stopXInput.valueTwo, stopYInput.valueOne,
            fillHolesInput.value, seedInput.valueOne, displayInput.value)

        eventArgs.isValidResult = False

    def display(self, sizeX:int, sizeY:int, sizeZ:int, sizeBall:float, sizeSpace:float,
        startX1:int, startX2:int, startY:int, stopX1:int, stopX2:int, stopY:int,
        fillHoles:bool, seed:int, display:bool):
        
        if display:
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

        else:
            gen = Generator(sizeX, sizeY, sizeZ)
            gen.initStart(startX1, startX2, startY, stopX1, stopX2, stopY)

        builder = BuilderSketch()
        builder.build(gen, sizeBall, sizeSpace, '', 'None', 0.0)


    def initStartPaths(self, sizeX:int, sizeY:int, sizeZ:int,
        startX1:int, startX2:int, startY:int, stopX1:int, stopX2:int, stopY:int):

        paths = {
            'X': [ [ [ False for _ in range(sizeX-1) ] 
                             for _ in range(sizeY) ] 
                             for _ in range(sizeZ) ],
            'Y': [ [ [ False for _ in range(sizeX) ] 
                             for _ in range(sizeY-1) ]
                             for _ in range(sizeZ) ],
            'Z': [ [ [ False for _ in range(sizeX) ] 
                             for _ in range(sizeY) ]
                             for _ in range(sizeZ-1) ],
        }
        for x in range(startX1-1, startX2-1):
            paths['X'][0][startY-1][x] = True
        for x in range(stopX1-1, stopX2-1):
            paths['X'][sizeZ-1][stopY-1][x] = True

        return paths
