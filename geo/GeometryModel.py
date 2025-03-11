#import sys
#sys.path.append("../glob")
#from geom.GeometryPart import *
from geo.GeometryAssembly import *
#from geom.GeometryInstance import *

class GeometryModel:
    def __init__(self,
                 modelName: str,
                 plate: Plate,
                 rebars: dict[Rebar],
                 assembly: GeometryAssembly):
        self.name = modelName
        self.plate = plate
        self.rebars = rebars
        self.assembly = assembly
