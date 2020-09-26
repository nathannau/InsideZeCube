import adsk.core # pylint: disable=import-error
import adsk.fusion # pylint: disable=import-error
import adsk.cam # pylint: disable=import-error
import math
import traceback
from .BuilderSolid import BuilderSolid
from .Generator import Generator

class BuilderSquare(BuilderSolid):

    def _caps(self, comp:adsk.fusion.Component, sizeBall:float, sizeSpace:float):
        # Build Capsule

        # # Create Sketch
        squareSketch = comp.sketches.add(comp.yZConstructionPlane)
        squareSketch.sketchCurves.sketchLines.addCenterPointRectangle(
            adsk.core.Point3D.create(-sizeBall/2 - sizeSpace/2, 0, 0),
            adsk.core.Point3D.create(sizeBall/2, sizeBall/2, 0)
        )

        # # Create Cube
        extrudeInput = comp.features.extrudeFeatures.createInput(
            squareSketch.profiles.item(0),
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        extrudeInput.setDistanceExtent(
            True,
            adsk.core.ValueInput.createByReal(sizeBall/2)
        )
        cube1 = comp.features.extrudeFeatures.add(extrudeInput).bodies

        return [cube1[0]]


