from abaqus import *
from abaqusConstants import *
import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior

#import sys
#sys.path.append("geom")
#sys.path.append("glob")
from geo.GeometryModel import *
#from geom.geomPart import *
#from geom.geomAssembly import *
#from geom.geomInstance import *

class AbaqusModelFactory:
    def __init__(self,
                 dataBaseName: str):
        self.dataBaseName = dataBaseName
        self.mdb = Mdb(pathName= dataBaseName)



    def createAbaqusModel(self, model: GeometryModel):
        self.mdb.Model(name = model.name, modelType = STANDARD_EXPLICIT)
        self.__createPlate(model)
        self.__createRebars(model)
        self.__setNodeSets(model)
        self.__setSurfaces(model)
        self.__createSections(model)
        self.__assignSectionsToParts(model)
        self.__assignOrientationsToRebars(model)
        self.__createDatumPlanes(model)
        self.__partitionByDatumPlanes(model)
        self.__meshParts(model)
        self.__createInstances(model)
        self.__createEssentialBoundaries(model)
        self.__createEmbeddedRegions(model)

    def __createPlate(self, model: GeometryModel):
        s = self.mdb.models[model.name].ConstrainedSketch(name='plateSketch',
                                                     sheetSize=200.0)
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)
        s.rectangle(point1=(-model.plate.width/2, -model.plate.length/2), point2=(model.plate.width/2, model.plate.length/2))
        s.CircleByCenterPerimeter(center=model.plate.centerHole, point1=(model.plate.centerHole[0] + model.plate.holeRadius, model.plate.centerHole[1]))
        p = mdb.models[model.name].Part(name=model.plate.name,
                                        dimensionality=THREE_D, 
                                        type=DEFORMABLE_BODY)
        p.BaseSolidExtrude(sketch=s,
                           depth=model.plate.thickness)
        s.unsetPrimaryObject()

    def __createRebars(self, model: GeometryModel):
        for rebar in model.rebars.values():
            s = self.mdb.models[model.name].ConstrainedSketch(name=f"{rebar.name}Sketch", 
                                                              sheetSize=200.0)
            g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
            s.setPrimaryObject(option=STANDALONE)
            if "X" in rebar.name:
                s.Line(point1=(-rebar.length/2, 0.0), point2=(rebar.length/2, 0.0))
            elif "Y" in rebar.name:
                s.Line(point1=(0.0, -rebar.length/2), point2=(0.0, rebar.length/2))
            #s.HorizontalConstraint(entity=g[2], addUndoState=False)
            p = mdb.models[model.name].Part(name=rebar.name,
                                            dimensionality=THREE_D, 
                                            type=DEFORMABLE_BODY)
            p.BaseWire(sketch=s)
            s.unsetPrimaryObject()

    def __setNodeSets(self, model: GeometryModel):
        p = self.mdb.models[model.name].parts[model.plate.name]
        pickedCells = p.cells.getByBoundingSphere(center=(0,0,0), radius=1000000)
        p.Set(cells=pickedCells, name='all')

        pickedFaces = p.faces.getByBoundingBox(xMin = -model.plate.width/2 - 1,
                                               yMin = -model.plate.length/2 - 1,
                                               zMin = -1,
                                               xMax = -model.plate.width/2 + 1,
                                               yMax = model.plate.length/2 + 1,
                                               zMax = model.plate.thickness + 1)
        p.Set(faces=pickedFaces, name="b_Left")

        for rebar in model.rebars.values():
            p = self.mdb.models[model.name].parts[rebar.name]
            pickedEdges = p.edges.getByBoundingSphere(center=(0,0,0), radius=1000000)
            p.Set(edges=pickedEdges, name='all')

    def __setSurfaces(self, model: GeometryModel):
        p = self.mdb.models[model.name].parts[model.plate.name]
        side1Faces = p.faces.getByBoundingBox(xMin = -model.plate.width/2 -1,
                                              yMin = -model.plate.length/2 -1,
                                              zMin = model.plate.thickness -1,
                                              xMax = model.plate.width/2 +1,
                                              yMax = model.plate.length/2 +1,
                                              zMax = model.plate.thickness +1)
        p.Surface(side1Faces=side1Faces, name="s_Top")

    def __createSections(self, model: GeometryModel):
        self.mdb.models[model.name].HomogeneousSolidSection(name=model.plate.section.name,
                                                            material=model.plate.section.material,
                                                            thickness=None)
        self.mdb.models[model.name].CircularProfile(name='profileRebar',
                                                    r=model.rebars["rebarX"].section.diameter/2)
        self.mdb.models[model.name].BeamSection(name=model.rebars["rebarX"].section.name,
                                                integration=DURING_ANALYSIS,
                                                poissonRatio=0.0,
                                                profile='profileRebar',
                                                material=model.rebars["rebarX"].section.material,
                                                temperatureVar=LINEAR,
                                                beamSectionOffset=(0.0,0.0),
                                                consistentMassMatrix=False)

    def __assignSectionsToParts(self, model: GeometryModel):
        p = self.mdb.models[model.name].parts[model.plate.name]
        region = p.sets['all']
        p.SectionAssignment(region=region,
                            sectionName=model.plate.section.name)

        for rebar in model.rebars.values():
            p = self.mdb.models[model.name].parts[rebar.name]
            region = p.sets['all']
            p.SectionAssignment(region=region,
                                sectionName=rebar.section.name)

    def __assignOrientationsToRebars(self, model: GeometryModel):
        for rebar in model.rebars.values():
            p = self.mdb.models[model.name].parts[rebar.name]
            region = p.sets['all']
            p.assignBeamSectionOrientation(region=region,
                                           method=N1_COSINES,
                                           n1=(0.0,0.0,-1.0))

    def __createDatumPlanes(self, model: GeometryModel):
        p = self.mdb.models[model.name].parts[model.plate.name]
        p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=model.plate.centerHole[1])
        p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=model.plate.centerHole[0])

    def __partitionByDatumPlanes(self, model: GeometryModel):
        p = self.mdb.models[model.name].parts[model.plate.name]
        for datum in p.datums.values():
            pickedCells = p.cells.getByBoundingSphere(center=(0,0,0), radius=10000000)
            p.PartitionCellByDatumPlane(datumPlane=datum,
                                        cells=pickedCells)
    
    def __meshParts(self, model: GeometryModel):
        elemTypePlate = mesh.ElemType(elemCode=C3D20, elemLibrary=STANDARD)
        elemTypeRebars = mesh.ElemType(elemCode=B32, elemLibrary=STANDARD)

        p = self.mdb.models[model.name].parts[model.plate.name]
        p.seedPart(size=model.plate.meshSize, deviationFactor=0.1, minSizeFactor=0.1)
        pickedCells = p.cells.getByBoundingSphere(center=(0,0,0), radius=10000000)
        pickedRegions=(pickedCells, )
        p.setElementType(regions=pickedRegions, elemTypes=(elemTypePlate,))
        p.generateMesh()

        for rebar in model.rebars.values():
            p = self.mdb.models[model.name].parts[rebar.name]
            p.seedPart(size=rebar.meshSize, deviationFactor=0.1, minSizeFactor=0.1)
            pickedEdges = p.edges.getByBoundingSphere(center=(0,0,0), radius=10000000)
            pickedRegions=(pickedEdges, )
            p.setElementType(regions=pickedRegions, elemTypes=(elemTypeRebars,))
            p.generateMesh()

    def __createInstances(self, model: GeometryModel):
        a = self.mdb.models[model.name].rootAssembly

        for instance in model.assembly.instances:
            p = self.mdb.models[model.name].parts[instance.part.name]
            a.Instance(name=instance.name,
                       part=p,
                       dependent=ON)
            a.translate(instanceList=(instance.name, ), vector=instance.position)

    def __createEssentialBoundaries(self, model: GeometryModel):
        a = self.mdb.models[model.name].rootAssembly
        region = a.instances["i_plate"].sets["b_Left"]
        self.mdb.models[model.name].DisplacementBC(name='b_Left',
                                                   createStepName='Initial', 
                                                   region=region,
                                                   u1=SET,
                                                   u2=SET,
                                                   u3=SET,
                                                   ur1=UNSET,
                                                   ur2=UNSET,
                                                   ur3=UNSET, 
                                                   amplitude=UNSET,
                                                   distributionType=UNIFORM,
                                                   fieldName='', 
                                                   localCsys=None)

    def __createEmbeddedRegions(self, model: GeometryModel):
        a = self.mdb.models[model.name].rootAssembly
        for i,(key,instance) in enumerate(a.instances.items()):
            if "plate" in key:
                continue
            try:
                e += instance.edges
            except:
                e = instance.edges
        a.Set(edges=e, name='allRebars')

        embeddedRegion = a.sets['allRebars']
        hostRegion = a.instances['i_plate'].sets['all']
        self.mdb.models[model.name].EmbeddedRegion(name='EmbeddedRegion',
                                                   embeddedRegion=embeddedRegion,
                                                   hostRegion=hostRegion,
                                                   weightFactorTolerance=1e-06,
                                                   absoluteTolerance=0.0, 
                                                   fractionalTolerance=0.05,
                                                   toleranceMethod=BOTH)

    def __createJob(self, model: GeometryModel):
        self.mdb.Job(name=model.name, model=model.name, description='', type=ANALYSIS, atTime=None, 
        waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, numDomains=1, 
        activateLoadBalancing=False, numThreadsPerMpiProcess=1, 
        multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)

    def __addIncludeFile(self, model: GeometryModel):
        self.mdb.models[model.name].keywordBlock.synchVersions(storeNodesAndElements=False)
        self.mdb.models[model.name].keywordBlock.setValues(edited = 0)
        self.mdb.models[model.name].keywordBlock.synchVersions(storeNodesAndElements=False)
        self.mdb.models[model.name].keywordBlock.insert(0, f"*include, input=materials.inc")


        
    #====================================================================================

    def createLoadStep(self, model: GeometryModel,
                       stepName: str,
                       pressureMagnitude: float,
                       timePeriod: float,
                       initialInc: float,
                       minInc: float,
                       maxInc: float,
                       maxNumInc: int = 100,
                       nlgeom: str = "OFF"):
        match nlgeom:
            case "ON":
                nl = ON
            case _ :
                nl = OFF

        self.mdb.models[model.name].StaticStep(name=stepName,
                                               previous='Initial',
                                               timePeriod=timePeriod,
                                               initialInc=initialInc,
                                               minInc=minInc,
                                               maxInc=maxInc,
                                               maxNumInc=maxNumInc,
                                               nlgeom= nl)
        region = self.mdb.models[model.name].rootAssembly.instances['i_plate'].surfaces['s_Top']
        self.mdb.models[model.name].Pressure(name='Pressure',
                                             createStepName=stepName, 
                                             region=region,
                                             distributionType=UNIFORM,
                                             field='',
                                             magnitude=pressureMagnitude,
                                             amplitude=UNSET)

    def setOutput(self, model: GeometryModel, stepName: str, outputName: str, frequency: int, variables: tuple):
        self.mdb.models[model.name].FieldOutputRequest(name=outputName,
                                                       createStepName=stepName,
                                                       frequency=frequency,
                                                       variables=variables)

    def writeInput(self, model: GeometryModel):
        self.mdb.jobs[model.name].writeInput(consistencyChecking=OFF)

    def saveMdb(self):
        self.mdb.saveAs(pathName=self.dataBaseName)
