"""
Script for CreatePipeFromCenterLine
"""

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_Utility as AllplanUtil
import NemAll_Python_IFW_ElementAdapter as AllplanIFWElem

from BuildingElementPaletteService import BuildingElementPaletteService
from BuildingElementService import BuildingElementService
from TraceService import TraceService
from PythonPart import *
import math

print('Load CreatePipeFromCenterLine.py')

def check_allplan_version(build_ele, version):
    """
    Check the current Allplan version

    Args:
        build_ele: the building element.
        version:   the current Allplan version

    Returns:
        True/False if version is supported by this script
    """

    # Delete unused arguments
    del build_ele
    del version

    # Support all versions
    return True


def create_element(build_ele, doc):
    """
    Creation of element (only necessary for the library preview)

    Args:
        build_ele: the building element.
        doc:       input document
    """

    del build_ele
    del doc

    com_prop = AllplanBaseElements.CommonProperties()
    com_prop.GetGlobalProperties()

    line1 = AllplanGeo.Line2D(AllplanGeo.Point2D(),AllplanGeo.Point2D(1000,1000))
    line2 = AllplanGeo.Line2D(AllplanGeo.Point2D(1000,500),AllplanGeo.Point2D(2000,200))

    model_ele_list = [AllplanBasisElements.ModelElement2D(com_prop, line1),
                      AllplanBasisElements.ModelElement2D(com_prop, line2)]

    return (model_ele_list, None, None)


def create_interactor(coord_input, pyp_path, str_table_service):
    """
    Create the interactor

    Args:
        coord_input:        coordinate input
        pyp_path:           path of the pyp file
        str_table_service:  string table service
    """
    return CreatePipeFromCenterLine(coord_input, pyp_path, str_table_service)


class CreatePipeFromCenterLine():
    """
    Definition of class GeometrySelectInteractor
    """

    def __init__(self, coord_input, pyp_path, str_table_service):
        """
        Initialization of class GeometrySelectInteractor

        Args:
            coord_input:        coordinate input
            pyp_path:           path of the pyp file
            str_table_service:  string table service
        """
        # Default Parameters
        self.coord_input       = coord_input
        self.pyp_path          = pyp_path
        self.str_table_service = str_table_service
        self.first_point_input = True
        self.first_point       = AllplanGeo.Point3D()
        self.model_ele_list    = []
        self.build_ele_service = BuildingElementService()

        #Dimension
        self.diameter = 50
        self.thickness = 3

        self.includePad = True
        self.padDiameter = 70
        self.padThickness = 5

        #Global Parameters
        self.com_prop = AllplanBaseElements.CommonProperties()
        self.com_prop.GetGlobalProperties()

        #interactor UI
        self.coord_input.InitFirstElementInput(AllplanIFW.InputStringConvert("Select Line: "))


    def on_preview_draw(self):
        """
        Handles the preview draw event
        """


    def on_mouse_leave(self):
        """
        Handles the mouse leave event
        """


    def on_cancel_function(self):
        """
        Check for input function cancel in case of ESC

        Returns:
            True/False for success.
        """
        return True


    def modify_element_property(self, page, name, value):
        """
        Modify property of element

        Args:
            page:   the page of the property
            name:   the name of the property.
            value:  new value for property.
        """


    def process_mouse_msg(self, mouse_msg, pnt, msg_info):
        """
        Process the mouse message event

        Args:
            mouse_msg:  the mouse message.
            pnt:        the input point in view coordinates
            msg_info:   additional message info.

        Returns:
            True/False for success.
        """

        self.coord_input.SelectElement(mouse_msg, pnt, msg_info, True, True, True)

        if self.coord_input.IsMouseMove(mouse_msg):
            return True

        geo_ele = self.coord_input.GetSelectedGeometryElement()

        if geo_ele.__class__.__name__ == "Line3D":
            AllplanUtil.ShowMessageBox("Centerline: Line3D", 1)
            self.create_geo(geo_ele, "Line3D")
            AllplanBaseElements.CreateElements(self.coord_input.GetInputViewDocument(),
                                           AllplanGeo.Matrix3D(),
                                           self.model_ele_list, [], None)

        elif geo_ele.__class__.__name__ == "Arc3D" :
            AllplanUtil.ShowMessageBox("Centerline: Arc3D" + str(geo_ele), 1)
            self.create_geo(geo_ele, "Arc3D")
            AllplanBaseElements.CreateElements(self.coord_input.GetInputViewDocument(),
                                           AllplanGeo.Matrix3D(),
                                           self.model_ele_list, [], None)
        if not geo_ele:
            return True

        return True


    def create_geo(self, centerline, type):
        if type == "Line3D":
            path = centerline
            originPoint = path.GetStartPoint()
            lastPoint = path.GetEndPoint()

            lengPath = originPoint.GetDistance(lastPoint)

            pathVector = path.GetVector()
            perPathVector = AllplanGeo.Vector3D(-(pathVector.Y) - pathVector.Z, pathVector.X, pathVector.X)

            #------------------ Create the pipe solid body
            axisPlace = AllplanGeo.AxisPlacement3D(originPoint, perPathVector, pathVector)
            pipeOut = AllplanGeo.BRep3D.CreateCylinder(axisPlace, self.diameter, lengPath, True, True)

            brepListToUnion =  AllplanGeo.BRep3DList()
            if self.includePad:
                pipePadBot = AllplanGeo.BRep3D.CreateCylinder(axisPlace, self.padDiameter, self.padThickness, True, True);
                if pipePadBot.IsValid():
                    brepListToUnion.append(pipePadBot)

                axisPlaceRe = AllplanGeo.AxisPlacement3D(lastPoint, perPathVector, pathVector)
                pipePadTop = AllplanGeo.BRep3D.CreateCylinder(axisPlaceRe, self.padDiameter, self.padThickness, True, True);
                if pipePadTop.IsValid():
                    brepListToUnion.append(pipePadTop)
            #----union
            pipeSolid = pipeOut
            if self.includePad:
                err, pipeSolid = AllplanGeo.MakeUnion(pipeOut, brepListToUnion)
            #else:
            #    pipeSolid = pipeOut

            #inDiameter = self.diameter-2*self.thickness
            #pipeVoid = AllplanGeo.BRep3D.CreateCylinder(axisPlace, inDiameter, self.length, True, True)


            #pipe = None
            #if pipeSolid.IsValid() and pipeVoid.IsValid():
            #    err, pipe = AllplanGeo.MakeSubtraction(pipeSolid, pipeVoid)

            #self.pipe = pipe

            self.model_ele_list.clear()
            self.model_ele_list = [AllplanBasisElements.ModelElement3D(self.com_prop, pipeSolid)]

        elif type == "Arc3D":
            pathArc = centerline
            #------------------ Create the pipe solid body
            centerPointPath = pathArc.GetCenter()

            firstPointArc = pathArc.GetStartPoint()
            ytempAxis = AllplanGeo.Vector3D(firstPointArc.X-centerPointPath.X,firstPointArc.Y-centerPointPath.Y,firstPointArc.Z-centerPointPath.Z)
            zAxis = AllplanGeo.Vector3D(pathArc.GetZAxis())
            ytempAxis.CrossProduct(zAxis)

            angle = pathArc.GetDeltaAngle()

            profiles = []
            profile = AllplanGeo.Arc3D(firstPointArc, zAxis, ytempAxis, 50, 50, 0, math.pi*2)

            profiles.append(profile)

            axisRev = AllplanGeo.Axis3D(centerPointPath, zAxis)
            err, unionRevBrep_solid = AllplanGeo.CreateRevolvedBRep3D(profiles, axisRev, angle, True, 1)

            self.model_ele_list.clear()
            self.model_ele_list = [AllplanBasisElements.ModelElement3D(self.com_prop, unionRevBrep_solid)]

    # Tranform
    def translate(self, element, trans_vector):
        """
        Translate element by translation vector
        """
        matrix = AllplanGeo.Matrix3D()
        matrix.Translate(trans_vector)
        return AllplanGeo.Transform(element, matrix)


