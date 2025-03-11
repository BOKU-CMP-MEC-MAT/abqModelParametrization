class GeometrySection:
    def __init__(self,
                 sectionName: str,
                 material: str):
        self.name = sectionName
        self.material = material

#==============================================================================

class RebarSection(GeometrySection):
    def __init__(self,
                 sectionName: str,
                 material: str,
                 diameter: float):
        super().__init__(sectionName, material)
        self.diameter = diameter 
