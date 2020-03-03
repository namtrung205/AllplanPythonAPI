"""
Script for Table
"""
import hashlib

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import GeometryValidate as GeometryValidate

from HandleDirection import HandleDirection
from HandleProperties import HandleProperties
from PythonPart import View2D3D, PythonPart


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

def move_handle(build_ele, handle_prop, input_pnt, doc):
    """
    Modify the element geometry by handles

    Args:
        build_ele:  the building element.
        handle_prop handle properties
        input_pnt:  input point
        doc:        input document
    """

    build_ele.change_property(handle_prop, input_pnt)
    return create_element(build_ele, doc)

def create_element(build_ele, doc):
    """
    Creation of element

    Args:
        build_ele: the building element.
        doc:       input document
    """
    del doc # param not needed

    common_props = AllplanBaseElements.CommonProperties()
    common_props.GetGlobalProperties()

    box = Box(build_ele.Length.value, build_ele.Width.value, build_ele.Height.value,)
    if not box.is_valid():
        return ([], [])

    handle_list = box.create_handles()
    box_views = [View2D3D ([AllplanBasisElements.ModelElement3D(common_props, box.create())])]

    pythonpart = PythonPart ("Box",
                             parameter_list = build_ele.get_params_list(),
                             hash_value = build_ele.get_hash(),
                             python_file = build_ele.pyp_file_name,
                             views = box_views)

    model_elem_list = pythonpart.create()

    return (model_elem_list, handle_list)


class Box():
    """
    Definition of class Table
    """

    def __init__(self, length = 1000.0, width = 500.0, height = 100.0):
        """
        Initialisation of class Table
        """
        self.length = length
        self.width = width
        self.height = height
        self.table = None

    def get_params_list(self):
        """
        Append all parameters as parameter list

        Returns: param list
        """
        param_list = []
        param_list.append ("Length = %s\n" % self.length)
        param_list.append ("Width = %s\n" % self.width)
        param_list.append ("Height = %s\n" % self.height)
        return param_list

    def __repr__(self):
        return 'Table(length=%s, width=%s, height=%s, board_thickness=%s,' \
            % (self.length, self.width, self.height)

    def hash (self):
        """
        Calculate hash value for script

        Returns:
            Hash string
        """
        param_string = self.__repr__()
        hash_val = hashlib.sha224(param_string.encode('utf-8')).hexdigest()
        return hash_val

    def filename(self):
        """
        Python script filename

        Returns:
            Script filename
        """
        return "CreateBoxPythonPart.py"

    def is_valid(self):
        """
        Check for valid values
        """
        if self.length <= 0 or self.width <= 0 or self.height <= 0:
            return False
        return True

    def create(self):
        """
        Create a Table
        """
        if not self.is_valid():
            return []


        #------------------ Create the board
        point1 = AllplanGeo.Point3D(0, 0, 0)
        point2 = AllplanGeo.Point3D(self.length, self.width, self.height)
        box = AllplanGeo.Polyhedron3D.CreateCuboid(point1, point2)

        common_props = AllplanBaseElements.CommonProperties()
        common_props.GetGlobalProperties()

        self.box = box
        return self.box

    def create_handles(self):
        """
        Create handles

        Returns:
            List of HandleProperties
        """

        #------------------ Create the handle

        handle_list = [HandleProperties("Handle",
                                        AllplanGeo.Point3D(self.length, 0, 0),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("Length", HandleDirection.x_dir),],
                                         HandleDirection.x_dir),
                       HandleProperties("Handle",
                                        AllplanGeo.Point3D(0, self.width, 0),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("Width", HandleDirection.y_dir),],
                                         HandleDirection.y_dir),
                       HandleProperties("Handle",
                                        AllplanGeo.Point3D(0, 0, self.height),
                                        AllplanGeo.Point3D(0, 0, 0),
                                        [("Height", HandleDirection.z_dir)],
                                         HandleDirection.z_dir),
                      ]
        return handle_list


