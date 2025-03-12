#import sys
#sys.path.append("glob")
from geo.GeometryInstance import *
#from geom.GeometryPart import *
from geo.Constants import *

class GeometryAssembly:
    def __init__(self,
                 plate: GeometryPart,
                 rebars: dict[Rebar],
                 spacing: float):
        self.instances = []
        self.zPositionRebarsX = plate.thickness - Constants.CONCRETE_COVER - rebars["rebarX"].section.diameter/2
        self.zPositionRebarsY = self.zPositionRebarsX - rebars["rebarX"].section.diameter
        self.__createInstances(plate, rebars, spacing)

    def __createInstances(self, plate: GeometryPart, rebars: list[Rebar], spacing: float):
        rX_bottom = -plate.length/2 + Constants.CONCRETE_COVER
        rX_top = -rX_bottom
        rY_left = -plate.width/2 + Constants.CONCRETE_COVER
        rY_right = -rY_left

        rX_holeBottom = plate.centerHole[1] - plate.holeDiameter/2 - Constants.CONCRETE_COVER
        rX_holeTop =  plate.centerHole[1] + plate.holeDiameter/2 + Constants.CONCRETE_COVER
        rY_holeLeft = plate.centerHole[0] - plate.holeDiameter/2 - Constants.CONCRETE_COVER
        rY_holeRight = plate.centerHole[0] + plate.holeDiameter/2 + Constants.CONCRETE_COVER
        rXLeft_X = (rY_left + rY_holeLeft)/2
        rXRight_X = (rY_right + rY_holeRight)/2
        rYTop_Y = (rX_top + rX_holeTop)/2
        rYBottom_Y = (rX_bottom + rX_holeBottom)/2

        self.instances.append(GeometryInstance(instanceName="i_plate",
                                               part=plate,
                                               positionCenter=(0, 0, 0)))
        self.instances.append(GeometryInstance(instanceName="i_rebarX_Bottom",
                                               part=rebars["rebarX"],
                                               positionCenter=(0, rX_bottom, self.zPositionRebarsX)))
        self.instances.append(GeometryInstance(instanceName="i_rebarX_Top",
                                               part=rebars["rebarX"],
                                               positionCenter=(0, rX_top, self.zPositionRebarsX)))
        self.instances.append(GeometryInstance(instanceName="i_rebarY_Left",
                                               part=rebars["rebarY"],
                                               positionCenter=(rY_left, 0, self.zPositionRebarsY)))
        self.instances.append(GeometryInstance(instanceName="i_rebarY_Right",
                                               part=rebars["rebarY"],
                                               positionCenter=(rY_right, 0, self.zPositionRebarsY)))
        self.instances.append(GeometryInstance(instanceName="i_rebarX_HoleBottom",
                                               part=rebars["rebarX"],
                                               positionCenter=(0, rX_holeBottom, self.zPositionRebarsX)))
        self.instances.append(GeometryInstance(instanceName="i_rebarX_HoleTop",
                                               part=rebars["rebarX"],
                                               positionCenter=(0, rX_holeTop, self.zPositionRebarsX)))
        self.instances.append(GeometryInstance(instanceName="i_rebarY_HoleLeft",
                                               part=rebars["rebarY"],
                                               positionCenter=(rY_holeLeft, 0, self.zPositionRebarsY)))
        self.instances.append(GeometryInstance(instanceName="i_rebarY_HoleRight",
                                               part=rebars["rebarY"],
                                               positionCenter=(rY_holeRight, 0, self.zPositionRebarsY)))
        # rebarsX inbetween
        dx_top = np.abs(rX_top - rX_holeTop)
        nX_top = int(round(dx_top/spacing,0))
        try:
            s_xTop = dx_top / nX_top  # Attempt division
        except ZeroDivisionError:
            print("Error: Division by zero in s_xTop calculation.")
        except Exception as e:
            print(f"Error: {e}")  # Catch any other exceptions
        else:
            # The for-loop only executes if no exception was raised
            for i in range(1, nX_top):
                self.instances.append(GeometryInstance(instanceName=f"i_rebarX_Top_{i}",
                                                       part=rebars["rebarX"],
                                                       positionCenter=(0, rX_top - i * s_xTop, self.zPositionRebarsX)))
        dx_bottom = np.abs(rX_bottom - rX_holeBottom)
        nX_bottom = int(round(dx_bottom/spacing,0))
        try:
            s_xBottom = dx_bottom/nX_bottom
        except ZeroDivisionError:
            print("Error: Division by zero in s_xBottom calculation.")
        except Exception as e:
            print(f"Error: {e}")  # Catch any other exceptions
        else:
            for i in range(1,nX_bottom):
                self.instances.append(GeometryInstance(instanceName=f"i_rebarX_Bottom_{i}",
                                                   part=rebars["rebarX"],
                                                   positionCenter=(0, rX_holeBottom - i*s_xBottom, self.zPositionRebarsX)))
        dx_middle = np.abs(rX_holeTop - rX_holeBottom)
        nX_middle = int(round(dx_middle/spacing,0))
        try:
            s_xMiddle = dx_middle/nX_middle
        except ZeroDivisionError:
            print("Error: Division by zero in s_xMiddle calculation.")
        except Exception as e:
            print(f"Error: {e}")  # Catch any other exceptions
        else:
            for i in range(1,nX_middle):
                self.instances.append(GeometryInstance(instanceName=f"i_rebarXLeft_Middle_{i}",
                                                   part=rebars["rebarXLeft"],
                                                   positionCenter=(rXLeft_X, rX_holeTop - i*s_xMiddle, self.zPositionRebarsX)))
                self.instances.append(GeometryInstance(instanceName=f"i_rebarXRight_Middle_{i}",
                                                   part=rebars["rebarXRight"],
                                                   positionCenter=(rXRight_X, rX_holeTop - i*s_xMiddle, self.zPositionRebarsX)))
         
        # rebarsY inbetween
        dy_left = np.abs(rY_left - rY_holeLeft)
        nY_left = int(round(dy_left/spacing,0))
        try:
            s_yLeft = dy_left/nY_left
        except ZeroDivisionError:
            print("Error: Division by zero in s_yLeft calculation.")
        except Exception as e:
            print(f"Error: {e}")  # Catch any other exceptions
        else:
            for i in range(1,nY_left):
                self.instances.append(GeometryInstance(instanceName=f"i_rebarY_Left_{i}",
                                                   part=rebars["rebarY"],
                                                   positionCenter=(rY_left + i*s_yLeft, 0, self.zPositionRebarsY)))
        dy_right = np.abs(rY_right - rY_holeRight)
        nY_right = int(round(dy_right/spacing,0))
        try:
            s_yRight = dy_right/nY_right
        except ZeroDivisionError:
            print("Error: Division by zero in s_yRight calculation.")
        except Exception as e:
            print(f"Error: {e}")  # Catch any other exceptions
        else:
            for i in range(1,nY_right):
                self.instances.append(GeometryInstance(instanceName=f"i_rebarY_Right_{i}",
                                                   part=rebars["rebarY"],
                                                   positionCenter=(rY_holeRight + i*s_yRight, 0, self.zPositionRebarsY)))

        dy_middle = np.abs(rY_holeLeft - rY_holeRight)
        nY_middle = int(round(dy_middle/spacing,0))
        try:
            s_yMiddle = dy_middle/nY_middle
        except ZeroDivisionError:
            print("Error: Division by zero in s_yMiddle calculation.")
        except Exception as e:
            print(f"Error: {e}")  # Catch any other exceptions
        else:
            for i in range(1,nY_middle):
                self.instances.append(GeometryInstance(instanceName=f"i_rebarYTop_Middle_{i}",
                                                   part=rebars["rebarYTop"],
                                                   positionCenter=(rY_holeLeft + i*s_yMiddle, rYTop_Y, self.zPositionRebarsY)))
                self.instances.append(GeometryInstance(instanceName=f"i_rebarYBottom_Middle_{i}",
                                                   part=rebars["rebarYBottom"],
                                                   positionCenter=(rY_holeLeft + i*s_yMiddle, rYBottom_Y, self.zPositionRebarsY)))