class CreatePipeFromPickPoint():
    """
    Definition of class GeometrySelectInteractor
    """

    def __init__(self, coord_input, pyp_path, str_table_service):
        """
        Initialization of class GeometrySelectInteractor

        Args:
            coord_input:        coordinate input
            pyp_path:           path of the pyp file
            str_table_service:  string table service
        """
        self.coord_input       = coord_input
        self.pyp_path          = pyp_path
        self.str_table_service = str_table_service
        self.first_point_input = True
        self.first_point       = AllplanGeo.Point3D()
        self.model_ele_list    = []
        self.build_ele_service = BuildingElementService()
        self.list_point_input = []

        #Dimension
        self.diameter = 50
        self.thickness = 3

        self.includePad = True
        self.padDiameter = 70
        self.padThickness = 5

        #Global Parameters
        self.com_prop = AllplanBaseElements.CommonProperties()
        self.com_prop.GetGlobalProperties()


        #Pick First Point
        self.coord_input.InitFirstPointInput(AllplanIFW.InputStringConvert("Select Point"))
        self.first_point = coord_input.GetCurrentPoint().GetPoint()


    def on_preview_draw(self):
        """
        Handles the preview draw event
        """
        if len(self.list_point_input)>1:
            self.draw_preview()


    def on_mouse_leave(self):
        """
        Handles the mouse leave event
        """


    def on_cancel_function(self):
        """
        Check for input function cancel in case of ESC

        Returns:
            True/False for success.
        """
        AllplanBaseElements.CreateElements(self.coord_input.GetInputViewDocument(),
                                           AllplanGeo.Matrix3D(),
                                           self.model_ele_list, [], None)
        return True


    def modify_element_property(self, page, name, value):
        """
        Modify property of element

        Args:
            page:   the page of the property
            name:   the name of the property.
            value:  new value for property.
        """


    def process_mouse_msg(self, mouse_msg, pnt, msg_info):
        """
        Process the mouse message event

        Args:
            mouse_msg:  the mouse message.
            pnt:        the input point in view coordinates
            msg_info:   additional message info.

        Returns:
            True/False for success.
        """
        coorInput_rs = self.coord_input.GetInputPoint(mouse_msg, pnt, msg_info, True )
        if self.coord_input.IsMouseMove(mouse_msg):
            return True

        self.list_point_input.append(coorInput_rs.GetPoint())
        if(len(self.list_point_input)>1):
            line = AllplanGeo.Line3D(AllplanGeo.Point3D(self.list_point_input[-1]),AllplanGeo.Point3D(self.list_point_input[-2]))
            self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.com_prop, line))


        AllplanUtil.ShowMessageBox(str(self.list_point_input), 1)
        self.coord_input.InitNextPointInput(AllplanIFW.InputStringConvert("Select Next Point"))
        return True


    def draw_preview(self):
        """
        Draw the preview

        Args:
            input_pnt:  Input point
        """

        if(len(self.list_point_input)>1):
            line = AllplanGeo.Line3D(AllplanGeo.Point3D(self.list_point_input[-1]),AllplanGeo.Point3D(self.list_point_input[-2]))
            self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.com_prop, line))
            AllplanBaseElements.DrawElementPreview(self.coord_input.GetInputViewDocument(),
                                                   AllplanGeo.Matrix3D(),
                                                   self.model_ele_list, False, None)