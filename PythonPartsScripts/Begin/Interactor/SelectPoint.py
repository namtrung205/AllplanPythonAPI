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


def create_interactor2(coord_input, pyp_path, str_table_service):
    """
    Create the interactor

    Args:
        coord_input:        coordinate input
        pyp_path:           path of the pyp file
        str_table_service:  string table service
    """
    return GeometrySelectInteractor(coord_input, pyp_path, str_table_service)


class GeometrySelectInteractor():
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

        self.coord_input.InitFirstElementInput(AllplanIFW.InputStringConvert("Select element"))
        self.coord_input.SelectWallFace()

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
        base_ele = self.coord_input.GetSelectedElement()
        ele_guid = base_ele.GetModelElementUUID()

        querytype =  AllplanIFW.QueryTypeID(ele_guid)

        select_query = AllplanIFW.SelectionQuery(querytype)

        AllplanUtil.ShowMessageBox(str(select_query), 1)



        print("len attributes: " + str(len(a)))

        for a1 in a:
            print(a1)

        #AllplanUtil.ShowMessageBox(str(b), 1)

        if not geo_ele:
            return True

        return True


