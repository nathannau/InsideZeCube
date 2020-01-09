#Author-Nathan Nau
#Description-

import adsk.core # pylint: disable=import-error
import adsk.fusion # pylint: disable=import-error
import adsk.cam # pylint: disable=import-error
import traceback
import random
import math
import time

_handlers = []
cmdDefName = 'cmdInputsSample_'+str(round(time.time()))

def run(context):
    global app, ui

    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        # ui.messageBox('Hello script')

        # product = app.activeProduct
        # design = adsk.fusion.Design.cast(product)
        # comp = design.activeComponent
        # baseSketch = comp.sketches.add(comp.xYConstructionPlane)

        # btn = ui.commandDefinitions.addButtonDefinition('IZCGId'+str(round(time.time())), 'IZCGName', 'ToolTip', './/')

        # ssap = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        # btnc = ssap.controls.addCommand(btn)
        # btnc.isPromotedByDefault = True
        # btnc.isPromoted = True
        # tb = ui.toolbars
        # atp = ui.allToolbarPanels
        # att = ui.allToolbarTabs
        # print("* * * toolbars * * *")
        # for i in tb:
        #     print('\t' + i.id)
        # print("* * * allToolbarPanels * * *")
        # for i in atp:
        #     print('\t' + i.id)
        # print("* * * allToolbarTabs * * *")
        # for i in att:
        #     print('\t' + i.id)


        # ui.messageBox('Oki')
        # adsk.autoTerminate(True)
        # return
        cmdDef = ui.commandDefinitions.itemById(cmdDefName)
        if not cmdDef:
            cmdDef = ui.commandDefinitions.addButtonDefinition(cmdDefName, 'Command Inputs Sample', 'Sample to demonstrate various command inputs.')


        # Connect to the command created event.
        onCommandCreated = MyCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        # Execute the command definition.
        cmdDef.execute()

        # Prevent this module from being terminated when the script returns, because we are waiting for event handlers to fire.
        adsk.autoTerminate(False)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Connect to the command destroyed event.
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # Connect to the input changed event.           
            onInputChanged = MyCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)

            # Connect to the command execute preview event.           
            onExecutePreview = MyCommandExecutePreviewHandler()
            cmd.executePreview.add(onExecutePreview)
            _handlers.append(onExecutePreview)

            # Connect to the command execute event.           
            onExecute = MyCommandExecuteHandler()
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

            inputs.addBoolValueInput('fillHoles', 'Remplir les trous', True, '', True)
            inputs.addIntegerSliderCommandInput('seed', 'Seed', 0, 0xffff, False)

            renderMode = inputs.addDropDownCommandInput('renderMode', 'Render', adsk.core.DropDownStyles.TextListDropDownStyle)
            renderModeItems = renderMode.listItems
            renderModeItems.add('Sketch', False, '')
            renderModeItems.add('Pipe', True, '')
            renderModeItems.add('Square', False, '')

            inputs.addBoolValueInput('display', 'Afficher', True, '', False)

        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            adsk.terminate()
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class MyCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
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
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class MyCommandExecutePreviewHandler(adsk.core.CommandEventHandler):
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

        buildSketch(gen, sizeBall, sizeSpace)


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


