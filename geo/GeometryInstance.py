from geo.GeometryPart import *

class GeometryInstance:
    def __init__(self,
                 instanceName: str,
                 part: GeometryPart,
                 positionCenter: tuple):
        self.name = instanceName
        self.part = part
        self.position = positionCenter
