import adsk.core # pylint: disable=import-error
import adsk.fusion # pylint: disable=import-error
import adsk.cam # pylint: disable=import-error
import math
import traceback
from . import Builder
from . import Generator

class BuilderPipe(Builder):

    def build(self, gen:Generator, sizeBall:float, sizeSpace:float):
        app = adsk.core.Application.get()
        ui  = app.userInterface

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
        
        caps = self._caps(comp, sizeBall, sizeSpace)
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
                        self._cutAt(comp, cube, capsColl,
                            comp.xConstructionAxis.geometry.direction,
                            px, py, pz)

                    if y < gen.sizeY-1 and gen.paths['Y'][gen.pathYPos(x, y, z)]:
                        self._cutAt(comp, cube, capsColl,
                            comp.yConstructionAxis.geometry.direction,
                            px, py, pz)

                    if z < gen.sizeZ-1 and gen.paths['Z'][gen.pathZPos(x, y, z)]:
                        self._cutAt(comp, cube, capsColl,
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

    def _caps(self, comp:adsk.fusion.Component, sizeBall:float, sizeSpace:float):
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

    def _cutAt(self, comp:adsk.fusion.Component, 
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