class MyCommandExecuteHandler(adsk.core.CommandEventHandler):
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
        # displayInput = adsk.core.BoolValueCommandInput.cast(inputs.itemById('display'))
        renderModeInput = adsk.core.DropDownCommandInput.cast(inputs.itemById('renderMode'))

        self.display(xInput.value, yInput.value, zInput.value, bsInput.value, ssInput.value,
            startXInput.valueOne, startXInput.valueTwo, startYInput.valueOne,
            stopXInput.valueOne, stopXInput.valueTwo, stopYInput.valueOne,
            fillHolesInput.value, seedInput.valueOne, renderModeInput.selectedItem.name)

        eventArgs.isValidResult = True

    def display(self, sizeX:int, sizeY:int, sizeZ:int, sizeBall:float, sizeSpace:float,
        startX1:int, startX2:int, startY:int, stopX1:int, stopX2:int, stopY:int, 
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

        if mode == 'Sketch':
            buildSketch(gen, sizeBall, sizeSpace)
        elif mode == 'Pipe':
            buildPipe(gen, sizeBall, sizeSpace)
        elif mode == 'Square':
            pass


class Generator:
    EMPTY = 0
    PIPE = 1
    START = 2
    STOP = 3
    UNUSE = 4

    sizeX = 0
    sizeY = 0
    sizeZ = 0
    cube = []
    paths = {}

    def __init__(self, sizeX:int, sizeY:int, sizeZ:int):
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.sizeZ = sizeZ
        self.cube = [ Generator.EMPTY] * sizeX *  sizeY * sizeZ
        self.paths = {
            'X': [ False ] * (sizeX-1) *  sizeY * sizeZ,
            'Y': [ False ] * sizeX *  (sizeY-1) * sizeZ,
            'Z': [ False ] * sizeX *  sizeY * (sizeZ-1),
        }        

    def cubePos(self, x:int, y:int, z:int):
        return self.sizeX * self.sizeY * z + self.sizeX * y + x
    def pathXPos(self, x:int, y:int, z:int):
        return (self.sizeX-1) * self.sizeY * z + (self.sizeX-1) * y + x
    def pathYPos(self, x:int, y:int, z:int):
        return self.sizeX * (self.sizeY-1) * z + self.sizeX * y + x
    def pathZPos(self, x:int, y:int, z:int):
        return self.sizeX * self.sizeY * z + self.sizeX * y + x

    def initStart(self, 
        startX1:int, startX2:int, startY:int, 
        stopX1:int, stopX2:int, stopY:int):

        x0 = self.cubePos(0, startY-1, 0)
        for x in range(startX1-1, startX2):
            if x == startX1-1 or x == startX2-1:
                self.cube[x0 + x] = self.START
            else:
                self.cube[x0 + x] = self.UNUSE
        
        x0 = self.cubePos(0, stopY-1, self.sizeZ-1)
        for x in range(stopX1-1, stopX2):
            if x == stopX1-1 or x == stopX2-1:
                self.cube[x0 + x] = self.STOP
            else:
                self.cube[x0 + x] = self.UNUSE

        x0 = self.pathXPos(0, startY-1, 0)
        for x in range(startX1-1, startX2-1):
            self.paths['X'][x0 + x] = True
        x0 = self.pathXPos(0, stopY-1, self.sizeZ-1)
        for x in range(stopX1-1, stopX2-1):
            self.paths['X'][x0 + x] = True

    def copy(self):
        ret = Generator(0, 0, 0)
        ret.sizeX = self.sizeX
        ret.sizeY = self.sizeY
        ret.sizeZ = self.sizeZ
        ret.cube = self.cube[:]
        ret.paths = {
            'X': self.paths['X'][:],
            'Y': self.paths['Y'][:],
            'Z': self.paths['Z'][:],
        }
        return ret

    def build(self, 
        startX1:int, startX2:int, startY:int, 
        stopX1:int, stopX2:int, stopY:int,
        seed:int):

        random.seed(seed)
        self.initStart(startX1, startX2, startY, stopX1, stopX2, stopY)

        if random.randint(0, 1) == 0:
            pos = { 'X': startX1-1, 'Y': startY-1, 'Z':0 }
        else:
            pos = { 'X': startX2-1, 'Y': startY-1, 'Z':0 }
             
        self.cube[self.cubePos(pos['X'],pos['Y'], pos['Z'])] = self.PIPE

        return self.buildPath(pos)

    def buildPath(self, pos:dict):

        dirs = [
            { 'X':-1, 'Y':0, 'Z':0 },
            { 'X': 1, 'Y':0, 'Z':0 },
            { 'X':0, 'Y':-1, 'Z':0 },
            { 'X':0, 'Y': 1, 'Z':0 },
            { 'X':0, 'Y':0, 'Z':-1 },
            { 'X':0, 'Y':0, 'Z': 1 },
        ]
        random.shuffle(dirs)

        while len(dirs):
            d = dirs.pop()

            gen = self.setDirection(pos, d)
            if gen is None: continue

            return gen

        return None

    def isValidPosition(self, pos:dict):
        return (pos['X'] >= 0 and pos['Y'] >= 0 and pos['Z'] >= 0 and
                pos['X'] < self.sizeX and pos['Y'] < self.sizeY and pos['Z'] < self.sizeZ)

    def setDirection(self, pos, direction):
        n = dict(pos)
        v = 0
        for k in n: 
            n[k] += direction[k]
            v += direction[k]

        if not self.isValidPosition(n):
            return None

        gen = self.copy()

        ncp = self.cubePos(n['X'], n['Y'], n['Z'])
        if v > 0:
            pp = pos
        else:
            pp = n
        if direction['X'] != 0 : 
            gen.paths['X'][gen.pathXPos(pp['X'], pp['Y'], pp['Z'])] = True
        elif direction['Y'] != 0 : 
            gen.paths['Y'][gen.pathYPos(pp['X'], pp['Y'], pp['Z'])] = True
        elif direction['Z'] != 0 : 
            gen.paths['Z'][gen.pathZPos(pp['X'], pp['Y'], pp['Z'])] = True

        gen.cube[ncp] = Generator.PIPE

        if self.cube[ncp] == Generator.STOP:
            return gen

        if self.cube[ncp] != Generator.EMPTY:
            return None

        return gen.buildPath(n)

    def fillHoles(self):

        pos = [ { 'X':x, 'Y':y, 'Z':z } 
            for x in range(self.sizeX) 
            for y in range(self.sizeY)
            for z in range(self.sizeZ) 
        ]
        random.shuffle(pos)

        while len(pos):
            p = pos.pop()
            if self.cube[self.cubePos(p['X'], p['Y'], p['Z'])] != Generator.EMPTY:
                continue
            self.fillHole(p)

    def fillHole(self, pos:dict):
        dirs = [
            { 'X':-1, 'Y':0, 'Z':0 },
            { 'X': 1, 'Y':0, 'Z':0 },
            { 'X':0, 'Y':-1, 'Z':0 },
            { 'X':0, 'Y': 1, 'Z':0 },
            { 'X':0, 'Y':0, 'Z':-1 },
            { 'X':0, 'Y':0, 'Z': 1 },
        ]
        random.shuffle(dirs)

        while len(dirs):
            d = dirs.pop()
            n = dict(pos)
            v = 0
            for k in n: 
                n[k] += d[k]
                v += d[k]

            if not self.isValidPosition(n):
                continue

            dst = self.cube[self.cubePos(n['X'], n['Y'], n['Z'])]
            if not dst in [Generator.EMPTY, Generator.PIPE]:
                continue

            self.cube[self.cubePos(pos['X'], pos['Y'], pos['Z'])] = Generator.PIPE

            if v > 0:
                pp = pos
            else:
                pp = n
            if d['X'] != 0 :
                if self.paths['X'][self.pathXPos(pp['X'], pp['Y'], pp['Z'])]: continue
                self.paths['X'][self.pathXPos(pp['X'], pp['Y'], pp['Z'])] = True
            elif d['Y'] != 0 : 
                if self.paths['Y'][self.pathYPos(pp['X'], pp['Y'], pp['Z'])]: continue
                self.paths['Y'][self.pathYPos(pp['X'], pp['Y'], pp['Z'])] = True
            elif d['Z'] != 0 : 
                if self.paths['Z'][self.pathZPos(pp['X'], pp['Y'], pp['Z'])]: continue
                self.paths['Z'][self.pathZPos(pp['X'], pp['Y'], pp['Z'])] = True

            return


def buildSketch(gen:Generator, sizeBall:float, sizeSpace:float):

    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    comp = design.activeComponent

    bf = comp.features.baseFeatures.add()
    bf.startEdit()
    baseSketch = comp.sketches.add(comp.xYConstructionPlane)

    x = gen.sizeX * (sizeBall + sizeSpace) + sizeSpace
    y = gen.sizeY * (sizeBall + sizeSpace) + sizeSpace
    z = gen.sizeZ * (sizeBall + sizeSpace) + sizeSpace

    ps = [ 
        adsk.core.Point3D.create(0,0,0),
        adsk.core.Point3D.create(x,0,0),
        adsk.core.Point3D.create(0,y,0),
        adsk.core.Point3D.create(0,0,z),
        adsk.core.Point3D.create(x,y,0),
        adsk.core.Point3D.create(x,0,z),
        adsk.core.Point3D.create(0,y,z),
        adsk.core.Point3D.create(x,y,z)
    ]

    baseSketch.sketchCurves.sketchLines.addByTwoPoints(ps[0], ps[1])
    baseSketch.sketchCurves.sketchLines.addByTwoPoints(ps[0], ps[2])
    baseSketch.sketchCurves.sketchLines.addByTwoPoints(ps[0], ps[3])
    baseSketch.sketchCurves.sketchLines.addByTwoPoints(ps[1], ps[4])
    baseSketch.sketchCurves.sketchLines.addByTwoPoints(ps[1], ps[5])
    baseSketch.sketchCurves.sketchLines.addByTwoPoints(ps[2], ps[4])
    baseSketch.sketchCurves.sketchLines.addByTwoPoints(ps[2], ps[6])
    baseSketch.sketchCurves.sketchLines.addByTwoPoints(ps[3], ps[5])
    baseSketch.sketchCurves.sketchLines.addByTwoPoints(ps[3], ps[6])
    baseSketch.sketchCurves.sketchLines.addByTwoPoints(ps[4], ps[7])
    baseSketch.sketchCurves.sketchLines.addByTwoPoints(ps[5], ps[7])
    baseSketch.sketchCurves.sketchLines.addByTwoPoints(ps[6], ps[7])

    progressDialog = ui.createProgressDialog()
    progressDialog.cancelButtonText = 'Cancel'
    progressDialog.isBackgroundTranslucent = False
    progressDialog.isCancelButtonShown = True
    progressDialog.show('InsideZeCube Generator', 'Display', 0, gen.sizeX * gen.sizeY * gen.sizeZ, 1)

    delta = sizeBall + sizeSpace
    offset = sizeSpace + sizeBall / 2

    for z in range(gen.sizeZ):
        pz = z * delta + offset
        for y in range(gen.sizeY):
            py = y * delta + offset
            for x in range(gen.sizeX):
                px = x * delta + offset
                if x < gen.sizeX-1 and gen.paths['X'][gen.pathXPos(x, y, z)]:
                    baseSketch.sketchCurves.sketchLines.addByTwoPoints(
                        adsk.core.Point3D.create(px, py, pz),
                        adsk.core.Point3D.create(px + delta, py, pz)
                    )
                if y < gen.sizeY-1 and gen.paths['Y'][gen.pathYPos(x, y, z)]:
                    baseSketch.sketchCurves.sketchLines.addByTwoPoints(
                        adsk.core.Point3D.create(px, py, pz),
                        adsk.core.Point3D.create(px, py + delta, pz)
                    )
                if z < gen.sizeZ-1 and gen.paths['Z'][gen.pathZPos(x, y, z)]:
                    baseSketch.sketchCurves.sketchLines.addByTwoPoints(
                        adsk.core.Point3D.create(px, py, pz),
                        adsk.core.Point3D.create(px, py, pz + delta)
                    )

                progressDialog.progressValue += 1
                if (progressDialog.wasCancelled): return

    progressDialog.hide()
    bf.finishEdit()

def buildPipe(gen:Generator, sizeBall:float, sizeSpace:float):

    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    comp = design.activeComponent

    bf = comp.features.baseFeatures.add()
    bf.startEdit()

    # # Build Cube
    baseSketch = comp.sketches.add(comp.xYConstructionPlane)
    x = gen.sizeX * (sizeBall + sizeSpace) + sizeSpace
    y = gen.sizeY * (sizeBall + sizeSpace) + sizeSpace
    z = gen.sizeZ * (sizeBall + sizeSpace) + sizeSpace
    baseSketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(0, 0, 0),
        adsk.core.Point3D.create(x, y, 0)
    )
    cube = comp.features.extrudeFeatures.addSimple(
        baseSketch.profiles.item(0),
        adsk.core.ValueInput.createByReal(z),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    ).bodies
    
    caps = buildPipeCaps(comp, sizeBall, sizeSpace)
    capsColl = adsk.core.ObjectCollection.create()
    for b in caps:
        capsColl.add(b)


    progressDialog = ui.createProgressDialog()
    progressDialog.cancelButtonText = 'Cancel'
    progressDialog.isBackgroundTranslucent = False
    progressDialog.isCancelButtonShown = True
    progressDialog.show('InsideZeCube Generator', 'Display', 0, gen.sizeX * gen.sizeY * gen.sizeZ, 1)

    delta = sizeBall + sizeSpace
    offset = sizeSpace + sizeBall / 2

    # # nodeComp.name = "nodeComp"
    for z in range(gen.sizeZ):
        pz = z * delta + offset
        for y in range(gen.sizeY):
            py = y * delta + offset
            for x in range(gen.sizeX):
                px = x * delta + offset

                if x < gen.sizeX-1 and gen.paths['X'][gen.pathXPos(x, y, z)]:
                    buildPipeCutAt(comp, cube, capsColl,
                        comp.xConstructionAxis.geometry.direction,
                        px, py, pz)

                if y < gen.sizeY-1 and gen.paths['Y'][gen.pathYPos(x, y, z)]:
                    buildPipeCutAt(comp, cube, capsColl,
                        comp.yConstructionAxis.geometry.direction,
                        px, py, pz)

                if z < gen.sizeZ-1 and gen.paths['Z'][gen.pathZPos(x, y, z)]:
                    buildPipeCutAt(comp, cube, capsColl,
                        comp.zConstructionAxis.geometry.direction,
                        px, py, pz)

                progressDialog.progressValue += 1
                if (progressDialog.wasCancelled): 
                    bf.finishEdit()
                    progressDialog.hide()          
                    return

    for b in caps:
        b.deleteMe()

    bf.finishEdit()

    progressDialog.hide()          

