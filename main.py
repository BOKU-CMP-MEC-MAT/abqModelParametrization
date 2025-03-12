from abq.AbaqusModelFactory import *
#from geo.GeometryPart import *
#from geo.GeometryModel import *
#from geo.GeometryAssembly import *
import numpy as np
import matplotlib.pyplot as plt

caeName = "PlateWithRebar"
factory = AbaqusModelFactory(caeName)

w = 1000
l = 1000
t = 100
holeDiameter = 250
rebarDiameter = 10
meshSizePlate = 25
meshSizeRebar = 25
spacingRebars = 100
pressure=10

cxRange = (-w/2 + holeDiameter/2 + Plate.MIN_DISTANCE_TO_EDGE,
           w/2 - holeDiameter/2 - Plate.MIN_DISTANCE_TO_EDGE)

cyRange = (-l/2 + holeDiameter/2 + Plate.MIN_DISTANCE_TO_EDGE,
           l/2 - holeDiameter/2 - Plate.MIN_DISTANCE_TO_EDGE)


for cx in np.arange(cxRange[0], cxRange[1]+1, 200):
    for cy in np.arange(cyRange[0], cyRange[1]+1, 200):
        modelName = f"model_{int(cx)}_{int(cy)}"
        print(modelName)
        plateSection = GeometrySection(sectionName="secPlate",
                                       material="concrete")
        rebarSection = RebarSection(sectionName="secRebar",
                                    material="steel",
                                    diameter=rebarDiameter)
        plate = Plate(partName="plate",
                      section=plateSection,
                      meshSize=meshSizePlate,
                      thickness=t,
                      width=w,
                      length=l,
                      centerHole=(cx, cy),
                      holeDiameter=holeDiameter)

        rebars = {"rebarX": Rebar(partName="rebarX",
                                  section=rebarSection,
                                  meshSize=meshSizeRebar,
                                  length=w-2*Constants.CONCRETE_COVER),
                  "rebarY": Rebar(partName="rebarY",
                                  section=rebarSection,
                                  meshSize=meshSizeRebar,
                                  length=l-2*Constants.CONCRETE_COVER),
                  "rebarXLeft": Rebar(partName="rebarXLeft",
                                      section=rebarSection,
                                      meshSize=meshSizeRebar,
                                      length= cx + w/2 - plate.holeRadius - 2*Constants.CONCRETE_COVER),
                  "rebarXRight": Rebar(partName="rebarXRight",
                                       section=rebarSection,
                                       meshSize=meshSizeRebar,
                                       length= w/2 - cx - plate.holeRadius - 2*Constants.CONCRETE_COVER),
                  "rebarYBottom": Rebar(partName="rebarYBottom",
                                        section=rebarSection,
                                        meshSize=meshSizeRebar,
                                        length= cy + l/2 - plate.holeRadius - 2*Constants.CONCRETE_COVER),
                  "rebarYTop": Rebar(partName="rebarYTop",
                                     section=rebarSection,
                                     meshSize=meshSizeRebar,
                                     length= l/2 - cy - plate.holeRadius - 2*Constants.CONCRETE_COVER)}

        assembly = GeometryAssembly(plate=plate,
                                    rebars=rebars,
                                    spacing=spacingRebars)

        model = GeometryModel(modelName=modelName,
                              plate=plate,
                              rebars=rebars,
                              assembly=assembly)

        factory.createAbaqusModel(model=model)
        factory.createLoadStep(model=model,
                               stepName="Load",
                               pressureMagnitude=pressure,
                               timePeriod=1,
                               initialInc=1e-1,
                               minInc=1e-5,
                               maxInc=1)
        factory.setOutput(model=model,
                          stepName="Load",
                          outputName="output",
                          frequency=1,
                          variables=('S', 'MISES', 'E', 'PE','PEEQ', 'PEMAG', 'LE', 'U','RF'))

        factory.writeInput(model=model)

#factory.saveMdb()

        #figure, axes = plt.subplots()
        #for i in model.assembly.instances:
        #    axes.plot(i.position[0],i.position[1], "rx")
        #    if "X" in i.part.name:
        #        axes.plot([i.position[0]-i.part.length/2, i.position[0]+i.part.length/2],[i.position[1],i.position[1]],"k--")
        #    elif "Y" in i.part.name:
        #        axes.plot([i.position[0],i.position[0]],[i.position[1]-i.part.length/2, i.position[1]+i.part.length/2],"k--")
        #axes.add_artist(plt.Circle((cx,cy), plate.holeDiameter/2))
        #axes.set_aspect(1)
        #plt.show()
