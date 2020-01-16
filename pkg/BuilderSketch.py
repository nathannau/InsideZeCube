import adsk.core # pylint: disable=import-error
import adsk.fusion # pylint: disable=import-error
import adsk.cam # pylint: disable=import-error
# import math
import traceback
from . import Builder
from . import Generator

class BuilderSketch(Builder):

    def build(self, gen:Generator, sizeBall:float, sizeSpace:float, extremity:str, peephole:str, peepholeSize:float):
        app = adsk.core.Application.get()
        ui  = app.userInterface

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