def buildPipeCaps(comp:adsk.fusion.Component, sizeBall:float, sizeSpace:float):
    # Build Capsule
    
    # # Create Sketch
    roundSketch = comp.sketches.add(comp.xYConstructionPlane)
    roundSketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0),
        sizeBall/2
    )
    axe = roundSketch.sketchCurves.sketchLines.addByTwoPoints(
        adsk.core.Point3D.create(0, +sizeBall/2, 0),
        adsk.core.Point3D.create(0, -sizeBall/2, 0)
    )

    # # Create Sphere 1
    revolveInput = comp.features.revolveFeatures.createInput(
        roundSketch.profiles.item(0),
        axe,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    angle = adsk.core.ValueInput.createByReal(math.pi*2)
    revolveInput.setAngleExtent(False, angle)
    sphere1 = comp.features.revolveFeatures.add(revolveInput).bodies
    
    # # Create Sphere 2
    revolveInput = comp.features.revolveFeatures.createInput(
        roundSketch.profiles.item(0),
        axe,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    angle = adsk.core.ValueInput.createByReal(math.pi*2)
    revolveInput.setAngleExtent(False, angle)
    sphere2 = comp.features.revolveFeatures.add(revolveInput).bodies

    sphereColl = adsk.core.ObjectCollection.create()
    sphereColl.add(sphere2.item(0))
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(
        0, 
        0,
        sizeBall + sizeSpace
    )
    moveInput = comp.features.moveFeatures.createInput(
        sphereColl,
        transform
    )
    comp.features.moveFeatures.add(moveInput)

    # # # Create Caps
    roundProfil = adsk.core.ObjectCollection.create()
    roundProfil.add(roundSketch.profiles.item(0))
    roundProfil.add(roundSketch.profiles.item(1))
    extrudeInput = comp.features.extrudeFeatures.createInput(
        roundProfil,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        # adsk.fusion.FeatureOperations.JoinFeatureOperation
    )
    extrudeInput.setDistanceExtent(
        False,
        adsk.core.ValueInput.createByReal(sizeBall + sizeSpace)
    )
    # extrudeInput.participantBodies = [sphere1.item(0), sphere2.item(0)]
    pipe = comp.features.extrudeFeatures.add(extrudeInput).bodies

    return [sphere1[0], sphere2[0], pipe[0] ]
    # return None

def buildPipeCutAt(comp:adsk.fusion.Component, 
    cube: adsk.fusion.BRepBodies,
    capsColl:adsk.core.ObjectCollection, 
    direction:adsk.core.Vector3D, px:float, py:float, pz:float):
    transform = adsk.core.Matrix3D.create()
    transform.setToRotateTo(
        comp.zConstructionAxis.geometry.direction,
        direction,
        None
    )
    transform.translation = adsk.core.Vector3D.create(px, py, pz)
    moveInput = comp.features.moveFeatures.createInput(
        capsColl,
        transform
    )
    comp.features.moveFeatures.add(moveInput)
    
    combineInput = comp.features.combineFeatures.createInput(
        cube[0],
        capsColl
    )
    combineInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    combineInput.isKeepToolBodies = True
    comp.features.combineFeatures.add(combineInput)

    transform.invert()
    # transform.translation = adsk.core.Vector3D.create(2, 2, 0)
    moveInput = comp.features.moveFeatures.createInput(
        capsColl,
        transform
    )
    comp.features.moveFeatures.add(moveInput)

