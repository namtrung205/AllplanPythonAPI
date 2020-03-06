"""
Script for GeometrySelectInteractor
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

print('Load GeometrySelectInteractor.py')


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
    return SelectElement(coord_input, pyp_path, str_table_service)


class SelectElement():
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
        self.model_ele_list    = None
        self.build_ele_service = BuildingElementService()

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
            AllplanBaseElements.CreateElements()

        elif geo_ele.__class__.__name__ == "Arc3D" :
            AllplanUtil.ShowMessageBox("Centerline: Arc3D" + str(geo_ele), 1)

        if not geo_ele:
            return True

        return True

    def create_geo(self, centerline, type):
        path = None
        if type == "Line3D":
            path = centerline

            point1 = path.GetStartPoint()
            #-----------------Create center line
            line = AllplanGeo.Line3D(point1, AllplanGeo.Point3D(0, 0, self.length))

            #------------------ Create the pipe solid body
            axisPlace = AllplanGeo.AxisPlacement3D(point1,AllplanGeo.Vector3D(1,0,0),AllplanGeo.Vector3D(0,0,1))
            pipeOut = AllplanGeo.BRep3D.CreateCylinder(axisPlace, self.diameter, self.length, True, True)


            brepListToUnion =  AllplanGeo.BRep3DList()
            if self.includePad:
                pipePadBot = AllplanGeo.BRep3D.CreateCylinder(axisPlace, self.padDiameter, self.padThickness, True, True);
                if pipePadBot.IsValid():
                    brepListToUnion.append(pipePadBot)

                axisPlaceRe = AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, self.length), AllplanGeo.Vector3D(1,0,0),AllplanGeo.Vector3D(0,0,-1))
                pipePadTop = AllplanGeo.BRep3D.CreateCylinder(axisPlaceRe, self.padDiameter, self.padThickness, True, True);
                if pipePadTop.IsValid():
                    brepListToUnion.append(pipePadTop)

            #----union
            pipeSolid = pipeOut
            if self.includePad:
                err, pipeSolid = AllplanGeo.MakeUnion(pipeOut, brepListToUnion)
            else:
                pipeSolid = pipeOut

            inDiameter = self.diameter-2*self.thickness
            pipeVoid = AllplanGeo.BRep3D.CreateCylinder(axisPlace, inDiameter, self.length, True, True)


            pipe = None
            if pipeSolid.IsValid() and pipeVoid.IsValid():
                err, pipe = AllplanGeo.MakeSubtraction(pipeSolid, pipeVoid)

            self.pipe = pipe
            return self.pipe

    # Tranform
    def translate(self, element, trans_vector):
        """
        Translate element by translation vector
        """
        matrix = AllplanGeo.Matrix3D()
        matrix.Translate(trans_vector)
        return AllplanGeo.Transform(element, matrix)


    def create_extrude_box_steel(self, centerline, height, OD, thickness, radFillet): # Swept bởi Vector

        # Path to extrude
        path = centerline
        start_pnt = AllplanGeo.Point3D(0,0,0)
        path += start_pnt
        path += start_pnt + AllplanGeo.Point3D(0, 0, height)

        # Create Profile 1
        polyline_out = AllplanGeo.Polyline3D()
        polyline_out += AllplanGeo.Point3D(-OD/2, -OD/2, 0)
        polyline_out += polyline_out.GetLastPoint() + AllplanGeo.Vector3D(OD, 0, 0)
        polyline_out += polyline_out.GetLastPoint() + AllplanGeo.Vector3D(0, OD, 0)
        polyline_out += polyline_out.GetLastPoint() + AllplanGeo.Vector3D(-OD, 0, 0)
        polyline_out += polyline_out.GetStartPoint()

        profile_out = self.translate(polyline_out, AllplanGeo.Vector3D(0,0,0))

        #self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.com_prop, profile_out))

        poly_list_out = AllplanGeo.Polyline3DList()
        poly_list_out.append(profile_out)

        err_out, solid_out = AllplanGeo.CreateSweptPolyhedron3D(poly_list_out, path, True, True, AllplanGeo.Vector3D())

        # Create Profile 2
        ID = OD-thickness*2
        polyline_in = AllplanGeo.Polyline3D()
        polyline_in += AllplanGeo.Point3D(-ID/2, -ID/2, 0)
        polyline_in += polyline_in.GetLastPoint() + AllplanGeo.Vector3D(ID, 0, 0)
        polyline_in += polyline_in.GetLastPoint() + AllplanGeo.Vector3D(0, ID, 0)
        polyline_in += polyline_in.GetLastPoint() + AllplanGeo.Vector3D(-ID, 0, 0)
        polyline_in += polyline_in.GetStartPoint()

        profile_in = self.translate(polyline_in, AllplanGeo.Vector3D(0,0,0))

        self.model_ele_list.append(AllplanBasisElements.ModelElement3D(self.com_prop, profile_in))

        poly_list_in = AllplanGeo.Polyline3DList()
        poly_list_in.append(profile_in)

        err_in, solid_in = AllplanGeo.CreateSweptPolyhedron3D(poly_list_in, path, True, True, AllplanGeo.Vector3D())

        # Subtract Object
        err, solid_box_steel = AllplanGeo.MakeSubtraction(solid_out, solid_in)

        #Edge fillet
        edges = AllplanUtil.VecSizeTList()
        numberEdge = int(solid_box_steel.GetEdgesCount())
        for i in range(0, numberEdge):
            edges.append(i)

        # Fillet
        err_Fillet, solid_box_steel_fillet = AllplanGeo.FilletCalculus3D.Calculate(solid_box_steel, edges, radFillet, True)
        self.create_elements(err_Fillet, solid_box_steel_fillet)

class Selectpoint():
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