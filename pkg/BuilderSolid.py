import adsk.core # pylint: disable=import-error
import adsk.fusion # pylint: disable=import-error
import adsk.cam # pylint: disable=import-error
import math
import traceback
from .Builder import Builder
from .Generator import Generator

class BuilderSolid(Builder):

    def build(self, gen:Generator, sizeBall:float, sizeSpace:float, extremity:str, peephole:str, peepholeSize:float, spliceLevel:bool):
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

        if extremity == "Open":
            for p in gen.extremities:
                t = gen.cube[gen.cubePos(p['X'], p['Y'], p['Z'])]
                if t == Generator.START:
                    self._cutAt(
                        comp, cube, capsColl,
                        comp.zConstructionAxis.geometry.direction,
                        p['X'] * delta + offset,
                        p['Y'] * delta + offset,
                        - delta + offset
                    )
                if t == Generator.STOP:
                    self._cutAt(
                        comp, cube, capsColl,
                        comp.zConstructionAxis.geometry.direction,
                        p['X'] * delta + offset,
                        p['Y'] * delta + offset,
                        (gen.sizeZ-1) * delta + offset
                    )

        if extremity == "Window":
            windowStartSketch = comp.sketches.add(comp.xYConstructionPlane)
            x1 = gen.extremities[0]['X'] * delta + offset - sizeBall / 4
            y1 = gen.extremities[0]['Y'] * delta + offset - sizeBall / 4
            x2 = gen.extremities[1]['X'] * delta + offset + sizeBall / 4
            y2 = gen.extremities[1]['Y'] * delta + offset + sizeBall / 4
            windowStartSketch.sketchCurves.sketchLines.addTwoPointRectangle(
                adsk.core.Point3D.create(x1, y1, 0),
                adsk.core.Point3D.create(x2, y2, 0)
            )
            comp.features.extrudeFeatures.addSimple(
                windowStartSketch.profiles.item(0),
                adsk.core.ValueInput.createByReal(sizeBall/2 + sizeSpace),
                adsk.fusion.FeatureOperations.CutFeatureOperation
            )

            windowStartSketch = comp.sketches.add(comp.xYConstructionPlane)
            x1 = gen.extremities[2]['X'] * delta + offset - sizeBall / 4
            y1 = gen.extremities[2]['Y'] * delta + offset - sizeBall / 4
            x2 = gen.extremities[3]['X'] * delta + offset + sizeBall / 4
            y2 = gen.extremities[3]['Y'] * delta + offset + sizeBall / 4
            windowStartSketch.sketchCurves.sketchLines.addTwoPointRectangle(
                adsk.core.Point3D.create(x1, y1, 0),
                adsk.core.Point3D.create(x2, y2, 0)
            )
            extrudeInput = comp.features.extrudeFeatures.createInput(
                windowStartSketch.profiles.item(0),
                adsk.fusion.FeatureOperations.CutFeatureOperation
            )

            extrudeInput.setOneSideExtent(
                adsk.fusion.DistanceExtentDefinition.create(
                    adsk.core.ValueInput.createByReal(sizeBall/2 + sizeSpace)
                ),
                adsk.fusion.ExtentDirections.PositiveExtentDirection
            )
            extrudeInput.startExtent = adsk.fusion.OffsetStartDefinition.create(
                adsk.core.ValueInput.createByReal((gen.sizeZ-1) * delta + offset),
            )

            comp.features.extrudeFeatures.add(extrudeInput)

        for b in caps:
            b.deleteMe()

        progressDialog.hide()

        if peephole != 'None':
            m = max(gen.sizeX, gen.sizeY, gen.sizeZ)
            progressDialog.show('InsideZeCube Generator', 'Judas', 0, m * m, 1)
            peepholeSketch = comp.sketches.add(comp.xYConstructionPlane)
            peepholeSketch.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(0, 0, 0),
                peepholeSize/2
            )
            peepholeBody = comp.features.extrudeFeatures.addSimple(
                peepholeSketch.profiles.item(0),
                adsk.core.ValueInput.createByReal(
                    (sizeBall+sizeSpace)*m+sizeSpace
                    if peephole == "Full" else
                    sizeBall/2+sizeSpace
                ),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation
            ).bodies
            peepholeColl = adsk.core.ObjectCollection.create()
            peepholeColl.add(peepholeBody.item(0))

            for j in range(m):
                for i in range(m):
                    p = [] if i >= gen.sizeX and j >= gen.sizeY else \
                        [0] if peephole == 'Full' else \
                        [0, (gen.sizeZ-1) * delta + offset] # 'External'
                    for k in p:
                        self._cutAt(
                            comp, cube, peepholeColl,
                            comp.zConstructionAxis.geometry.direction,
                            i * delta + offset,
                            j * delta + offset,
                            k
                        )

                    p = [] if i >= gen.sizeX and j >= gen.sizeZ else \
                        [0] if peephole == 'Full' else \
                        [0, (gen.sizeY-1) * delta + offset] # 'External'
                    for k in p:
                        self._cutAt(
                            comp, cube, peepholeColl,
                            comp.yConstructionAxis.geometry.direction,
                            i * delta + offset,
                            k,
                            j * delta + offset
                        )


                    p = [] if i >= gen.sizeY and j >= gen.sizeZ else \
                        [0] if peephole == 'Full' else \
                        [0, (gen.sizeX-1) * delta + offset] # 'External'
                    for k in p:
                        self._cutAt(
                            comp, cube, peepholeColl,
                            comp.xConstructionAxis.geometry.direction,
                            k,
                            i * delta + offset,
                            j * delta + offset
                        )

                    # pass
                    progressDialog.progressValue += 1
                    if (progressDialog.wasCancelled):
                        bf.finishEdit()
                        progressDialog.hide()
                        return

            peepholeBody.item(0).deleteMe()
            # peephole:str, peepholeSize:float)
            # 'None', 'Full', 'External'

            progressDialog.hide()

        if spliceLevel:
            cutters = self._splice(comp, gen, sizeBall, sizeSpace)
            # oc = adsk.core.ObjectCollection.create()
            # oc.add(cutters.sketchCurves.sketchLines[0])
            for oc in cutters.sketchCurves.sketchLines :
                cc = adsk.core.ObjectCollection.create()
                for c in cube:
                    cc.add(c)
                splitBodyInput = comp.features.splitBodyFeatures.createInput(cc, oc, True)
                # splitBodyInput = comp.features.splitBodyFeatures.createInput(cube[0], oc, True)
                comp.features.splitBodyFeatures.add(splitBodyInput)
            
        bf.finishEdit()
        # t = design.timeline
        # tc = t.count
        # progressDialog.hide()

    def _caps(self, comp:adsk.fusion.Component, sizeBall:float, sizeSpace:float):
        # Build Capsule
        pass

    def _splice(self, comp:adsk.fusion.Component, gen:Generator, sizeBall:float, sizeSpace:float):
        # Build Capsule
        spliceSketch = comp.sketches.add(comp.yZConstructionPlane)
        # return [ spliceSketch.sketchCurves.sketchLines.addByTwoPoints(
        #         adsk.core.Point3D.create(-i * (sizeBall + sizeSpace), 0, 0),
        #         adsk.core.Point3D.create(-i * (sizeBall + sizeSpace), sizeBall, 0)
        # ) for i in range(1, gen.sizeZ + 1) ]
        for i in range(1, gen.sizeZ + 1) :
            spliceSketch.sketchCurves.sketchLines.addByTwoPoints(
                adsk.core.Point3D.create(-i * (sizeBall + sizeSpace), 0, 0),
                adsk.core.Point3D.create(-i * (sizeBall + sizeSpace), sizeBall, 0)
            )
        return spliceSketch

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

