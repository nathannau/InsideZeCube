import adsk.core # pylint: disable=import-error
import adsk.fusion # pylint: disable=import-error
import adsk.cam # pylint: disable=import-error
import math
import traceback
from .BuilderSolid import BuilderSolid
from .Generator import Generator

class BuilderPipe(BuilderSolid):

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

