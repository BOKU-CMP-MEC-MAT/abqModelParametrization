from geo.GeometrySection import *
import numpy as np

class GeometryPart:
    def __init__(self,
                 partName: str,
                 section: GeometrySection,
                 meshSize: float):
        self.name = partName
        self.section = section
        self.meshSize = meshSize

#==============================================================================

class Plate(GeometryPart):
    MIN_DISTANCE_TO_EDGE = 50 #mm

    def __init__(self,
                 partName: str,
                 section: GeometrySection,
                 meshSize: float,
                 thickness: float,
                 width: float,
                 length: float,
                 centerHole: tuple,
                 holeDiameter: float):
        super().__init__(partName, section, meshSize)
        self.thickness = thickness
        self.width = width
        self.length = length
        self.centerHole = centerHole
        self.holeDiameter = holeDiameter
        self.__checkHole()

    @property
    def holeRadius(self):
        return self.holeDiameter/2

    def __checkHole(self):
        xDistanceToEdge = self.width/2 - (np.abs(self.centerHole[0]) + self.holeRadius)
        yDistanceToEdge = self.length/2 - (np.abs(self.centerHole[1]) + self.holeRadius)

        if xDistanceToEdge < Plate.MIN_DISTANCE_TO_EDGE:
            raise ValueError(f"Hole center x-coordinate is out of range: {xDistanceToEdge} < {Plate.MIN_DISTANCE_TO_EDGE}")
        if yDistanceToEdge < Plate.MIN_DISTANCE_TO_EDGE:
            raise ValueError(f"Hole center y-coordinate is out of range: {yDistanceToEdge} < {Plate.MIN_DISTANCE_TO_EDGE}")

#==============================================================================

class Rebar(GeometryPart):
    def __init__(self,
                 partName: str,
                 section: RebarSection,
                 meshSize: float,
                 length: float):
        super().__init__(partName, section, meshSize)
        self.length = length

#==============================================================================

if __name__ == "__main__":
    s = GeometrySection("section1", "concrete")

    meshSize = 1   #mm 
    thickness = 20 #mm 
    width = 1000   #mm
    length = 2000  #mm
    centerHole = (430, 0) #mm
    holeDiameter = 100  #mm
    p = Plate(partName="plate1",
              section=s,
              meshSize=meshSize,
              thickness=thickness,
              width=width,
              length=length,
              centerHole=centerHole,
              holeDiameter=holeDiameter)
